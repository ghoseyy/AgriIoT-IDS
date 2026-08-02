"""Measure real, zero-hardware-purchase resource metrics for the paper's
"resource-constrained" claim:
  - sklearn model sizes (pickle bytes) for RF / DT / LR -- trivial, exact.
  - Torch AE/VAE: fp32 state_dict size vs. dynamically int8-quantized size,
    plus CPU inference latency for both, on this machine.

This does NOT require a Raspberry Pi or microcontroller. It gives you real,
citable numbers for "quantized model size" and "CPU inference latency,"
which you then contextualize in the paper against published Raspberry Pi
figures from the literature (Chehade et al. 2025, Jamshidi et al. 2025) --
e.g. "our quantized Autoencoder is Y KB, comparable in order of magnitude to
Jamshidi et al.'s reported RPi 4B footprint of 113.2 MB for a similar
autoencoder-based detector."

For a genuine ARM-hardware number (recommended next step, still free): sign
up for Oracle Cloud's Always-Free tier (Ampere A1, real ARM CPU), copy this
project there, run this same script, and report those latency numbers
instead of/alongside the ones measured here.

Usage:
    uv run python scripts/measure_resource_footprint.py
"""
from __future__ import annotations

import io
import json
import pickle
import time
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def measure_sklearn_models(prepared_dir: Path, random_state: int = 42) -> list[dict]:
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.linear_model import LogisticRegression
    from agri_iot_ids.data.cicids2017 import load_prepared_data

    prepared = load_prepared_data(prepared_dir)
    rng = np.random.default_rng(random_state)
    X_val, y_val = prepared.x_val, prepared.y_val
    X_attack = X_val[y_val == 1]
    y_attack = np.ones(len(X_attack), dtype=int)
    n_normal = min(len(prepared.x_train), len(X_attack) * 3)
    idx_normal = rng.choice(len(prepared.x_train), size=n_normal, replace=False)
    X_train = np.concatenate([prepared.x_train[idx_normal], X_attack], axis=0)
    y_train = np.concatenate([np.zeros(n_normal, dtype=int), y_attack], axis=0)

    models = [
        ("Random Forest", RandomForestClassifier(n_estimators=100, max_depth=20, n_jobs=-1, random_state=random_state)),
        ("Decision Tree", DecisionTreeClassifier(max_depth=20, random_state=random_state)),
        ("Logistic Regression", LogisticRegression(max_iter=1000, n_jobs=-1, random_state=random_state)),
    ]

    results = []
    n_bench = min(1000, len(prepared.x_test))
    X_bench = prepared.x_test[:n_bench]
    for name, model in models:
        model.fit(X_train, y_train)
        size_bytes = len(pickle.dumps(model))

        t0 = time.perf_counter()
        model.predict(X_bench)
        elapsed = time.perf_counter() - t0
        per_sample_ms = (elapsed / n_bench) * 1000

        results.append({
            "model": name,
            "size_kb": round(size_bytes / 1024, 2),
            "inference_latency_ms_per_sample": round(per_sample_ms, 5),
            "benchmarked_on_n_samples": n_bench,
        })
        print(f"{name}: {size_bytes / 1024:.2f} KB, {per_sample_ms:.5f} ms/sample")

    return results


def measure_torch_model(name: str, model, checkpoint_path: Path, input_dim: int) -> dict:
    import torch

    available_engines = torch.backends.quantized.supported_engines
    for engine in ("qnnpack", "fbgemm"):
        if engine in available_engines:
            torch.backends.quantized.engine = engine
            break
    else:
        raise SystemExit(f"No usable quantization engine found. Available: {available_engines}")

    model.load_state_dict(torch.load(checkpoint_path, map_location="cpu"))
    model.eval()

    fp32_buffer = io.BytesIO()
    torch.save(model.state_dict(), fp32_buffer)
    fp32_size_kb = len(fp32_buffer.getvalue()) / 1024

    quantized = torch.quantization.quantize_dynamic(model, {torch.nn.Linear}, dtype=torch.qint8)
    q_buffer = io.BytesIO()
    torch.save(quantized.state_dict(), q_buffer)
    q_size_kb = len(q_buffer.getvalue()) / 1024

    n_bench = 1000
    dummy = torch.randn(n_bench, input_dim)

    with torch.no_grad():
        t0 = time.perf_counter()
        model(dummy)
        fp32_latency_ms = ((time.perf_counter() - t0) / n_bench) * 1000

        t0 = time.perf_counter()
        quantized(dummy)
        q_latency_ms = ((time.perf_counter() - t0) / n_bench) * 1000

    result = {
        "model": name,
        "fp32_size_kb": round(fp32_size_kb, 2),
        "int8_dynamic_quantized_size_kb": round(q_size_kb, 2),
        "size_reduction_pct": round((1 - q_size_kb / fp32_size_kb) * 100, 1),
        "fp32_inference_latency_ms_per_sample": round(fp32_latency_ms, 5),
        "int8_inference_latency_ms_per_sample": round(q_latency_ms, 5),
        "benchmarked_on_n_samples": n_bench,
        "benchmark_device": "CPU (this machine -- NOT an embedded/ARM device; see script docstring)",
    }
    print(json.dumps(result, indent=2))
    return result


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepared-dir", type=Path, default=Path("experiments/preprocessing/cicids2017"))
    parser.add_argument("--ae-checkpoint", type=Path, default=Path("experiments/autoencoder/model.pt"))
    parser.add_argument("--ae-results", type=Path, default=Path("experiments/autoencoder/results.json"))
    parser.add_argument("--vae-checkpoint", type=Path, default=Path("experiments/vae/model.pt"))
    parser.add_argument("--vae-results", type=Path, default=Path("experiments/vae/results.json"))
    parser.add_argument("--output", type=Path, default=Path("experiments/resource_footprint/results.json"))
    args = parser.parse_args()

    try:
        import torch
        from agri_iot_ids.models.autoencoder import Autoencoder
        from agri_iot_ids.models.vae import VariationalAutoencoder
        from agri_iot_ids.data.cicids2017 import load_prepared_data
    except ModuleNotFoundError as exc:
        raise SystemExit(f"Missing dependency: {exc}. Run `uv sync` first.") from exc

    prepared = load_prepared_data(args.prepared_dir)
    input_dim = prepared.input_dim

    print("=" * 60)
    print("SKLEARN MODELS (Random Forest, Decision Tree, Logistic Regression)")
    print("=" * 60)
    sklearn_results = measure_sklearn_models(args.prepared_dir)

    print("\n" + "=" * 60)
    print("AUTOENCODER: fp32 vs int8 dynamic quantization")
    print("=" * 60)
    ae_config = json.loads(args.ae_results.read_text())["config"]
    ae_model = Autoencoder(input_dim=input_dim, latent_dim=ae_config["latent_dim"], hidden_dims=ae_config["hidden_dims"])
    ae_result = measure_torch_model("Autoencoder", ae_model, args.ae_checkpoint, input_dim)

    print("\n" + "=" * 60)
    print("VAE: fp32 vs int8 dynamic quantization")
    print("=" * 60)
    vae_config = json.loads(args.vae_results.read_text())["config"]
    vae_model = VariationalAutoencoder(input_dim=input_dim, latent_dim=vae_config["latent_dim"], hidden_dims=vae_config["hidden_dims"])
    vae_result = measure_torch_model("VAE", vae_model, args.vae_checkpoint, input_dim)

    summary = {
        "sklearn_models": sklearn_results,
        "autoencoder": ae_result,
        "vae": vae_result,
        "note": (
            "Latency/memory measured on this development machine's CPU, not on embedded/ARM "
            "hardware. For a genuine ARM number, run this same script on an Oracle Cloud "
            "Always-Free Ampere A1 instance (real ARM CPU, no cost) and report those figures "
            "alongside or instead of these. Full microcontroller-class (Cortex-M) validation "
            "is out of scope without physical hardware."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2) + "\n")
    print(f"\nSaved to {args.output}")


if __name__ == "__main__":
    main()

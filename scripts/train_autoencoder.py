from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def parse_hidden_dims(raw: str) -> list[int]:
    return [int(value) for value in raw.split(",") if value]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train an autoencoder baseline on CIC-IDS-2017.")
    parser.add_argument("--data-dir", type=Path, default=Path("data/CICIDS2017"))
    parser.add_argument("--prepared-dir", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=Path("experiments/autoencoder/results.json"))
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--latent-dim", type=int, default=16)
    parser.add_argument("--hidden-dims", type=str, default="128,64")
    parser.add_argument("--device", type=str, default=None)
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument("--checkpoint", type=Path, default=Path("experiments/autoencoder/model.pt"))
    parser.add_argument("--report", type=Path, default=Path("experiments/autoencoder/report.md"))
    parser.add_argument("--loss-plot", type=Path, default=Path("experiments/autoencoder/loss.png"))
    parser.add_argument("--score-plot", type=Path, default=Path("experiments/autoencoder/scores.png"))
    parser.add_argument("--max-train-samples", type=int, default=None)
    parser.add_argument("--max-eval-samples", type=int, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        import torch
    except ModuleNotFoundError as exc:
        raise SystemExit("PyTorch is required. Install dependencies with `uv sync`.") from exc
    try:
        import numpy as np
        from agri_iot_ids.data.cicids2017 import load_prepared_data, prepare_cicids_data
        from agri_iot_ids.evaluation import persist_run_summary, save_loss_plot, save_score_histogram, write_markdown_report
        from agri_iot_ids.models.autoencoder import Autoencoder
        from agri_iot_ids.training.engine import evaluate_scores, fit_autoencoder, score_autoencoder, select_threshold
    except ModuleNotFoundError as exc:
        raise SystemExit("Project dependencies are missing. Install them with `uv sync`.") from exc

    prepared = (
        load_prepared_data(args.prepared_dir)
        if args.prepared_dir is not None
        else prepare_cicids_data(args.data_dir, random_state=args.random_state)
    )
    rng = np.random.default_rng(args.random_state)
    x_train = prepared.x_train
    x_val = prepared.x_val
    y_val = prepared.y_val
    x_test = prepared.x_test
    y_test = prepared.y_test
    if args.max_train_samples and len(x_train) > args.max_train_samples:
        train_indices = rng.choice(len(x_train), size=args.max_train_samples, replace=False)
        x_train = x_train[train_indices]
    if args.max_eval_samples and len(x_val) > args.max_eval_samples:
        val_indices = rng.choice(len(x_val), size=args.max_eval_samples, replace=False)
        x_val = x_val[val_indices]
        y_val = y_val[val_indices]
    if args.max_eval_samples and len(x_test) > args.max_eval_samples:
        test_indices = rng.choice(len(x_test), size=args.max_eval_samples, replace=False)
        x_test = x_test[test_indices]
        y_test = y_test[test_indices]
    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
    hidden_dims = parse_hidden_dims(args.hidden_dims)
    model = Autoencoder(
        input_dim=prepared.input_dim,
        latent_dim=args.latent_dim,
        hidden_dims=hidden_dims,
    )

    history = fit_autoencoder(
        model=model,
        train_array=x_train,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        device=device,
        verbose=True,
    )

    val_scores = score_autoencoder(model, x_val, device=device)
    threshold = select_threshold(val_scores, y_val)
    val_metrics = evaluate_scores(val_scores, y_val, threshold)
    test_scores = score_autoencoder(model, x_test, device=device)
    test_metrics = evaluate_scores(test_scores, y_test, threshold)
    test_normal_scores = test_scores[y_test == 0]
    test_anomaly_scores = test_scores[y_test == 1]

    config = {
        "model": "autoencoder",
        "latent_dim": args.latent_dim,
        "hidden_dims": hidden_dims,
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "learning_rate": args.learning_rate,
        "device": device,
        "train_samples_used": int(len(x_train)),
        "val_samples_used": int(len(x_val)),
        "test_samples_used": int(len(x_test)),
    }
    persist_run_summary(args.output, config, history, val_metrics, test_metrics)
    args.checkpoint.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), args.checkpoint)
    save_loss_plot(history, args.loss_plot, title="Autoencoder Training Loss")
    save_score_histogram(
        normal_scores=test_normal_scores,
        anomaly_scores=test_anomaly_scores,
        threshold=threshold,
        output_path=args.score_plot,
        title="Autoencoder Test Reconstruction Scores",
    )
    write_markdown_report(
        args.report,
        config=config,
        validation_metrics=val_metrics,
        test_metrics=test_metrics,
        extra_sections={
            "Artifacts": f"""
            - checkpoint: {args.checkpoint}
            - metrics_json: {args.output}
            - loss_plot: {args.loss_plot}
            - score_plot: {args.score_plot}
            """
        },
    )
    print(f"Saved AE results to {args.output}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Optuna search for the autoencoder baseline.")
    parser.add_argument("--data-dir", type=Path, default=Path("data/CICIDS2017"))
    parser.add_argument("--prepared-dir", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=Path("experiments/autoencoder/optuna_results.json"))
    parser.add_argument("--trials", type=int, default=20)
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--device", type=str, default=None)
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument("--max-train-samples", type=int, default=None)
    parser.add_argument("--max-eval-samples", type=int, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        import optuna
        import torch
    except ModuleNotFoundError as exc:
        raise SystemExit("Optuna and PyTorch are required. Install dependencies with `uv sync`.") from exc
    try:
        import numpy as np
        from agri_iot_ids.data.cicids2017 import load_prepared_data, prepare_cicids_data
        from agri_iot_ids.models.autoencoder import Autoencoder
        from agri_iot_ids.training.engine import evaluate_scores, fit_autoencoder, score_autoencoder, select_threshold, save_json
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
    if args.max_train_samples and len(x_train) > args.max_train_samples:
        train_indices = rng.choice(len(x_train), size=args.max_train_samples, replace=False)
        x_train = x_train[train_indices]
    if args.max_eval_samples and len(x_val) > args.max_eval_samples:
        val_indices = rng.choice(len(x_val), size=args.max_eval_samples, replace=False)
        x_val = x_val[val_indices]
        y_val = y_val[val_indices]
    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")

    def objective(trial: optuna.Trial) -> float:
        latent_dim = trial.suggest_categorical("latent_dim", [8, 16, 32, 64])
        learning_rate = trial.suggest_float("learning_rate", 1e-4, 5e-3, log=True)
        batch_size = trial.suggest_categorical("batch_size", [256, 512, 1024])
        depth = trial.suggest_int("depth", 1, 3)
        width = trial.suggest_categorical("width", [64, 128, 256])
        hidden_dims = [width // (2 ** idx) for idx in range(depth)]

        model = Autoencoder(
            input_dim=prepared.input_dim,
            latent_dim=latent_dim,
            hidden_dims=hidden_dims,
        )
        fit_autoencoder(
            model=model,
            train_array=x_train,
            epochs=args.epochs,
            batch_size=batch_size,
            learning_rate=learning_rate,
            device=device,
        )

        val_scores = score_autoencoder(model, x_val, device=device)
        threshold = select_threshold(val_scores, y_val)
        metrics = evaluate_scores(val_scores, y_val, threshold)
        trial.set_user_attr("threshold", threshold)
        trial.set_user_attr("metrics", metrics)
        return metrics["f1"]

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=args.trials)

    save_json(
        {
            "best_value": study.best_value,
            "best_params": study.best_params,
            "best_trial_metrics": study.best_trial.user_attrs.get("metrics", {}),
            "train_samples_used": int(len(x_train)),
            "val_samples_used": int(len(x_val)),
        },
        args.output,
    )
    print(f"Saved Optuna results to {args.output}")


if __name__ == "__main__":
    main()

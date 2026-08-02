"""Preprocess the already-downloaded Farm-flow dataset (Ferreira et al., 2025,
Computers and Electrical Engineering 121:109892) into the same splits.npz /
metadata.json / scaler.pkl format used for CICIDS2017, for cross-dataset
validation.

Unlike the generic assumptions in download_prepare_farmflow.py, the actual
archive ships pre-split, pre-normalized binary files:
  Datasets/Farm-Flow_Train_Binary.csv (561,082 rows)
  Datasets/Farm-Flow_Test_Binary.csv  (3,546 rows)
with a clean binary label column "is_attack" (0.0/1.0, roughly balanced) and
a leftover multiclass column "traffic" (8 classes) that is dropped for this
binary-classification study. This script respects the dataset authors' own
train/test boundary rather than remixing it.

Usage:
    uv run python scripts/prepare_farmflow.py
"""
from __future__ import annotations

import argparse
import json
import pickle
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

LABEL_COLUMN = "is_attack"
DROP_COLUMNS = ("traffic",)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-dir", type=Path,
        default=Path("data/FarmFlow/extracted/Datasets"),
    )
    parser.add_argument("--artifact-dir", type=Path, default=Path("experiments/preprocessing/farmflow"))
    parser.add_argument("--output", type=Path, default=Path("experiments/preprocessing/farmflow_summary.json"))
    parser.add_argument("--val-fraction-of-train", type=float, default=0.2,
                         help="Fraction of the Train_Binary.csv normal rows held out, "
                              "combined with all its attack rows, to form the validation split.")
    parser.add_argument("--random-state", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        import numpy as np
        import pandas as pd
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import StandardScaler
    except ModuleNotFoundError as exc:
        raise SystemExit(f"Missing dependency: {exc}. Run `uv sync` first.") from exc

    train_path = args.data_dir / "Farm-Flow_Train_Binary.csv"
    test_path = args.data_dir / "Farm-Flow_Test_Binary.csv"
    if not train_path.exists() or not test_path.exists():
        raise SystemExit(f"Expected {train_path} and {test_path} to exist. Run the Farm-flow download/extraction first.")

    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    print(f"Loaded train: {train_df.shape}, test: {test_df.shape}")

    for df in (train_df, test_df):
        for col in DROP_COLUMNS:
            if col in df.columns:
                df.drop(columns=[col], inplace=True)

    feature_names = [c for c in train_df.columns if c != LABEL_COLUMN]
    assert list(test_df.columns) == list(train_df.columns), "Train/test column mismatch after dropping traffic."

    rng = np.random.default_rng(args.random_state)

    # Split the authors' Train_Binary.csv into an unsupervised-training pool
    # (normal only, for the Autoencoder) and a validation pool (normal + attack,
    # for threshold selection and the supervised-set assembly), mirroring the
    # CICIDS2017 pipeline's split semantics. Test_Binary.csv is used exactly as
    # given -- it is the dataset authors' own held-out test set, not remixed.
    train_normal = train_df[train_df[LABEL_COLUMN] == 0.0]
    train_attack = train_df[train_df[LABEL_COLUMN] == 1.0]

    x_train_pool, x_val_normal = train_test_split(
        train_normal[feature_names].to_numpy(dtype=np.float32),
        test_size=args.val_fraction_of_train, random_state=args.random_state, shuffle=True,
    )
    x_val_attack = train_attack[feature_names].to_numpy(dtype=np.float32)

    x_test = test_df[feature_names].to_numpy(dtype=np.float32)
    y_test = test_df[LABEL_COLUMN].to_numpy(dtype=np.int64)

    scaler = StandardScaler()
    x_train_scaled = scaler.fit_transform(x_train_pool).astype(np.float32)
    x_val_scaled = scaler.transform(
        np.concatenate([x_val_normal, x_val_attack], axis=0)
    ).astype(np.float32)
    x_test_scaled = scaler.transform(x_test).astype(np.float32)

    y_val = np.concatenate([
        np.zeros(len(x_val_normal), dtype=np.int64),
        np.ones(len(x_val_attack), dtype=np.int64),
    ])

    args.artifact_dir.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        args.artifact_dir / "splits.npz",
        x_train=x_train_scaled, x_val=x_val_scaled, y_val=y_val,
        x_test=x_test_scaled, y_test=y_test,
    )
    metadata = {
        "feature_names": feature_names,
        "label_column": LABEL_COLUMN,
        "total_rows": int(len(train_df) + len(test_df)),
        "retained_rows": int(len(train_df) + len(test_df)),
        "normal_rows": int((train_df[LABEL_COLUMN] == 0.0).sum() + (test_df[LABEL_COLUMN] == 0.0).sum()),
        "anomaly_rows": int((train_df[LABEL_COLUMN] == 1.0).sum() + (test_df[LABEL_COLUMN] == 1.0).sum()),
        "source_files": ["Farm-Flow_Train_Binary.csv", "Farm-Flow_Test_Binary.csv"],
        "dataset": "Farm-flow (Ferreira et al., 2025, Computers and Electrical Engineering 121:109892)",
        "source_url": "https://zenodo.org/records/10964648",
        "note": "Features arrive pre-normalized by the dataset authors; this pipeline's StandardScaler is applied on top for consistency with the CICIDS2017 protocol, not because the raw features were unscaled.",
    }
    (args.artifact_dir / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    with (args.artifact_dir / "scaler.pkl").open("wb") as fh:
        pickle.dump(scaler, fh)

    summary = {
        **metadata,
        "feature_count": len(feature_names),
        "train_samples": int(len(x_train_scaled)),
        "val_samples": int(len(x_val_scaled)),
        "val_anomalies": int(y_val.sum()),
        "test_samples": int(len(x_test_scaled)),
        "test_anomalies": int(y_test.sum()),
        "artifact_dir": str(args.artifact_dir),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    print(f"\nSaved prepared Farm-flow splits to {args.artifact_dir}")


if __name__ == "__main__":
    main()

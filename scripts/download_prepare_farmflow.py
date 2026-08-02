"""Download and preprocess the Farm-flow dataset (Ferreira et al., 2025,
Computers and Electrical Engineering 121:109892) for cross-dataset validation
against CICIDS2017.

Source: https://zenodo.org/records/10964648 (farm-flow.zip, ~501 MB, 1.31M
labeled flow instances, 8 real AG-IoT attack types + benign traffic).

This mirrors the structure of src/agri_iot_ids/data/cicids2017.py so the
resulting splits.npz / metadata.json / scaler.pkl can be loaded by the
existing train_sklearn.py / train_autoencoder.py / train_vae.py scripts by
pointing --prepared-dir at the output directory this script writes to.

Usage:
    uv run python scripts/download_prepare_farmflow.py

If the dataset's internal folder/file layout differs from what this script
guesses, it will print what it found under Dataset/ so you can pass an
explicit --csv-glob / --label-column override.
"""
from __future__ import annotations

import argparse
import json
import pickle
import subprocess
import zipfile
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

ZENODO_FILE_URL = "https://zenodo.org/records/10964648/files/farm-flow.zip?download=1"

LABEL_CANDIDATES = (
    "Label", "label", "Attack", "attack", "Attack_type", "attack_type",
    "class", "Class", "Category", "category",
)
NORMAL_LABELS = {
    "BENIGN", "Benign", "benign", "Normal", "normal", "NORMAL", "0",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download + preprocess Farm-flow dataset.")
    parser.add_argument("--data-dir", type=Path, default=Path("data/FarmFlow"))
    parser.add_argument("--artifact-dir", type=Path, default=Path("experiments/preprocessing/farmflow"))
    parser.add_argument("--output", type=Path, default=Path("experiments/preprocessing/farmflow_summary.json"))
    parser.add_argument(
        "--csv-glob",
        type=str,
        default="**/*inary*.csv",
        help="Glob (relative to the extracted Dataset/ folder) selecting which CSV(s) to load. "
             "Default targets the binary-classification files. If this picks up the wrong files, "
             "re-run with --list-only first to see what's available, then pass an explicit glob.",
    )
    parser.add_argument("--label-column", type=str, default=None, help="Override auto-detected label column name.")
    parser.add_argument("--list-only", action="store_true", help="Just download/extract and print the file tree, then exit.")
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--val-size", type=float, default=0.2)
    parser.add_argument("--random-state", type=int, default=42)
    return parser.parse_args()


def download_and_extract(data_dir: Path) -> Path:
    data_dir.mkdir(parents=True, exist_ok=True)
    archive_path = data_dir / "farm-flow.zip"
    extract_dir = data_dir / "extracted"

    if not archive_path.exists():
        print(f"Downloading Farm-flow (~501 MB) from Zenodo to {archive_path} ...")
        subprocess.run(
            ["curl", "-L", "--fail", "-o", str(archive_path), ZENODO_FILE_URL],
            check=True,
        )
        print("Download complete.")
    else:
        print(f"Archive already present at {archive_path}, skipping download.")

    if not extract_dir.exists():
        print(f"Extracting to {extract_dir} ...")
        with zipfile.ZipFile(archive_path) as zf:
            zf.extractall(extract_dir)
        print("Extraction complete.")
    else:
        print(f"Already extracted at {extract_dir}, skipping.")

    return extract_dir


def print_tree(root: Path, max_entries: int = 200) -> None:
    print(f"\n=== File tree under {root} (first {max_entries} entries) ===")
    count = 0
    for path in sorted(root.rglob("*")):
        if path.is_file():
            print(f"  {path.relative_to(root)}  ({path.stat().st_size / 1e6:.1f} MB)")
            count += 1
            if count >= max_entries:
                print("  ... (truncated)")
                break


def resolve_label_column(frame, override: str | None) -> str:
    if override:
        if override not in frame.columns:
            raise KeyError(f"--label-column {override!r} not found. Columns: {list(frame.columns)}")
        return override
    for candidate in LABEL_CANDIDATES:
        if candidate in frame.columns:
            return candidate
    raise KeyError(
        f"Could not auto-detect a label column among {LABEL_CANDIDATES}. "
        f"Actual columns: {list(frame.columns)}. Pass --label-column explicitly."
    )


def main() -> None:
    args = parse_args()
    extract_dir = download_and_extract(args.data_dir)

    if args.list_only:
        print_tree(extract_dir)
        return

    try:
        import numpy as np
        import pandas as pd
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import StandardScaler
    except ModuleNotFoundError as exc:
        raise SystemExit(f"Missing dependency: {exc}. Run `uv sync` first.") from exc

    csv_files = sorted(extract_dir.glob(args.csv_glob))
    if not csv_files:
        print(f"No files matched glob {args.csv_glob!r} under {extract_dir}.")
        print_tree(extract_dir)
        raise SystemExit(
            "Adjust --csv-glob to point at the right file(s) based on the tree printed above, "
            "then re-run."
        )

    print(f"Loading {len(csv_files)} file(s): {[p.name for p in csv_files]}")
    frames = [pd.read_csv(p, low_memory=False) for p in csv_files]
    frame = pd.concat(frames, ignore_index=True)
    frame.columns = [str(c).strip() for c in frame.columns]
    total_rows = len(frame)

    label_column = resolve_label_column(frame, args.label_column)
    labels = frame[label_column].astype(str).str.strip()
    features = frame.drop(columns=[label_column]).copy()
    features.columns = [c.strip() for c in features.columns]

    # Drop any other obvious non-numeric identifier columns (IPs, timestamps, flow IDs)
    # that would break scaling / aren't present in CICIDS2017 either.
    for column in list(features.columns):
        if features[column].dtype == object:
            features[column] = pd.to_numeric(features[column], errors="coerce")
    non_numeric_all_nan = [c for c in features.columns if features[c].isna().all()]
    if non_numeric_all_nan:
        print(f"Dropping {len(non_numeric_all_nan)} non-numeric columns: {non_numeric_all_nan}")
        features = features.drop(columns=non_numeric_all_nan)

    features = features.replace([np.inf, -np.inf], np.nan)
    valid_mask = ~(features.isna().any(axis=1))
    features = features.loc[valid_mask].reset_index(drop=True)
    labels = labels.loc[valid_mask].reset_index(drop=True)
    retained_rows = len(features)

    binary_labels = (~labels.isin(NORMAL_LABELS)).astype(np.int64).to_numpy()
    normal_mask = binary_labels == 0
    anomaly_mask = ~normal_mask
    print(f"Retained {retained_rows}/{total_rows} rows. Normal: {normal_mask.sum()}, Attack: {anomaly_mask.sum()}")
    if normal_mask.sum() < 100:
        print(
            "WARNING: very few 'normal' rows detected -- Farm-flow's overall class balance is "
            "known to be attack-heavy (27,458 normal vs 1,282,429 attack across the full dataset). "
            "If this looks wrong, double check --label-column and NORMAL_LABELS matching."
        )

    x_normal = features.loc[normal_mask].to_numpy(dtype=np.float32)
    x_anomaly = features.loc[anomaly_mask].to_numpy(dtype=np.float32)

    x_train, x_normal_holdout = train_test_split(
        x_normal, test_size=args.test_size + args.val_size,
        random_state=args.random_state, shuffle=True,
    )
    val_ratio = args.val_size / (args.test_size + args.val_size)
    x_val_normal, x_test_normal = train_test_split(
        x_normal_holdout, test_size=1.0 - val_ratio,
        random_state=args.random_state, shuffle=True,
    )
    x_val_anomaly, x_test_anomaly = train_test_split(
        x_anomaly, test_size=0.5, random_state=args.random_state, shuffle=True,
    )

    scaler = StandardScaler()
    x_train_scaled = scaler.fit_transform(x_train).astype(np.float32)
    x_val_scaled = scaler.transform(np.concatenate([x_val_normal, x_val_anomaly], axis=0)).astype(np.float32)
    x_test_scaled = scaler.transform(np.concatenate([x_test_normal, x_test_anomaly], axis=0)).astype(np.float32)

    y_val = np.concatenate([np.zeros(len(x_val_normal), dtype=np.int64), np.ones(len(x_val_anomaly), dtype=np.int64)])
    y_test = np.concatenate([np.zeros(len(x_test_normal), dtype=np.int64), np.ones(len(x_test_anomaly), dtype=np.int64)])

    args.artifact_dir.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        args.artifact_dir / "splits.npz",
        x_train=x_train_scaled, x_val=x_val_scaled, y_val=y_val,
        x_test=x_test_scaled, y_test=y_test,
    )
    metadata = {
        "feature_names": list(features.columns),
        "label_column": label_column,
        "total_rows": int(total_rows),
        "retained_rows": int(retained_rows),
        "normal_rows": int(normal_mask.sum()),
        "anomaly_rows": int(anomaly_mask.sum()),
        "source_files": [p.name for p in csv_files],
        "dataset": "Farm-flow (Ferreira et al., 2025, Computers and Electrical Engineering 121:109892)",
        "source_url": "https://zenodo.org/records/10964648",
    }
    (args.artifact_dir / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    with (args.artifact_dir / "scaler.pkl").open("wb") as fh:
        pickle.dump(scaler, fh)

    summary = {
        **metadata,
        "feature_count": len(features.columns),
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
    print(
        "\nTo evaluate existing models on this dataset:\n"
        f"  uv run python scripts/train_sklearn.py --prepared-dir {args.artifact_dir} "
        f"--output-dir experiments/sklearn_farmflow\n"
        f"  uv run python scripts/train_autoencoder.py --prepared-dir {args.artifact_dir} "
        f"--output experiments/autoencoder_farmflow/results.json --checkpoint experiments/autoencoder_farmflow/model.pt "
        f"--report experiments/autoencoder_farmflow/report.md --loss-plot experiments/autoencoder_farmflow/loss.png "
        f"--score-plot experiments/autoencoder_farmflow/scores.png"
    )


if __name__ == "__main__":
    main()

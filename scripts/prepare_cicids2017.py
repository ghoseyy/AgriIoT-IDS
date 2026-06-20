from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from agri_iot_ids.data.cicids2017 import prepare_cicids_data, save_prepared_data


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare CIC-IDS-2017 splits for anomaly detection.")
    parser.add_argument("--data-dir", type=Path, default=Path("data/CICIDS2017"))
    parser.add_argument("--output", type=Path, default=Path("experiments/preprocessing/cicids2017_summary.json"))
    parser.add_argument("--artifact-dir", type=Path, default=Path("experiments/preprocessing/cicids2017"))
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--val-size", type=float, default=0.2)
    parser.add_argument("--random-state", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    prepared = prepare_cicids_data(
        data_dir=args.data_dir,
        test_size=args.test_size,
        val_size=args.val_size,
        random_state=args.random_state,
    )
    save_prepared_data(prepared, args.artifact_dir)

    payload = {
        "source_files": prepared.source_files,
        "label_column": prepared.label_column,
        "total_rows": prepared.total_rows,
        "retained_rows": prepared.retained_rows,
        "dropped_rows": prepared.total_rows - prepared.retained_rows,
        "normal_rows": prepared.normal_rows,
        "anomaly_rows": prepared.anomaly_rows,
        "feature_count": len(prepared.feature_names),
        "train_samples": int(len(prepared.x_train)),
        "val_samples": int(len(prepared.x_val)),
        "val_anomalies": int(prepared.y_val.sum()),
        "test_samples": int(len(prepared.x_test)),
        "test_anomalies": int(prepared.y_test.sum()),
        "artifact_dir": str(args.artifact_dir),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

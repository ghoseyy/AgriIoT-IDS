from __future__ import annotations

from dataclasses import dataclass
import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


LABEL_CANDIDATES = ("Label", "label")
NORMAL_LABELS = {"BENIGN", "Benign", "benign"}
DATA_FILE_PATTERNS = ("*.csv", "*.parquet")


@dataclass
class PreparedData:
    feature_names: list[str]
    scaler: StandardScaler
    x_train: np.ndarray
    x_val: np.ndarray
    y_val: np.ndarray
    x_test: np.ndarray
    y_test: np.ndarray
    label_column: str
    total_rows: int
    retained_rows: int
    normal_rows: int
    anomaly_rows: int
    source_files: list[str]

    @property
    def input_dim(self) -> int:
        return int(self.x_train.shape[1])


def discover_csv_files(data_dir: Path) -> list[Path]:
    files: list[Path] = []
    for pattern in DATA_FILE_PATTERNS:
        files.extend(path for path in data_dir.rglob(pattern) if path.is_file())
    return sorted(files)


def load_cicids_frame(data_dir: Path) -> pd.DataFrame:
    csv_files = discover_csv_files(data_dir)
    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files found in {data_dir}. Download CIC-IDS-2017 files first."
        )

    frames = []
    for csv_path in csv_files:
        if csv_path.suffix.lower() == ".csv":
            frame = pd.read_csv(csv_path, low_memory=False)
        elif csv_path.suffix.lower() == ".parquet":
            frame = pd.read_parquet(csv_path)
        else:
            continue
        frame.columns = [str(column).strip() for column in frame.columns]
        frames.append(frame)

    return pd.concat(frames, ignore_index=True)


def _resolve_label_column(frame: pd.DataFrame) -> str:
    for candidate in LABEL_CANDIDATES:
        if candidate in frame.columns:
            return candidate
    raise KeyError(f"Expected one of {LABEL_CANDIDATES} in dataset columns.")


def _coerce_numeric_features(frame: pd.DataFrame, label_column: str) -> tuple[pd.DataFrame, pd.Series]:
    labels = frame[label_column].astype(str).str.strip()
    features = frame.drop(columns=[label_column]).copy()
    features.columns = [column.strip() for column in features.columns]

    for column in features.columns:
        if features[column].dtype == object:
            features[column] = features[column].astype(str).str.strip()
        features[column] = pd.to_numeric(features[column], errors="coerce")

    features = features.replace([np.inf, -np.inf], np.nan)
    valid_mask = ~(features.isna().any(axis=1))
    cleaned_features = features.loc[valid_mask].reset_index(drop=True)
    cleaned_labels = labels.loc[valid_mask].reset_index(drop=True)
    return cleaned_features, cleaned_labels


def prepare_cicids_data(
    data_dir: Path,
    test_size: float = 0.2,
    val_size: float = 0.2,
    random_state: int = 42,
) -> PreparedData:
    csv_files = discover_csv_files(data_dir)
    frame = load_cicids_frame(data_dir)
    total_rows = len(frame)
    label_column = _resolve_label_column(frame)
    features, labels = _coerce_numeric_features(frame, label_column)
    retained_rows = len(features)
    binary_labels = (~labels.isin(NORMAL_LABELS)).astype(np.int64).to_numpy()

    normal_mask = binary_labels == 0
    anomaly_mask = ~normal_mask

    x_normal = features.loc[normal_mask].to_numpy(dtype=np.float32)
    x_anomaly = features.loc[anomaly_mask].to_numpy(dtype=np.float32)

    x_train, x_normal_holdout = train_test_split(
        x_normal,
        test_size=test_size + val_size,
        random_state=random_state,
        shuffle=True,
    )

    val_ratio = val_size / (test_size + val_size)
    x_val_normal, x_test_normal = train_test_split(
        x_normal_holdout,
        test_size=1.0 - val_ratio,
        random_state=random_state,
        shuffle=True,
    )

    x_val_anomaly, x_test_anomaly = train_test_split(
        x_anomaly,
        test_size=0.5,
        random_state=random_state,
        shuffle=True,
    )

    scaler = StandardScaler()
    x_train_scaled = scaler.fit_transform(x_train).astype(np.float32)
    x_val_scaled = scaler.transform(
        np.concatenate([x_val_normal, x_val_anomaly], axis=0)
    ).astype(np.float32)
    x_test_scaled = scaler.transform(
        np.concatenate([x_test_normal, x_test_anomaly], axis=0)
    ).astype(np.float32)

    y_val = np.concatenate(
        [
            np.zeros(len(x_val_normal), dtype=np.int64),
            np.ones(len(x_val_anomaly), dtype=np.int64),
        ]
    )
    y_test = np.concatenate(
        [
            np.zeros(len(x_test_normal), dtype=np.int64),
            np.ones(len(x_test_anomaly), dtype=np.int64),
        ]
    )

    return PreparedData(
        feature_names=list(features.columns),
        scaler=scaler,
        x_train=x_train_scaled,
        x_val=x_val_scaled,
        y_val=y_val,
        x_test=x_test_scaled,
        y_test=y_test,
        label_column=label_column,
        total_rows=total_rows,
        retained_rows=retained_rows,
        normal_rows=int(normal_mask.sum()),
        anomaly_rows=int(anomaly_mask.sum()),
        source_files=[path.name for path in csv_files],
    )


def save_prepared_data(prepared: PreparedData, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output_dir / "splits.npz",
        x_train=prepared.x_train,
        x_val=prepared.x_val,
        y_val=prepared.y_val,
        x_test=prepared.x_test,
        y_test=prepared.y_test,
    )
    metadata = {
        "feature_names": prepared.feature_names,
        "label_column": prepared.label_column,
        "total_rows": prepared.total_rows,
        "retained_rows": prepared.retained_rows,
        "normal_rows": prepared.normal_rows,
        "anomaly_rows": prepared.anomaly_rows,
        "source_files": prepared.source_files,
    }
    (output_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n",
        encoding="utf-8",
    )
    with (output_dir / "scaler.pkl").open("wb") as handle:
        pickle.dump(prepared.scaler, handle)


def load_prepared_data(input_dir: Path) -> PreparedData:
    bundle_path = input_dir / "splits.npz"
    metadata_path = input_dir / "metadata.json"
    scaler_path = input_dir / "scaler.pkl"

    if not bundle_path.exists():
        raise FileNotFoundError(f"Missing prepared split bundle: {bundle_path}")
    if not metadata_path.exists():
        raise FileNotFoundError(f"Missing prepared metadata: {metadata_path}")
    if not scaler_path.exists():
        raise FileNotFoundError(f"Missing scaler artifact: {scaler_path}")

    bundle = np.load(bundle_path)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    with scaler_path.open("rb") as handle:
        scaler = pickle.load(handle)

    return PreparedData(
        feature_names=list(metadata["feature_names"]),
        scaler=scaler,
        x_train=bundle["x_train"].astype(np.float32),
        x_val=bundle["x_val"].astype(np.float32),
        y_val=bundle["y_val"].astype(np.int64),
        x_test=bundle["x_test"].astype(np.float32),
        y_test=bundle["y_test"].astype(np.int64),
        label_column=str(metadata["label_column"]),
        total_rows=int(metadata["total_rows"]),
        retained_rows=int(metadata["retained_rows"]),
        normal_rows=int(metadata["normal_rows"]),
        anomaly_rows=int(metadata["anomaly_rows"]),
        source_files=[str(item) for item in metadata["source_files"]],
    )

"""Measure real training energy/carbon footprint using codecarbon, an
established open-source tool for ML energy/emissions estimation (CPU power
via RAPL/psutil-based modeling, not a wall power meter, but a legitimate
standard estimate rather than an invented number).

Usage:
    uv run python scripts/measure_training_energy.py
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def main() -> None:
    try:
        import numpy as np
        from sklearn.ensemble import RandomForestClassifier
        from codecarbon import OfflineEmissionsTracker
        from agri_iot_ids.data.cicids2017 import load_prepared_data
    except ModuleNotFoundError as exc:
        raise SystemExit(f"Missing dependency: {exc}. Run `uv sync` first.") from exc

    prepared = load_prepared_data(Path("experiments/preprocessing/cicids2017"))
    rng = np.random.default_rng(42)
    X_val, y_val = prepared.x_val, prepared.y_val
    X_attack = X_val[y_val == 1]
    y_attack = np.ones(len(X_attack), dtype=int)
    n_normal = min(len(prepared.x_train), len(X_attack) * 3)
    idx_normal = rng.choice(len(prepared.x_train), size=n_normal, replace=False)
    X_train = np.concatenate([prepared.x_train[idx_normal], X_attack], axis=0)
    y_train = np.concatenate([np.zeros(n_normal, dtype=int), y_attack], axis=0)

    output_dir = Path("experiments/training_energy")
    output_dir.mkdir(parents=True, exist_ok=True)

    tracker = OfflineEmissionsTracker(
        country_iso_code="NPL",  # Nepal, matching the paper's deployment context
        output_dir=str(output_dir),
        log_level="error",
        save_to_file=True,
        tracking_mode="process",
    )
    tracker.start()
    model = RandomForestClassifier(n_estimators=100, max_depth=20, n_jobs=-1, random_state=42)
    model.fit(X_train, y_train)
    emissions_kg = tracker.stop()

    energy_kwh = tracker.final_emissions_data.energy_consumed if tracker.final_emissions_data else None
    duration_s = tracker.final_emissions_data.duration if tracker.final_emissions_data else None

    summary = {
        "model": "Random Forest (100 trees, same config as main experiment)",
        "train_samples": int(len(X_train)),
        "measurement_tool": "codecarbon (OfflineEmissionsTracker, country=NPL grid carbon intensity)",
        "duration_seconds": duration_s,
        "energy_consumed_kwh": energy_kwh,
        "co2_emissions_kg": emissions_kg,
        "caveat": (
            "CPU/RAM power estimated from hardware modeling (psutil/RAPL-based), not a wall power "
            "meter reading. Reported as a standard, tool-based estimate, not a lab measurement."
        ),
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, default=str) + "\n")
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()

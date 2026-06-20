from __future__ import annotations

from pathlib import Path
import textwrap

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from agri_iot_ids.training.engine import save_json


def persist_run_summary(
    output_path: Path,
    config: dict,
    history: list[dict],
    validation_metrics: dict,
    test_metrics: dict,
) -> None:
    save_json(
        {
            "config": config,
            "history": history,
            "validation_metrics": validation_metrics,
            "test_metrics": test_metrics,
        },
        output_path,
    )


def save_loss_plot(history: list[dict], output_path: Path, title: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    epochs = [row["epoch"] for row in history]
    plt.figure(figsize=(8, 4.5))
    for key in history[0].keys():
        if key != "epoch":
            plt.plot(epochs, [row[key] for row in history], label=key)
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()


def save_score_histogram(
    normal_scores: np.ndarray,
    anomaly_scores: np.ndarray,
    threshold: float,
    output_path: Path,
    title: str,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(8, 4.5))
    plt.hist(normal_scores, bins=50, alpha=0.7, label="Normal", density=True)
    plt.hist(anomaly_scores, bins=50, alpha=0.7, label="Anomaly", density=True)
    plt.axvline(threshold, color="black", linestyle="--", label=f"Threshold={threshold:.6f}")
    plt.xlabel("Reconstruction error")
    plt.ylabel("Density")
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()


def write_markdown_report(
    output_path: Path,
    config: dict,
    validation_metrics: dict,
    test_metrics: dict,
    extra_sections: dict[str, str] | None = None,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Phase 1 Baseline Run",
        "",
        "## Configuration",
        "",
    ]
    for key, value in config.items():
        lines.append(f"- {key}: {value}")

    lines.extend(["", "## Validation Metrics", ""])
    for key, value in validation_metrics.items():
        lines.append(f"- {key}: {value:.6f}" if isinstance(value, float) else f"- {key}: {value}")

    lines.extend(["", "## Test Metrics", ""])
    for key, value in test_metrics.items():
        lines.append(f"- {key}: {value:.6f}" if isinstance(value, float) else f"- {key}: {value}")

    if extra_sections:
        for title, body in extra_sections.items():
            lines.extend(["", f"## {title}", "", textwrap.dedent(body).strip(), ""])

    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

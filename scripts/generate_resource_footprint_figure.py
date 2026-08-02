"""Bar chart for model size (KB, log scale): our sklearn models, our AE/VAE
before and after int8 quantization, and two directly-comparable literature
reference points (Panopoulos2026, Albaiz2026 -- both report an on-device KB
footprint, unlike Chehade2025/Jamshidi2025 which report params/MB and aren't
apples-to-apples with a KB weight-file size, so those two are left as text
comparisons only, not plotted here). Reads real data from
experiments/resource_footprint/results.json -- no invented values.
"""
import json
import os

import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({
    'font.size': 8,
    'font.family': 'serif',
    'font.serif': ['Times New Roman'],
    'axes.labelsize': 8,
    'xtick.labelsize': 7,
    'ytick.labelsize': 7,
    'legend.fontsize': 7,
    'figure.dpi': 600,
})

# Literature reference points: (label, KB, hatch) -- both report a direct
# on-device size figure comparable in kind to ours, unlike Chehade2025 (params
# only) or Jamshidi2025 (113.2 MB total memory, a different measurement basis).
LITERATURE_REFS = [
    ("Panopoulos2026\n(RPi Zero 2W)", 40.0),
    ("Albaiz2026\n(STM32 flash)", 63.0),
]


def plot_resource_footprint(results_path, output_path):
    with open(results_path) as f:
        data = json.load(f)

    labels, sizes, hatches = [], [], []

    for row in data["sklearn_models"]:
        labels.append(row["model"].replace(" ", "\n"))
        sizes.append(row["size_kb"])
        hatches.append("")

    ae = data["autoencoder"]
    labels += ["AE\n(fp32)", "AE\n(int8)"]
    sizes += [ae["fp32_size_kb"], ae["int8_dynamic_quantized_size_kb"]]
    hatches += ["", "//"]

    vae = data["vae"]
    labels += ["VAE\n(fp32)", "VAE\n(int8)"]
    sizes += [vae["fp32_size_kb"], vae["int8_dynamic_quantized_size_kb"]]
    hatches += ["", "//"]

    for lit_label, lit_kb in LITERATURE_REFS:
        labels.append(lit_label)
        sizes.append(lit_kb)
        hatches.append("xx")

    fig, ax = plt.subplots(figsize=(7.0, 2.6))
    x = np.arange(len(labels))
    colors = ['white'] * len(labels)

    bars = ax.bar(x, sizes, color=colors, edgecolor='black', hatch=hatches)
    ax.set_yscale('log')
    ax.set_ylabel('Model size (KB, log scale)')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=6)
    ax.grid(axis='y', linestyle='--', linewidth=0.5, color='gray', alpha=0.5)

    # Visually separate "ours" from "literature reference" groups
    ax.axvline(len(labels) - len(LITERATURE_REFS) - 0.5, color='gray', linestyle=':', linewidth=0.8)
    ax.text(len(labels) - len(LITERATURE_REFS) - 0.5 - 0.3, ax.get_ylim()[1] * 0.5,
            'this paper', fontsize=6, ha='right', style='italic', color='gray')
    ax.text(len(labels) - len(LITERATURE_REFS) - 0.5 + 0.3, ax.get_ylim()[1] * 0.5,
            'literature\n(different HW)', fontsize=6, ha='left', style='italic', color='gray')

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


if __name__ == "__main__":
    plot_resource_footprint('experiments/resource_footprint/results.json', 'arxiv_final/figure8_resource_footprint.png')
    plot_resource_footprint('experiments/resource_footprint/results.json', 'cee_submission/figure8_resource_footprint.png')
    print("Saved figure8_resource_footprint.png to both submission bundles")

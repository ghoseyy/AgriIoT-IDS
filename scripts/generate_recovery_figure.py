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

CONN_LABELS = {1.0: "Full\n(1.0)", 0.7: "Degraded\n(0.7)", 0.4: "Poor\n(0.4)"}
COMP_LABELS = {3: "Ample", 2: "Moderate", 1: "Constrained"}


def plot_recovery_gains(results_path, output_path):
    with open(results_path) as f:
        data = json.load(f)
    rows = data["results"]

    connectivities = [1.0, 0.7, 0.4]
    computes = [3, 2, 1]

    fig, ax = plt.subplots(figsize=(3.5, 2.6))
    x = np.arange(len(connectivities))
    width = 0.25
    hatches = ['', '//', 'xx']

    for i, comp in enumerate(computes):
        gains = []
        for conn in connectivities:
            row = next(r for r in rows if r["connectivity"] == conn and r["compute_budget"] == comp)
            gains.append(row["mttr_gain_pct"])
        ax.bar(x + (i - 1) * width, gains, width, label=COMP_LABELS[comp],
               color='white', edgecolor='black', hatch=hatches[i])

    ax.set_ylabel('MTTR improvement (%)')
    ax.set_xlabel('Connectivity reliability')
    ax.set_xticks(x)
    ax.set_xticklabels([CONN_LABELS[c] for c in connectivities])
    ax.set_ylim(0, 100)
    ax.legend(title='Compute budget', frameon=False)
    ax.grid(axis='y', linestyle='--', linewidth=0.5, color='gray', alpha=0.5)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


if __name__ == "__main__":
    os.makedirs('arxiv_final', exist_ok=True)
    plot_recovery_gains('experiments/recovery/results.json', 'arxiv_final/figure6_recovery_mttr.png')
    print("Saved arxiv_final/figure6_recovery_mttr.png")

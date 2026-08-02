"""Bar chart for the hybrid ablation (Tier 1 vs Tier 1+2): F1, Recall, and
False Positive Rate side by side, visualizing the trade-off the results
table reports in numbers. Reads real data from
experiments/hybrid_ablation/results.json -- no invented values.
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


def plot_hybrid_ablation(results_path, output_path):
    with open(results_path) as f:
        data = json.load(f)

    tier1 = data["tier1_rf_only_metrics"]
    tier12 = data["tier1_plus_tier2_metrics"]

    metrics = ["F1", "Recall", "FPR"]
    tier1_vals = [tier1["f1"], tier1["recall"], tier1["false_positive_rate"]]
    tier12_vals = [tier12["f1"], tier12["recall"], tier12["false_positive_rate"]]

    fig, axes = plt.subplots(1, 2, figsize=(3.5, 2.6), gridspec_kw={"width_ratios": [2, 1]})

    # Left panel: F1 and Recall (both near 1.0, share a zoomed y-axis)
    ax = axes[0]
    x = np.arange(2)
    width = 0.32
    bar1 = ax.bar(x - width / 2, tier1_vals[:2], width, label="Tier 1 (RF)",
                  color='white', edgecolor='black', hatch='')
    bar2 = ax.bar(x + width / 2, tier12_vals[:2], width, label="Tier 1+2 (RF+AE)",
                  color='white', edgecolor='black', hatch='//')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics[:2])
    ax.set_ylim(0.990, 1.001)
    ax.set_ylabel("Score")
    ax.grid(axis='y', linestyle='--', linewidth=0.5, color='gray', alpha=0.5)
    fig.legend(handles=[bar1, bar2], loc='upper center', bbox_to_anchor=(0.5, 1.08),
               ncol=2, frameon=False, fontsize=6.5)

    # Right panel: FPR, in percent, own axis since it's two orders of magnitude smaller
    ax2 = axes[1]
    fpr_pct = [tier1_vals[2] * 100, tier12_vals[2] * 100]
    ax2.bar([0], [fpr_pct[0]], width=0.4, color='white', edgecolor='black', hatch='')
    ax2.bar([1], [fpr_pct[1]], width=0.4, color='white', edgecolor='black', hatch='//')
    ax2.set_xticks([0, 1])
    ax2.set_xticklabels(["Tier 1", "Tier 1+2"], rotation=15)
    ax2.set_ylabel("False Positive Rate (%)")
    ax2.grid(axis='y', linestyle='--', linewidth=0.5, color='gray', alpha=0.5)

    plt.tight_layout(rect=[0, 0, 1, 0.92])
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()


if __name__ == "__main__":
    plot_hybrid_ablation('experiments/hybrid_ablation/results.json', 'arxiv_final/figure7_hybrid_ablation.png')
    plot_hybrid_ablation('experiments/hybrid_ablation/results.json', 'cee_submission/figure7_hybrid_ablation.png')
    print("Saved figure7_hybrid_ablation.png to both submission bundles")

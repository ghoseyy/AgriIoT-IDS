"""Two figures from experiments/rigor_analysis/results.json: RF feature
importance (horizontal bar chart) and confusion matrices for Tier 1 and
Tier 1+2 side by side. Real data only, matching existing figure style.
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


def plot_feature_importance(data, output_path):
    top = data["top_feature_importances"]
    labels = [row["feature"] for row in top][::-1]
    values = [row["importance"] for row in top][::-1]

    fig, ax = plt.subplots(figsize=(3.5, 3.2))
    y = np.arange(len(labels))
    ax.barh(y, values, color='white', edgecolor='black', hatch='//')
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=6)
    ax.set_xlabel("Gini importance")
    ax.grid(axis='x', linestyle='--', linewidth=0.5, color='gray', alpha=0.5)
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()


def plot_confusion_matrices(data, output_path):
    fig, axes = plt.subplots(1, 2, figsize=(4.2, 2.4))
    titles = ["Tier 1 (RF only)", "Tier 1+2 (RF+AE)"]
    keys = ["confusion_matrix_tier1", "confusion_matrix_tier1_plus_2"]

    for ax, title, key in zip(axes, titles, keys):
        cm = np.array(data[key]["matrix"])
        labels = data[key]["labels"]
        im = ax.imshow(cm, cmap='Greys', aspect='auto')
        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(labels, fontsize=6)
        ax.set_yticklabels(labels, fontsize=6)
        ax.set_xlabel("Predicted")
        ax.set_ylabel("Actual")
        ax.set_title(title, fontsize=7)
        max_val = cm.max()
        for i in range(2):
            for j in range(2):
                color = 'white' if cm[i, j] > max_val * 0.5 else 'black'
                ax.text(j, i, f"{cm[i, j]:,}", ha='center', va='center', fontsize=6.5, color=color)

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()


if __name__ == "__main__":
    with open('experiments/rigor_analysis/results.json') as f:
        data = json.load(f)

    plot_feature_importance(data, 'arxiv_final/figure9_feature_importance.png')
    plot_feature_importance(data, 'cee_submission/figure9_feature_importance.png')
    plot_confusion_matrices(data, 'arxiv_final/figure10_confusion_matrices.png')
    plot_confusion_matrices(data, 'cee_submission/figure10_confusion_matrices.png')
    print("Saved figure9_feature_importance.png and figure10_confusion_matrices.png to both bundles")

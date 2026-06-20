import matplotlib.pyplot as plt
import numpy as np
import json
import os

# IEEEtran styling configuration
plt.rcParams.update({
    'font.size': 8,
    'font.family': 'serif',
    'font.serif': ['Times New Roman'],
    'axes.labelsize': 8,
    'xtick.labelsize': 7,
    'ytick.labelsize': 7,
    'legend.fontsize': 7,
    'figure.dpi': 600,
    'savefig.format': 'pdf'
})

# Ensure target directory exists
os.makedirs('writing/figures', exist_ok=True)

def plot_metric_comparison():
    # Metrics extracted from results.json files
    models = ['RF', 'DT', 'LR', 'AE (Full)', 'AE (Quick)']
    f1 = [0.9965, 0.9967, 0.8921, 0.6914, 0.6975]
    
    fig, ax = plt.subplots(figsize=(3.5, 2.5))
    x = np.arange(len(models))
    ax.bar(x, f1, color='white', edgecolor='black', hatch='//')
    
    ax.set_ylabel('F1-Score')
    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=45, ha='right')
    ax.set_ylim(0, 1.1)
    ax.grid(axis='y', linestyle='--', linewidth=0.5, color='gray', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig('writing/figures/metric_comparison.pdf')
    plt.close()

def plot_loss(json_path, output_path, title):
    data = json.load(open(json_path))
    fig, ax = plt.subplots(figsize=(3.5, 2.5))
    ax.plot(data.get('train_loss', []), label='Train Loss', linestyle='-')
    ax.plot(data.get('val_loss', []), label='Val Loss', linestyle='--')
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Loss')
    ax.set_title(title)
    ax.legend()
    ax.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

if __name__ == "__main__":
    plot_metric_comparison()
    plot_loss('experiments/autoencoder/results.json', 'writing/figures/ae_loss.pdf', 'AE Training Loss')
    plot_loss('experiments/vae/results.json', 'writing/figures/vae_loss.pdf', 'VAE Training Loss')
    print("Figures generated successfully in writing/figures/")

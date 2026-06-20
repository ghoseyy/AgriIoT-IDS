# Phase 1 Baseline Run

## Configuration

- model: autoencoder
- latent_dim: 16
- hidden_dims: [128, 64]
- epochs: 2
- batch_size: 2048
- learning_rate: 0.001
- device: cpu
- train_samples_used: 100000
- val_samples_used: 50000
- test_samples_used: 50000

## Validation Metrics

- threshold: 0.047463
- precision: 0.535426
- recall: 0.996967
- f1: 0.696691
- roc_auc: 0.799873
- pr_auc: 0.728693

## Test Metrics

- threshold: 0.047463
- precision: 0.536134
- recall: 0.997888
- f1: 0.697515
- roc_auc: 0.802295
- pr_auc: 0.728081

## Artifacts

- checkpoint: experiments/autoencoder/model_quick.pt
- metrics_json: experiments/autoencoder/results_quick.json
- loss_plot: experiments/autoencoder/loss_quick.png
- score_plot: experiments/autoencoder/scores_quick.png

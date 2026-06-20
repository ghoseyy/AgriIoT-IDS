# Phase 1 Baseline Run

## Configuration

- model: autoencoder
- latent_dim: 16
- hidden_dims: [128, 64]
- epochs: 20
- batch_size: 512
- learning_rate: 0.001
- device: cpu
- train_samples_used: 1362792
- val_samples_used: 732542
- test_samples_used: 732542

## Validation Metrics

- threshold: 0.003818
- precision: 0.678648
- recall: 0.706057
- f1: 0.692081
- roc_auc: 0.836327
- pr_auc: 0.791736

## Test Metrics

- threshold: 0.003818
- precision: 0.679216
- recall: 0.704202
- f1: 0.691483
- roc_auc: 0.836317
- pr_auc: 0.791428

## Artifacts

- checkpoint: experiments/autoencoder/model.pt
- metrics_json: experiments/autoencoder/results.json
- loss_plot: experiments/autoencoder/loss.png
- score_plot: experiments/autoencoder/scores.png

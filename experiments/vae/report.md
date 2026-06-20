# Phase 1 Baseline Run

## Configuration

- model: vae
- latent_dim: 16
- hidden_dims: [128, 64]
- epochs: 20
- batch_size: 512
- learning_rate: 0.001
- beta: 1.0
- device: cpu
- train_samples_used: 100000
- val_samples_used: 50000
- test_samples_used: 50000

## Validation Metrics

- threshold: 0.092370
- precision: 0.531373
- recall: 0.958272
- f1: 0.683653
- roc_auc: 0.799945
- pr_auc: 0.732446

## Test Metrics

- threshold: 0.092370
- precision: 0.528819
- recall: 0.955129
- f1: 0.680738
- roc_auc: 0.801188
- pr_auc: 0.730044

## Artifacts

- checkpoint: experiments/vae/model.pt
- metrics_json: experiments/vae/results.json
- loss_plot: experiments/vae/loss.png
- score_plot: experiments/vae/scores.png

# Phase 1 Baseline Run

## Configuration

- model: vae
- latent_dim: 16
- hidden_dims: [128, 64]
- epochs: 2
- batch_size: 2048
- learning_rate: 0.001
- beta: 1.0
- device: cpu
- train_samples_used: 100000
- val_samples_used: 50000
- test_samples_used: 50000

## Validation Metrics

- threshold: 0.084680
- precision: 0.477884
- recall: 0.994300
- f1: 0.645517
- roc_auc: 0.717703
- pr_auc: 0.671519

## Test Metrics

- threshold: 0.084680
- precision: 0.476649
- recall: 0.994615
- f1: 0.644456
- roc_auc: 0.721854
- pr_auc: 0.672718

## Artifacts

- checkpoint: experiments/vae/model_quick.pt
- metrics_json: experiments/vae/results_quick.json
- loss_plot: experiments/vae/loss_quick.png
- score_plot: experiments/vae/scores_quick.png

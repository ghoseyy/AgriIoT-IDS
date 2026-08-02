# Phase 1 Baseline Run

## Configuration

- model: autoencoder
- latent_dim: 16
- hidden_dims: [128, 64]
- epochs: 20
- batch_size: 512
- learning_rate: 0.001
- device: cpu
- train_samples_used: 227904
- val_samples_used: 333177
- test_samples_used: 3545

## Validation Metrics

- threshold: 0.004974
- precision: 0.999360
- recall: 0.988885
- f1: 0.994095
- roc_auc: 0.994718
- pr_auc: 0.998904

## Test Metrics

- threshold: 0.004974
- precision: 0.982513
- recall: 0.856578
- f1: 0.915234
- roc_auc: 0.913079
- pr_auc: 0.936409

## Artifacts

- checkpoint: experiments/autoencoder_farmflow/model.pt
- metrics_json: experiments/autoencoder_farmflow/results.json
- loss_plot: experiments/autoencoder_farmflow/loss.png
- score_plot: experiments/autoencoder_farmflow/scores.png

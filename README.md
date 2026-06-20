# AgriIoT-IDS — Intrusion Detection for Agricultural IoT Networks

Code and experiment artifacts for the study **"Intrusion Detection for Agricultural IoT
Networks: An Empirical Comparison of Supervised and Unsupervised Machine Learning
Approaches"** by Hasta Bahadur Chhetri.

This repository is a **code & reproducibility release**. It contains the training/evaluation
pipeline, model definitions, experiment configs, trained model artifacts, and analysis notes.
It does **not** redistribute the CICIDS2017 dataset or any third-party copyrighted papers.

## What's inside

- `src/agri_iot_ids/` — core package: data loading (`data/cicids2017.py`), models
  (`models/autoencoder.py`, `models/vae.py`), training engine, and evaluation.
- `scripts/` — training and utility scripts (sklearn models, autoencoder, VAE, PR-AUC,
  figure generation, dataset preparation).
- `experiments/` — results (`results.json`, reports, loss/score plots) and the small trained
  model artifacts (`*.pt`, `scaler.pkl`).
- `reports/` — experiment summary, literature matrix, and research-gap analysis.
- `notes/` — the author's own summaries of the reviewed literature.

## Getting started

This project uses [`uv`](https://github.com/astral-sh/uv) for package management.

```bash
uv sync                                    # create venv + install deps
bash scripts/download_cicids2017.sh        # fetch CICIDS2017 (not bundled here)
uv run python scripts/prepare_cicids2017.py
uv run python scripts/train_sklearn.py     # Random Forest / Decision Tree / Logistic Regression
uv run python scripts/train_autoencoder.py # unsupervised autoencoder
uv run python scripts/train_vae.py         # variational autoencoder
```

## Dataset

Experiments use the **CICIDS2017** benchmark, distributed by the Canadian Institute for
Cybersecurity, and it is **not** included in this repository. Use the scripts in `scripts/`
to download and prepare it locally (`data/` is git-ignored).

## Headline results (CICIDS2017)

| Model | F1 | ROC-AUC |
|---|---|---|
| Random Forest | 0.9965 | 0.9998 |
| Decision Tree | 0.9967 | 0.9976 |
| Logistic Regression | 0.8921 | — |
| Autoencoder (quick) | 0.6975 | — |
| VAE (quick) | 0.6444 | — |

Supervised ensembles strongly outperform unsupervised detectors on labeled attacks, while
autoencoders offer high-recall zero-day anomaly detection — motivating a two-tier hybrid IDS
for resource-constrained smart farms.

## License

Code is released for academic and research use. Third-party papers and the CICIDS2017 dataset
remain under their respective licenses and are not redistributed here.

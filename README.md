# AgriIoT-IDS — Intrusion Detection and Recovery for Agricultural IoT Networks

Code and experiment artifacts for the study **"Beyond Detection: Testing the Assumptions
Behind Intrusion Recovery for Resource-Constrained Agricultural IoT"** by Hasta Bahadur
Chhetri.

This repository is a **code & reproducibility release**. It contains the training/evaluation
pipeline, model definitions, experiment configs, trained model artifacts, and analysis notes.
It does **not** redistribute the CICIDS2017 or Farm-flow datasets, nor any third-party
copyrighted papers.

## What's inside

- `src/agri_iot_ids/` — core package: data loading (`data/cicids2017.py`), models
  (`models/autoencoder.py`, `models/vae.py`), training engine, evaluation, and the
  Q-learning recovery agent (`recovery/`).
- `scripts/` — training and utility scripts (sklearn models, autoencoder, VAE, PR-AUC,
  figure generation, dataset preparation, hybrid ablation, rigor analysis, resource
  footprint, training-energy measurement, Farm-flow preparation).
- `experiments/` — results (`results.json`, reports, loss/score plots) and the small trained
  model artifacts (`*.pt`, `scaler.pkl`) for the baseline, recovery, hybrid-ablation,
  Farm-flow, rigor, resource-footprint, and training-energy experiments.
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
uv run python scripts/run_recovery_experiment.py  # Q-learning recovery agent
```

Additional experiments (run from the project root):

```bash
uv run python scripts/hybrid_ablation.py               # Tier 1 vs Tier 1+2 + grounded-confidence recovery
uv run python scripts/rigor_analysis.py                # multi-seed, McNemar, sensitivity, feature importance
uv run python scripts/measure_resource_footprint.py    # model sizes + INT8 quantization
uv run python scripts/measure_training_energy.py       # codecarbon training-energy measurement
uv run python scripts/download_prepare_farmflow.py     # fetch Farm-flow (agri-IoT dataset, ~500 MB)
uv run python scripts/prepare_farmflow.py              # prepare Farm-flow splits
```

## Datasets

Experiments use the **CICIDS2017** benchmark, distributed by the Canadian Institute for
Cybersecurity, and the **Farm-flow** smart-agriculture flow dataset (Ferreira et al., 2025,
Zenodo). Neither is included in this repository; use the scripts in `scripts/` to download
and prepare them locally (`data/` is git-ignored).

## Headline results

| Model (CICIDS2017) | F1 | ROC-AUC |
|---|---|---|
| Random Forest | 0.9965 | 0.9998 |
| Decision Tree | 0.9967 | 0.9976 |
| Logistic Regression | 0.8921 | — |
| Autoencoder (quick) | 0.6975 | — |
| VAE (quick) | 0.6444 | — |

Key findings from the newer experiments:

- **Hybrid ablation:** routing low-confidence Random Forest predictions to an Autoencoder
  lowers the false-positive rate (0.082% → 0.069%, McNemar `p<10^-45`) at a cost of roughly
  seven additional missed attacks per false alarm avoided — a real trade-off, not a clean win.
- **Recovery:** a Q-learning agent cuts mean time to recovery by ~68% and downtime by ~62%
  against a manual-response baseline across a 3x3 compute/connectivity grid, degrading
  gracefully rather than collapsing (77.8% → 44.1% MTTR gain).
- **Cross-dataset:** revalidating four detectors on Farm-flow shows the model ranking
  transfers but CICIDS2017's near-perfect ceiling does not (F1 around 0.92), and the sharp
  supervised/unsupervised gap largely closes.
- **Resource footprint:** INT8 quantization shrinks the Autoencoder and VAE by roughly 70%
  with no retraining.

## License

Code is released for academic and research use. Third-party papers, the CICIDS2017 and
Farm-flow datasets, and the manuscript remain under their respective licenses and are not
redistributed here.

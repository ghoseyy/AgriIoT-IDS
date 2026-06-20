
# AgriIoT-IDS Research Project — Agent Context

## Project Overview
Hybrid Quantum-Classical Intrusion Detection System for Precision Agriculture IoT networks. Iterative research roadmap from classical baselines through quantum-enhanced multi-agent frameworks.

## Research Roadmap (Phases 0–5)

### Phase 0 — Project Scaffolding
- [x] Define iterative roadmap
- [x] Create project structure (data/, experiments/, papers/, scripts/, writing/, zotero/)
- [x] Organize papers into topical directories
- [x] Create .gitignore
- [x] Create AGENTS.md (this file)
- [x] Pin Python dependencies in requirements.txt

### Phase 1 — Classical Baselines (AE + VAE)
- [x] Source CIC-IDS-2017 dataset → data/CICIDS2017/
- [x] Build preprocessing pipeline (normalization, train/val/test split)
- [x] Implement Autoencoder anomaly detector (PyTorch)
- [x] Implement Variational Autoencoder anomaly detector (PyTorch)
- [x] Bayesian hyperparameter optimization (Optuna)
- [x] Evaluate: precision, recall, F1, ROC-AUC, PR-AUC
- [x] Document classical baseline results

### Phase 2 — Quantum Autoencoder (QAE)
- [ ] Replace AE latent layer with PennyLane quantum circuit (default.qubit)
- [ ] Benchmark QAE vs classical AE/VAE on same metrics
- [ ] Bayesian optimization for quantum circuit hyperparameters
- [ ] Integrate SHAP explainability (local + global feature importance)
- [ ] Document quantum vs classical comparison

### Phase 3 — Graph-based Feature Correlation (GNN)
- [ ] Design graph representation of IoT network traffic
- [ ] Implement GNN (GCN/GAT) for feature correlation learning
- [ ] Integrate with QAE as hybrid GNN-QAE detector
- [ ] Benchmark vs Phase 2 results

### Phase 4 — Multi-Agent Hybrid Framework + Semi-Supervised Learning
- [ ] Design multi-agent architecture (specialized detector agents)
- [ ] Implement semi-supervised learning to handle label sparsity
- [ ] Agent coordination and ensemble voting mechanism
- [ ] Benchmark against all prior phases

### Phase 5 — Real-World Validation & Paper Writing
- [ ] Validate on IoT-23 and N-BaIoT datasets
- [ ] Cross-dataset generalization study
- [ ] Ablation studies (each component removal)
- [ ] Write and submit research paper

## Tech Stack
- **Classical ML**: PyTorch, scikit-learn
- **Quantum simulation**: PennyLane (default.qubit)
- **Hardware quantum**: Qiskit (deferred to later phases)
- **Hyperparameter optimization**: Optuna (Bayesian)
- **Explainability**: SHAP
- **Visualization**: matplotlib, seaborn
- **Experiment tracking**: Manual (CSV/JSON logs in experiments/)

## Key Design Decisions
1. Autoencoder + VAE as classical baseline before introducing quantum layers
2. Bayesian Optimization (Optuna) preferred over grid search
3. SHAP for explainability (local + global)
4. PennyLane for quantum circuit simulation; Qiskit reserved for hardware runs
5. Semi-supervised approach for Phase 4 (label sparsity in real-world Agri-IoT)
6. CIC-IDS-2017 as primary dataset; IoT-23 and N-BaIoT for cross-dataset validation

## Project Structure
```
AgriIoT-IDS-Research/
├── data/                  # Dataset files (not committed)
│   ├── CICIDS2017/
│   ├── IoT-23/
│   └── N-BaIoT/
├── experiments/           # Experiment logs, results, checkpoints
├── papers/                # Reference PDFs (organized by topic)
├── scripts/               # Utility scripts
│   ├── organize_papers.py
│   ├── fix_zotero.py
│   ├── prepare_cicids2017.py
│   ├── train_autoencoder.py
│   ├── train_vae.py
│   ├── optimize_autoencoder.py
│   └── optimize_vae.py
├── src/                   # Research code package
├── writing/               # Paper drafts, notes
├── zotero/                # Zotero bibliography
│   └── AgriIoT-IDS-Research.bib
├── AGENTS.md              # This file
└── .gitignore
```

## Collaboration
- GitHub for version control (issues, PRs)
- English-language project
- Research-grade code (not production); prioritize clarity and reproducibility

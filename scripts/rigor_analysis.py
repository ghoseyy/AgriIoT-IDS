"""Statistical rigor pass: multi-seed variance for the model comparison and
hybrid ablation, a McNemar significance test on Tier1 vs Tier1+2, a
confidence-band sensitivity sweep, Random Forest feature importance, and a
confusion matrix -- all from real re-runs of the existing pipeline, no
invented numbers.

Usage:
    uv run python scripts/rigor_analysis.py
"""
from __future__ import annotations

import argparse
import json
import statistics as st
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

SEEDS = [42, 0, 1, 7, 123]
BAND_SWEEP = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30]
PRIMARY_SEED = 42


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepared-dir", type=Path, default=Path("experiments/preprocessing/cicids2017"))
    parser.add_argument("--ae-checkpoint", type=Path, default=Path("experiments/autoencoder/model.pt"))
    parser.add_argument("--ae-results", type=Path, default=Path("experiments/autoencoder/results.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("experiments/rigor_analysis"))
    return parser.parse_args()


def build_supervised_set(prepared, seed):
    import numpy as np
    rng = np.random.default_rng(seed)
    X_val, y_val = prepared.x_val, prepared.y_val
    X_attack = X_val[y_val == 1]
    y_attack = np.ones(len(X_attack), dtype=int)
    n_normal = min(len(prepared.x_train), len(X_attack) * 3)
    idx_normal = rng.choice(len(prepared.x_train), size=n_normal, replace=False)
    X_train = np.concatenate([prepared.x_train[idx_normal], X_attack], axis=0)
    y_train = np.concatenate([np.zeros(n_normal, dtype=int), y_attack], axis=0)
    shuffle_idx = rng.permutation(len(X_train))
    return X_train[shuffle_idx], y_train[shuffle_idx]


def metrics_for(y_true, y_pred, y_proba):
    from sklearn.metrics import (
        precision_score, recall_score, f1_score, roc_auc_score,
        average_precision_score, confusion_matrix,
    )
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    return {
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, y_proba)),
        "pr_auc": float(average_precision_score(y_true, y_proba)),
        "false_positive_rate": float(fpr),
    }


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    try:
        import numpy as np
        import torch
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.tree import DecisionTreeClassifier
        from sklearn.linear_model import LogisticRegression
        from agri_iot_ids.data.cicids2017 import load_prepared_data
        from agri_iot_ids.models.autoencoder import Autoencoder
        from agri_iot_ids.training.engine import score_autoencoder
    except ModuleNotFoundError as exc:
        raise SystemExit(f"Missing dependency: {exc}. Run `uv sync` first.") from exc

    prepared = load_prepared_data(args.prepared_dir)
    X_test, y_test = prepared.x_test, prepared.y_test

    ae_config = json.loads(args.ae_results.read_text())["config"]
    ae_threshold = json.loads(args.ae_results.read_text())["test_metrics"]["threshold"]
    ae = Autoencoder(input_dim=prepared.input_dim, latent_dim=ae_config["latent_dim"], hidden_dims=ae_config["hidden_dims"])
    ae.load_state_dict(torch.load(args.ae_checkpoint, map_location="cpu"))
    ae_scores_test = score_autoencoder(ae, X_test, device="cpu")
    ae_pseudo_conf = np.clip(0.5 + 0.5 * (ae_scores_test - ae_threshold) / (ae_threshold + 1e-9), 0.0, 1.0)
    ae_pred_all = (ae_scores_test >= ae_threshold).astype(int)

    # ---- 1. Multi-seed model comparison + hybrid ablation ----
    print("=" * 60)
    print(f"MULTI-SEED RUNS ({len(SEEDS)} seeds: {SEEDS})")
    print("=" * 60)

    per_seed_model_metrics = {"Random Forest": [], "Decision Tree": [], "Logistic Regression": []}
    per_seed_hybrid_metrics = {"tier1": [], "tier1_plus_2": []}
    primary_seed_rf = None
    primary_seed_rf_proba = None
    primary_seed_rf_pred = None

    for seed in SEEDS:
        X_train, y_train = build_supervised_set(prepared, seed)

        models = [
            ("Random Forest", RandomForestClassifier(n_estimators=100, max_depth=20, n_jobs=-1, random_state=seed)),
            ("Decision Tree", DecisionTreeClassifier(max_depth=20, random_state=seed)),
            ("Logistic Regression", LogisticRegression(max_iter=1000, n_jobs=-1, random_state=seed)),
        ]
        rf_model = None
        for name, model in models:
            model.fit(X_train, y_train)
            proba = model.predict_proba(X_test)[:, 1]
            pred = (proba >= 0.5).astype(int)
            m = metrics_for(y_test, pred, proba)
            per_seed_model_metrics[name].append(m)
            if name == "Random Forest":
                rf_model = model

        rf_proba = rf_model.predict_proba(X_test)[:, 1]
        rf_pred = (rf_proba >= 0.5).astype(int)
        tier1_m = metrics_for(y_test, rf_pred, rf_proba)
        per_seed_hybrid_metrics["tier1"].append(tier1_m)

        low_conf_band = (rf_proba >= 0.35) & (rf_proba <= 0.65)
        combined_pred = rf_pred.copy()
        combined_proba = rf_proba.copy()
        combined_pred[low_conf_band] = ae_pred_all[low_conf_band]
        combined_proba[low_conf_band] = ae_pseudo_conf[low_conf_band]
        tier12_m = metrics_for(y_test, combined_pred, combined_proba)
        per_seed_hybrid_metrics["tier1_plus_2"].append(tier12_m)

        print(f"seed={seed}: RF F1={tier1_m['f1']:.4f} FPR={tier1_m['false_positive_rate']:.5f} | "
              f"Tier1+2 F1={tier12_m['f1']:.4f} FPR={tier12_m['false_positive_rate']:.5f}")

        if seed == PRIMARY_SEED:
            primary_seed_rf = rf_model
            primary_seed_rf_proba = rf_proba
            primary_seed_rf_pred = rf_pred
            primary_seed_combined_pred = combined_pred

    def summarize(metric_list, key):
        vals = [m[key] for m in metric_list]
        return {"mean": st.mean(vals), "std": st.pstdev(vals), "values": vals}

    model_summary = {}
    for name, metric_list in per_seed_model_metrics.items():
        model_summary[name] = {k: summarize(metric_list, k) for k in ["f1", "recall", "precision", "roc_auc", "pr_auc"]}

    hybrid_summary = {}
    for tier, metric_list in per_seed_hybrid_metrics.items():
        hybrid_summary[tier] = {k: summarize(metric_list, k) for k in ["f1", "recall", "precision", "false_positive_rate"]}

    # ---- 2. McNemar's test: Tier1 (RF) vs Tier1+2, primary seed ----
    print("\n" + "=" * 60)
    print("MCNEMAR'S TEST: Tier 1 (RF) vs Tier 1+2 (RF+AE), seed=42")
    print("=" * 60)
    from scipy.stats import binomtest

    rf_correct = (primary_seed_rf_pred == y_test)
    hybrid_correct = (primary_seed_combined_pred == y_test)
    n01 = int(np.sum(~rf_correct & hybrid_correct))   # RF wrong, hybrid right
    n10 = int(np.sum(rf_correct & ~hybrid_correct))   # RF right, hybrid wrong
    n_discordant = n01 + n10
    if n_discordant > 0:
        mcnemar_result = binomtest(min(n01, n10), n_discordant, p=0.5, alternative="two-sided")
        mcnemar_p = mcnemar_result.pvalue
    else:
        mcnemar_p = 1.0
    print(f"Discordant pairs: RF-wrong/Hybrid-right={n01}, RF-right/Hybrid-wrong={n10}")
    print(f"McNemar exact binomial test p-value: {mcnemar_p:.6f}")

    # ---- 3. Confidence-band sensitivity sweep, primary seed ----
    print("\n" + "=" * 60)
    print("CONFIDENCE-BAND SENSITIVITY SWEEP, seed=42")
    print("=" * 60)
    band_sweep_results = []
    for band in BAND_SWEEP:
        low_conf = (primary_seed_rf_proba >= 0.5 - band) & (primary_seed_rf_proba <= 0.5 + band)
        pred = primary_seed_rf_pred.copy()
        proba = primary_seed_rf_proba.copy()
        pred[low_conf] = ae_pred_all[low_conf]
        proba[low_conf] = ae_pseudo_conf[low_conf]
        m = metrics_for(y_test, pred, proba)
        m["band"] = band
        m["pct_routed_to_ae"] = float(low_conf.mean() * 100)
        band_sweep_results.append(m)
        print(f"band=±{band:.2f}: routed={m['pct_routed_to_ae']:.2f}% F1={m['f1']:.4f} "
              f"Recall={m['recall']:.4f} FPR={m['false_positive_rate']:.5f}")

    # ---- 4. Feature importance, primary seed RF ----
    print("\n" + "=" * 60)
    print("TOP 15 FEATURE IMPORTANCES (Random Forest, seed=42)")
    print("=" * 60)
    importances = primary_seed_rf.feature_importances_
    feature_names = prepared.feature_names
    order = np.argsort(importances)[::-1][:15]
    top_features = [{"feature": feature_names[i], "importance": float(importances[i])} for i in order]
    for row in top_features:
        print(f"{row['feature']}: {row['importance']:.4f}")

    # ---- 5. Confusion matrix, primary seed, Tier1 and Tier1+2 ----
    from sklearn.metrics import confusion_matrix
    cm_tier1 = confusion_matrix(y_test, primary_seed_rf_pred, labels=[0, 1]).tolist()
    cm_tier12 = confusion_matrix(y_test, primary_seed_combined_pred, labels=[0, 1]).tolist()

    summary = {
        "seeds": SEEDS,
        "model_comparison_multiseed": model_summary,
        "hybrid_ablation_multiseed": hybrid_summary,
        "mcnemar_test": {
            "n01_rf_wrong_hybrid_right": n01,
            "n10_rf_right_hybrid_wrong": n10,
            "p_value": float(mcnemar_p),
            "significant_at_0.05": bool(mcnemar_p < 0.05),
        },
        "confidence_band_sweep": band_sweep_results,
        "top_feature_importances": top_features,
        "confusion_matrix_tier1": {"labels": ["benign", "attack"], "matrix": cm_tier1},
        "confusion_matrix_tier1_plus_2": {"labels": ["benign", "attack"], "matrix": cm_tier12},
    }
    (args.output_dir / "results.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(f"\nSaved full results to {args.output_dir / 'results.json'}")


if __name__ == "__main__":
    main()

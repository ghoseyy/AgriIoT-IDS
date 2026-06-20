from __future__ import annotations
import argparse
import json
import time
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

def parse_args():
    parser = argparse.ArgumentParser(description="Train traditional ML models on CIC-IDS-2017.")
    parser.add_argument("--prepared-dir", type=Path, default=Path("experiments/preprocessing/cicids2017"))
    parser.add_argument("--output-dir", type=Path, default=Path("experiments/sklearn"))
    parser.add_argument("--max-train-samples", type=int, default=None)
    parser.add_argument("--max-eval-samples", type=int, default=None)
    parser.add_argument("--random-state", type=int, default=42)
    return parser.parse_args()

def load_data(prepared_dir, max_train, max_eval, random_state):
    import numpy as np
    print(f"Loading data from {prepared_dir}...")
    splits = np.load(prepared_dir / "splits.npz")
    print(f"  Available keys: {list(splits.keys())}")

    # Keys are lowercase; no y_train (autoencoder was unsupervised)
    X_train_normal = splits["x_train"]
    X_val  = splits["x_val"]
    y_val  = splits["y_val"]
    X_test = splits["x_test"]
    y_test = splits["y_test"]

    # Build supervised training set from normal + attack samples
    X_attack = X_val[y_val == 1]
    y_attack = np.ones(len(X_attack), dtype=int)

    # 3:1 normal to attack ratio
    n_normal = min(len(X_train_normal), len(X_attack) * 3)
    rng = np.random.default_rng(random_state)
    idx_normal = rng.choice(len(X_train_normal), size=n_normal, replace=False)
    X_normal = X_train_normal[idx_normal]
    y_normal = np.zeros(n_normal, dtype=int)

    X_train = np.concatenate([X_normal, X_attack], axis=0)
    y_train = np.concatenate([y_normal, y_attack], axis=0)

    # Shuffle
    shuffle_idx = rng.permutation(len(X_train))
    X_train = X_train[shuffle_idx]
    y_train = y_train[shuffle_idx]

    print(f"  Built supervised train: {len(X_train)} samples "
          f"({n_normal} normal, {len(X_attack)} attack)")

    if max_train is not None and len(X_train) > max_train:
        idx = rng.choice(len(X_train), size=max_train, replace=False)
        X_train = X_train[idx]
        y_train = y_train[idx]
        print(f"  Capped train to {max_train} samples")

    if max_eval is not None:
        if len(X_val) > max_eval:
            idx = rng.choice(len(X_val), size=max_eval, replace=False)
            X_val  = X_val[idx]
            y_val  = y_val[idx]
        if len(X_test) > max_eval:
            idx = rng.choice(len(X_test), size=max_eval, replace=False)
            X_test = X_test[idx]
            y_test = y_test[idx]
        print(f"  Capped eval to {max_eval} samples")

    print(f"  Train: {X_train.shape}, Val: {X_val.shape}, Test: {X_test.shape}")
    print(f"  Train attack rate: {y_train.mean():.3f}")
    print(f"  Val  attack rate:  {y_val.mean():.3f}")
    print(f"  Test attack rate:  {y_test.mean():.3f}")

    return X_train, y_train, X_val, y_val, X_test, y_test

def compute_metrics(y_true, y_pred, y_proba=None):
    from sklearn.metrics import (
        precision_score, recall_score, f1_score,
        roc_auc_score, average_precision_score
    )
    metrics = {
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall":    float(recall_score(y_true, y_pred, zero_division=0)),
        "f1":        float(f1_score(y_true, y_pred, zero_division=0)),
    }
    if y_proba is not None:
        try:
            metrics["roc_auc"] = float(roc_auc_score(y_true, y_proba))
            metrics["pr_auc"]  = float(average_precision_score(y_true, y_proba))
        except Exception:
            metrics["roc_auc"] = None
            metrics["pr_auc"]  = None
    return metrics

def train_and_evaluate(name, model, X_train, y_train, X_val, y_val, X_test, y_test):
    print(f"\n{'='*50}")
    print(f"Training: {name}")
    print(f"{'='*50}")

    t0 = time.time()
    model.fit(X_train, y_train)
    train_time = time.time() - t0
    print(f"  Training time: {train_time:.1f}s")

    has_proba = hasattr(model, "predict_proba")

    val_pred  = model.predict(X_val)
    val_proba = model.predict_proba(X_val)[:, 1] if has_proba else None
    val_metrics = compute_metrics(y_val, val_pred, val_proba)
    print(f"  Val  — F1: {val_metrics['f1']:.4f} | "
          f"ROC-AUC: {val_metrics.get('roc_auc') or 'N/A'}")

    test_pred  = model.predict(X_test)
    test_proba = model.predict_proba(X_test)[:, 1] if has_proba else None
    test_metrics = compute_metrics(y_test, test_pred, test_proba)
    print(f"  Test — F1: {test_metrics['f1']:.4f} | "
          f"ROC-AUC: {test_metrics.get('roc_auc') or 'N/A'}")

    return {
        "model": name,
        "train_time_seconds": round(train_time, 2),
        "validation_metrics": val_metrics,
        "test_metrics": test_metrics
    }

def save_report(results, output_dir):
    lines = [
        "# Traditional ML Models — Results Comparison",
        "",
        "## Test Metrics",
        "",
        "| Model | F1 | ROC-AUC | PR-AUC | Precision | Recall | Train Time |",
        "|-------|----|---------|--------|-----------|--------|------------|",
    ]
    for r in results:
        m = r["test_metrics"]
        roc = "N/A" if m.get("roc_auc") is None else f"{m['roc_auc']:.4f}"
        pr  = "N/A" if m.get("pr_auc")  is None else f"{m['pr_auc']:.4f}"
        lines.append(
            f"| {r['model']} | {m['f1']:.4f} | {roc} | {pr} "
            f"| {m['precision']:.4f} | {m['recall']:.4f} | {r['train_time_seconds']}s |"
        )
    lines += ["", "## Notes", "- Dataset: CIC-IDS-2017", "- Supervised training"]
    path = output_dir / "comparison_report.md"
    path.write_text("\n".join(lines))
    print(f"\nSaved report to {path}")

def main():
    args = parse_args()

    try:
        import numpy as np
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.tree import DecisionTreeClassifier
        from sklearn.linear_model import LogisticRegression
        from sklearn.svm import SVC
    except ModuleNotFoundError as exc:
        raise SystemExit(f"Missing dependency: {exc}") from exc

    args.output_dir.mkdir(parents=True, exist_ok=True)

    X_train, y_train, X_val, y_val, X_test, y_test = load_data(
        args.prepared_dir,
        args.max_train_samples,
        args.max_eval_samples,
        args.random_state
    )

    models = [
        ("Random Forest", RandomForestClassifier(
            n_estimators=100, max_depth=20, n_jobs=-1,
            random_state=args.random_state)),
        ("Decision Tree", DecisionTreeClassifier(
            max_depth=20, random_state=args.random_state)),
        ("Logistic Regression", LogisticRegression(
            max_iter=1000, n_jobs=-1, random_state=args.random_state)),
    ]

    if len(X_train) <= 50000:
        models.append(("SVM", SVC(
            kernel="rbf", probability=True, random_state=args.random_state)))
        print("SVM included")
    else:
        print(f"SVM skipped (train size {len(X_train)} too large)")

    all_results = []
    for name, model in models:
        result = train_and_evaluate(
            name, model,
            X_train, y_train,
            X_val, y_val,
            X_test, y_test
        )
        all_results.append(result)

    results_path = args.output_dir / "results.json"
    with open(results_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nSaved results to {results_path}")

    save_report(all_results, args.output_dir)

    print("\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)
    print(f"{'Model':<25} {'F1':>8} {'ROC-AUC':>10} {'Precision':>10} {'Recall':>8}")
    print("-"*60)
    for r in all_results:
        m = r["test_metrics"]
        roc = f"{m['roc_auc']:.4f}" if m.get("roc_auc") else "N/A"
        print(f"{r['model']:<25} {m['f1']:>8.4f} {roc:>10} "
              f"{m['precision']:>10.4f} {m['recall']:>8.4f}")

if __name__ == "__main__":
    main()
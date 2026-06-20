"""
compute_prauc.py
Computes PR-AUC for RF, DT, and Logistic Regression,
then patches experiments/sklearn/results.json with the values.

Run from project root:
    uv run scripts/compute_prauc.py
"""

import json
import pathlib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA_PATH    = PROJECT_ROOT / "experiments" / "preprocessing" / "cicids2017" / "splits.npz"
RESULTS_PATH = PROJECT_ROOT / "experiments" / "sklearn" / "results.json"

# ── Load data ────────────────────────────────────────────────────────────────
print("Loading splits.npz ...")
data   = np.load(DATA_PATH)
x_train_normal = data["x_train"]
x_val          = data["x_val"]
y_val          = data["y_val"].astype(int)
X_test         = data["x_test"]
y_test         = data["y_test"].astype(int)

print(f"  x_train (normal) : {x_train_normal.shape}")
print(f"  x_test           : {X_test.shape}")
print(f"  test attack rate : {y_test.mean():.3f}")

# ── Build labelled training set (same strategy as train_sklearn.py) ──────────
attack_mask     = y_val == 1
x_attacks       = x_val[attack_mask]
x_normal_subset = x_train_normal[:len(x_attacks) * 3]  # 3:1 normal:attack ratio

X_train = np.vstack([x_normal_subset, x_attacks])
y_train = np.hstack([
    np.zeros(len(x_normal_subset), dtype=int),
    np.ones(len(x_attacks),        dtype=int),
])
print(f"  Training set     : {X_train.shape}  (normal={len(x_normal_subset)}, attacks={len(x_attacks)})")

# ── Models ───────────────────────────────────────────────────────────────────
models = {
    "random_forest":       RandomForestClassifier(n_estimators=100, n_jobs=-1, random_state=42),
    "decision_tree":       DecisionTreeClassifier(random_state=42),
    "logistic_regression": LogisticRegression(max_iter=1000, n_jobs=-1, random_state=42),
}

prauc_results = {}

for name, model in models.items():
    print(f"\nTraining {name} ...")
    model.fit(X_train, y_train)

    # Get probability scores for the positive class
    if hasattr(model, "predict_proba"):
        y_scores = model.predict_proba(X_test)[:, 1]
    else:
        y_scores = model.decision_function(X_test)

    prauc = average_precision_score(y_test, y_scores)
    prauc_results[name] = round(float(prauc), 4)
    print(f"  PR-AUC = {prauc:.4f}")

# ── Patch results.json ───────────────────────────────────────────────────────
print(f"\nPatching {RESULTS_PATH} ...")
with open(RESULTS_PATH) as f:
    results = json.load(f)

print("  Existing keys:", list(results.keys()))

# Handles both flat dict and nested dict structures
for model_key, prauc_val in prauc_results.items():
    if model_key in results:
        results[model_key]["pr_auc"] = prauc_val
        print(f"  Patched [{model_key}][pr_auc] = {prauc_val}")
    else:
        print(f"  WARNING: key '{model_key}' not found in results.json — skipping patch")
        print(f"           Available keys: {list(results.keys())}")

with open(RESULTS_PATH, "w") as f:
    json.dump(results, f, indent=2)

print("\nDone. Updated results.json:")
print(json.dumps(results, indent=2))
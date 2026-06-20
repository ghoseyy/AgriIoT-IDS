"""
compute_prauc_v2.py
Patches experiments/sklearn/results.json (list structure) with PR-AUC values.
PR-AUC already computed:
  random_forest       = 0.9992
  decision_tree       = 0.9972
  logistic_regression = 0.9697

Run from project root:
    uv run scripts/compute_prauc_v2.py
"""

import json
import pathlib

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
RESULTS_PATH = PROJECT_ROOT / "experiments" / "sklearn" / "results.json"

PRAUC_VALUES = {
    "random_forest":       0.9992,
    "decision_tree":       0.9972,
    "logistic_regression": 0.9697,
}

# Key aliases in case the list entries use different name formats
NAME_ALIASES = {
    "random forest":       "random_forest",
    "randomforest":        "random_forest",
    "decision tree":       "decision_tree",
    "decisiontree":        "decision_tree",
    "logistic regression": "logistic_regression",
    "logisticregression":  "logistic_regression",
}

with open(RESULTS_PATH) as f:
    results = json.load(f)

print("results.json structure (list of dicts):")
for i, entry in enumerate(results):
    print(f"  [{i}] keys: {list(entry.keys())}")
    # Print the name/model field if it exists
    for k in ("model", "name", "classifier", "algorithm"):
        if k in entry:
            print(f"       {k} = {entry[k]}")

print("\nPatching ...")
patched = 0
for entry in results:
    # Find the name field
    raw_name = None
    for k in ("model", "name", "classifier", "algorithm"):
        if k in entry:
            raw_name = str(entry[k]).lower().strip()
            break

    if raw_name is None:
        continue

    # Normalize name
    canonical = NAME_ALIASES.get(raw_name, raw_name.replace(" ", "_"))

    if canonical in PRAUC_VALUES:
        entry["pr_auc"] = PRAUC_VALUES[canonical]
        print(f"  Patched '{raw_name}' -> pr_auc = {PRAUC_VALUES[canonical]}")
        patched += 1

if patched == 0:
    print("  No entries matched. Printing full results.json for inspection:")
    print(json.dumps(results, indent=2))
else:
    with open(RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved. Patched {patched} entries.")
    print("\nFinal results.json:")
    print(json.dumps(results, indent=2))
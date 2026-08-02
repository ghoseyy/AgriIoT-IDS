"""Three-tier hybrid IDS ablation: Tier 1 (Random Forest) -> Tier 2
(Autoencoder fallback on low-confidence RF cases) -> Tier 3 (recovery agent,
using detector-confidence parameters empirically measured from Tier 1+2
instead of the placeholder Gaussian(0.9, 0.08) previously assumed).

This directly answers the "you proposed a hybrid architecture but never
tested it end-to-end" critique: it actually runs the tiers together and
reports Tier1-alone vs Tier1+2 vs Tier1+2+3 metrics on the same data.

Usage (on CICIDS2017, the default):
    uv run python scripts/hybrid_ablation.py

Usage (on Farm-flow, after running download_prepare_farmflow.py):
    uv run python scripts/hybrid_ablation.py \\
        --prepared-dir experiments/preprocessing/farmflow \\
        --ae-checkpoint experiments/autoencoder_farmflow/model.pt \\
        --ae-results experiments/autoencoder_farmflow/results.json \\
        --output-dir experiments/hybrid_ablation_farmflow

Note: Tier 2 requires an Autoencoder already trained on the SAME feature
space as --prepared-dir (same input_dim). If you haven't trained one for
Farm-flow yet, run scripts/train_autoencoder.py --prepared-dir <farmflow dir>
first.
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

CONNECTIVITY_SETTINGS = [1.0, 0.7, 0.4]
COMPUTE_SETTINGS = [3, 2, 1]
ATTACK_START = 5
MAX_STEPS = 100


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run and ablate the three-tier hybrid IDS.")
    parser.add_argument("--prepared-dir", type=Path, default=Path("experiments/preprocessing/cicids2017"))
    parser.add_argument("--ae-checkpoint", type=Path, default=Path("experiments/autoencoder/model.pt"))
    parser.add_argument("--ae-results", type=Path, default=Path("experiments/autoencoder/results.json"))
    parser.add_argument(
        "--confidence-band", type=float, default=0.15,
        help="RF predict_proba within [0.5-band, 0.5+band] is treated as 'low confidence' and "
             "deferred to Tier 2 (the Autoencoder). Default 0.15 => band is [0.35, 0.65].",
    )
    parser.add_argument("--recovery-train-episodes", type=int, default=4000)
    parser.add_argument("--recovery-eval-episodes", type=int, default=300)
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument("--output-dir", type=Path, default=Path("experiments/hybrid_ablation"))
    return parser.parse_args()


def load_ae_hidden_dims(ae_results_path: Path) -> tuple[int, list[int]]:
    payload = json.loads(ae_results_path.read_text())
    return payload["config"]["latent_dim"], payload["config"]["hidden_dims"]


def run_episode(env, policy, training=False):
    obs = env.reset()
    policy.reset()
    while True:
        prev_state = env.device_state
        action = policy.act(obs)
        next_obs, done = env.step(action)
        if training:
            from agri_iot_ids.recovery.agent import reward_for
            policy.update(obs, action, reward_for(env.device_state, prev_state), next_obs, done)
        obs = next_obs
        if done:
            break
    ttr = env.time_to_recover if env.time_to_recover is not None else (MAX_STEPS - ATTACK_START)
    return ttr, env.downtime_steps


def train_recovery_agent(env_kwargs, train_episodes, seed):
    from agri_iot_ids.recovery.agent import QLearningPolicy
    from agri_iot_ids.recovery.env import AgriIoTRecoveryEnv

    agent = QLearningPolicy(seed=seed)
    for ep in range(train_episodes):
        conn = CONNECTIVITY_SETTINGS[ep % len(CONNECTIVITY_SETTINGS)]
        comp = COMPUTE_SETTINGS[(ep // len(CONNECTIVITY_SETTINGS)) % len(COMPUTE_SETTINGS)]
        env = AgriIoTRecoveryEnv(
            connectivity_reliability=conn, compute_budget_per_step=comp,
            attack_start=ATTACK_START, max_steps=MAX_STEPS, seed=1000 + ep, **env_kwargs,
        )
        run_episode(env, agent, training=True)
        agent.epsilon = max(0.02, agent.epsilon * 0.999)
    agent.training = False
    return agent


def evaluate_recovery(policy, env_kwargs, conn, comp, n, seed_base=5000):
    from agri_iot_ids.recovery.env import AgriIoTRecoveryEnv
    ttrs, downtimes = [], []
    for i in range(n):
        env = AgriIoTRecoveryEnv(
            connectivity_reliability=conn, compute_budget_per_step=comp,
            attack_start=ATTACK_START, max_steps=MAX_STEPS, seed=seed_base + i, **env_kwargs,
        )
        ttr, dt = run_episode(env, policy, training=False)
        ttrs.append(ttr)
        downtimes.append(dt)
    return st.mean(ttrs), st.mean(downtimes)


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    try:
        import numpy as np
        import torch
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import (
            precision_score, recall_score, f1_score, roc_auc_score,
            average_precision_score, confusion_matrix,
        )
        from agri_iot_ids.data.cicids2017 import load_prepared_data
        from agri_iot_ids.models.autoencoder import Autoencoder
        from agri_iot_ids.training.engine import score_autoencoder
        from agri_iot_ids.recovery.agent import NaiveBaselinePolicy
    except ModuleNotFoundError as exc:
        raise SystemExit(f"Missing dependency: {exc}. Run `uv sync` first.") from exc

    # ---- Load data ----
    prepared = load_prepared_data(args.prepared_dir)
    X_train_normal, X_val, y_val, X_test, y_test = (
        prepared.x_train, prepared.x_val, prepared.y_val, prepared.x_test, prepared.y_test,
    )

    rng = np.random.default_rng(args.random_state)
    X_attack = X_val[y_val == 1]
    y_attack = np.ones(len(X_attack), dtype=int)
    n_normal = min(len(X_train_normal), len(X_attack) * 3)
    idx_normal = rng.choice(len(X_train_normal), size=n_normal, replace=False)
    X_normal = X_train_normal[idx_normal]
    y_normal = np.zeros(n_normal, dtype=int)
    X_train = np.concatenate([X_normal, X_attack], axis=0)
    y_train = np.concatenate([y_normal, y_attack], axis=0)
    shuffle_idx = rng.permutation(len(X_train))
    X_train, y_train = X_train[shuffle_idx], y_train[shuffle_idx]

    def metrics_for(y_true, y_pred, y_proba):
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        return {
            "precision": float(precision_score(y_true, y_pred, zero_division=0)),
            "recall": float(recall_score(y_true, y_pred, zero_division=0)),
            "f1": float(f1_score(y_true, y_pred, zero_division=0)),
            "roc_auc": float(roc_auc_score(y_true, y_proba)),
            "pr_auc": float(average_precision_score(y_true, y_proba)),
            "false_positive_rate": float(fpr),
            "n_test": int(len(y_true)),
        }

    # ---- Tier 1: Random Forest ----
    print("=" * 60)
    print("TIER 1: Random Forest (detection)")
    print("=" * 60)
    rf = RandomForestClassifier(n_estimators=100, max_depth=20, n_jobs=-1, random_state=args.random_state)
    rf.fit(X_train, y_train)
    rf_proba = rf.predict_proba(X_test)[:, 1]
    rf_pred = (rf_proba >= 0.5).astype(int)
    tier1_metrics = metrics_for(y_test, rf_pred, rf_proba)
    print(json.dumps(tier1_metrics, indent=2))

    # ---- Tier 2: Autoencoder fallback on low-confidence RF cases ----
    print("\n" + "=" * 60)
    print("TIER 2: RF + Autoencoder fallback on low-confidence cases")
    print("=" * 60)
    if not args.ae_checkpoint.exists():
        raise SystemExit(
            f"AE checkpoint not found at {args.ae_checkpoint}. Train one first with "
            f"scripts/train_autoencoder.py --prepared-dir {args.prepared_dir} (must match this "
            f"dataset's feature space)."
        )
    latent_dim, hidden_dims = load_ae_hidden_dims(args.ae_results)
    ae = Autoencoder(input_dim=prepared.input_dim, latent_dim=latent_dim, hidden_dims=hidden_dims)
    ae.load_state_dict(torch.load(args.ae_checkpoint, map_location="cpu"))
    ae_threshold = json.loads(args.ae_results.read_text())["test_metrics"]["threshold"]

    ae_scores_test = score_autoencoder(ae, X_test, device="cpu")
    # Normalize AE reconstruction error into a pseudo-confidence in [0,1]
    # relative to its own decision threshold, purely for combining with RF's
    # probability scale and for the Tier-3 confidence estimation below.
    ae_pseudo_conf = np.clip(0.5 + 0.5 * (ae_scores_test - ae_threshold) / (ae_threshold + 1e-9), 0.0, 1.0)
    ae_pred_all = (ae_scores_test >= ae_threshold).astype(int)

    low_conf_band = (rf_proba >= 0.5 - args.confidence_band) & (rf_proba <= 0.5 + args.confidence_band)
    print(f"RF low-confidence band [{0.5 - args.confidence_band:.2f}, {0.5 + args.confidence_band:.2f}]: "
          f"{low_conf_band.sum()}/{len(rf_proba)} test samples ({low_conf_band.mean() * 100:.2f}%) deferred to Tier 2")

    combined_pred = rf_pred.copy()
    combined_proba = rf_proba.copy()
    combined_pred[low_conf_band] = ae_pred_all[low_conf_band]
    combined_proba[low_conf_band] = ae_pseudo_conf[low_conf_band]
    tier1_2_metrics = metrics_for(y_test, combined_pred, combined_proba)
    print(json.dumps(tier1_2_metrics, indent=2))

    # ---- Empirically ground Tier 3's detector-confidence assumption ----
    true_positive_mask = (combined_pred == 1) & (y_test == 1)
    true_negative_mask = (combined_pred == 0) & (y_test == 0)
    if true_positive_mask.sum() < 2 or true_negative_mask.sum() < 2:
        raise SystemExit("Not enough true positives/negatives to estimate confidence distribution.")
    conf_active_mean = float(np.mean(combined_proba[true_positive_mask]))
    conf_active_std = float(np.std(combined_proba[true_positive_mask]))
    conf_idle_mean = float(np.mean(combined_proba[true_negative_mask]))
    conf_idle_std = float(np.std(combined_proba[true_negative_mask]))
    print(f"\nEmpirically measured detector-confidence distribution from Tier 1+2:")
    print(f"  active (true positive) conf ~ N({conf_active_mean:.3f}, {conf_active_std:.3f})")
    print(f"  idle   (true negative) conf ~ N({conf_idle_mean:.3f}, {conf_idle_std:.3f})")
    print(f"  (previously assumed, unmeasured: active ~ N(0.9, 0.08), idle ~ N(0.6, 0.2))")

    # ---- Tier 3: recovery agent, grounded confidence vs original assumed confidence ----
    print("\n" + "=" * 60)
    print("TIER 3: Recovery agent, empirically-grounded vs originally-assumed confidence")
    print("=" * 60)
    env_kwargs_grounded = dict(
        conf_active_mean=conf_active_mean, conf_active_std=conf_active_std,
        conf_idle_mean=conf_idle_mean, conf_idle_std=conf_idle_std,
    )
    env_kwargs_original = dict()  # uses env.py defaults (0.9/0.08, 0.6/0.2)

    recovery_rows = []
    for label, env_kwargs in (("grounded", env_kwargs_grounded), ("original_assumed", env_kwargs_original)):
        print(f"\n-- {label} --")
        agent = train_recovery_agent(env_kwargs, args.recovery_train_episodes, seed=0)
        baseline = NaiveBaselinePolicy(response_delay=6)
        for conn in CONNECTIVITY_SETTINGS:
            for comp in COMPUTE_SETTINGS:
                b_ttr, b_dt = evaluate_recovery(baseline, env_kwargs, conn, comp, args.recovery_eval_episodes)
                a_ttr, a_dt = evaluate_recovery(agent, env_kwargs, conn, comp, args.recovery_eval_episodes)
                row = {
                    "confidence_source": label,
                    "connectivity": conn,
                    "compute_budget": comp,
                    "baseline_mttr": b_ttr,
                    "agent_mttr": a_ttr,
                    "mttr_gain_pct": (b_ttr - a_ttr) / b_ttr * 100 if b_ttr else 0.0,
                    "baseline_downtime": b_dt,
                    "agent_downtime": a_dt,
                    "downtime_gain_pct": (b_dt - a_dt) / b_dt * 100 if b_dt else 0.0,
                }
                recovery_rows.append(row)
                print(f"  conn={conn} comp={comp}: MTTR {b_ttr:.2f}->{a_ttr:.2f} ({row['mttr_gain_pct']:.1f}%), "
                      f"downtime {b_dt:.2f}->{a_dt:.2f} ({row['downtime_gain_pct']:.1f}%)")

    grounded_rows = [r for r in recovery_rows if r["confidence_source"] == "grounded"]
    original_rows = [r for r in recovery_rows if r["confidence_source"] == "original_assumed"]

    summary = {
        "prepared_dir": str(args.prepared_dir),
        "confidence_band": args.confidence_band,
        "tier1_rf_only_metrics": tier1_metrics,
        "tier1_plus_tier2_metrics": tier1_2_metrics,
        "empirical_detector_confidence": {
            "conf_active_mean": conf_active_mean, "conf_active_std": conf_active_std,
            "conf_idle_mean": conf_idle_mean, "conf_idle_std": conf_idle_std,
        },
        "recovery_results": recovery_rows,
        "recovery_grounded_overall_mttr_gain_pct": st.mean(r["mttr_gain_pct"] for r in grounded_rows),
        "recovery_grounded_overall_downtime_gain_pct": st.mean(r["downtime_gain_pct"] for r in grounded_rows),
        "recovery_original_assumed_overall_mttr_gain_pct": st.mean(r["mttr_gain_pct"] for r in original_rows),
        "recovery_original_assumed_overall_downtime_gain_pct": st.mean(r["downtime_gain_pct"] for r in original_rows),
    }
    (args.output_dir / "results.json").write_text(json.dumps(summary, indent=2) + "\n")

    print("\n" + "=" * 60)
    print("ABLATION SUMMARY")
    print("=" * 60)
    print(f"Tier 1 (RF alone):        F1={tier1_metrics['f1']:.4f}  FPR={tier1_metrics['false_positive_rate']:.4f}")
    print(f"Tier 1+2 (RF+AE hybrid):  F1={tier1_2_metrics['f1']:.4f}  FPR={tier1_2_metrics['false_positive_rate']:.4f}")
    print(f"Tier 1+2+3 (grounded):    mean MTTR gain {summary['recovery_grounded_overall_mttr_gain_pct']:.1f}%, "
          f"mean downtime gain {summary['recovery_grounded_overall_downtime_gain_pct']:.1f}%")
    print(f"Tier 1+2+3 (orig. assumed): mean MTTR gain {summary['recovery_original_assumed_overall_mttr_gain_pct']:.1f}%, "
          f"mean downtime gain {summary['recovery_original_assumed_overall_downtime_gain_pct']:.1f}%")
    print(f"\nSaved full results to {args.output_dir / 'results.json'}")


if __name__ == "__main__":
    main()

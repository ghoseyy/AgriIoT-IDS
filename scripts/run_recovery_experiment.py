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

from agri_iot_ids.recovery.env import AgriIoTRecoveryEnv
from agri_iot_ids.recovery.agent import NaiveBaselinePolicy, QLearningPolicy, reward_for

CONNECTIVITY_SETTINGS = [1.0, 0.7, 0.4]
COMPUTE_SETTINGS = [3, 2, 1]
ATTACK_START = 5
MAX_STEPS = 100


def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate autonomous recovery vs. naive baseline for constrained AgriIoT nodes.")
    parser.add_argument("--train-episodes", type=int, default=4000)
    parser.add_argument("--eval-episodes", type=int, default=300)
    parser.add_argument("--output-dir", type=Path, default=Path("experiments/recovery"))
    parser.add_argument("--seed", type=int, default=0)
    return parser.parse_args()


def run_episode(env, policy, training=False):
    obs = env.reset()
    policy.reset()
    while True:
        prev_state = env.device_state
        action = policy.act(obs)
        next_obs, done = env.step(action)
        if training:
            policy.update(obs, action, reward_for(env.device_state, prev_state), next_obs, done)
        obs = next_obs
        if done:
            break
    ttr = env.time_to_recover if env.time_to_recover is not None else (MAX_STEPS - ATTACK_START)
    return ttr, env.downtime_steps


def train_agent(train_episodes, seed):
    agent = QLearningPolicy(seed=seed)
    for ep in range(train_episodes):
        conn = CONNECTIVITY_SETTINGS[ep % len(CONNECTIVITY_SETTINGS)]
        comp = COMPUTE_SETTINGS[(ep // len(CONNECTIVITY_SETTINGS)) % len(COMPUTE_SETTINGS)]
        env = AgriIoTRecoveryEnv(connectivity_reliability=conn, compute_budget_per_step=comp,
                                  attack_start=ATTACK_START, max_steps=MAX_STEPS, seed=1000 + ep)
        run_episode(env, agent, training=True)
        agent.epsilon = max(0.02, agent.epsilon * 0.999)
    agent.training = False
    return agent


def evaluate(policy, conn, comp, n, seed_base=5000):
    ttrs, downtimes = [], []
    for i in range(n):
        env = AgriIoTRecoveryEnv(connectivity_reliability=conn, compute_budget_per_step=comp,
                                  attack_start=ATTACK_START, max_steps=MAX_STEPS, seed=seed_base + i)
        ttr, dt = run_episode(env, policy, training=False)
        ttrs.append(ttr)
        downtimes.append(dt)
    return st.mean(ttrs), st.mean(downtimes)


def main():
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    print("Training Q-learning recovery agent...")
    agent = train_agent(args.train_episodes, args.seed)
    baseline = NaiveBaselinePolicy(response_delay=6)

    rows = []
    for conn in CONNECTIVITY_SETTINGS:
        for comp in COMPUTE_SETTINGS:
            b_ttr, b_dt = evaluate(baseline, conn, comp, args.eval_episodes)
            a_ttr, a_dt = evaluate(agent, conn, comp, args.eval_episodes)
            rows.append({
                "connectivity": conn,
                "compute_budget": comp,
                "baseline_mttr": b_ttr,
                "agent_mttr": a_ttr,
                "mttr_gain_pct": (b_ttr - a_ttr) / b_ttr * 100,
                "baseline_downtime": b_dt,
                "agent_downtime": a_dt,
                "downtime_gain_pct": (b_dt - a_dt) / b_dt * 100,
            })
            print(f"conn={conn} comp={comp}: MTTR {b_ttr:.2f}->{a_ttr:.2f} "
                  f"({rows[-1]['mttr_gain_pct']:.1f}%), downtime {b_dt:.2f}->{a_dt:.2f} "
                  f"({rows[-1]['downtime_gain_pct']:.1f}%)")

    summary = {
        "train_episodes": args.train_episodes,
        "eval_episodes_per_setting": args.eval_episodes,
        "results": rows,
        "overall_mttr_gain_pct": st.mean(r["mttr_gain_pct"] for r in rows),
        "overall_downtime_gain_pct": st.mean(r["downtime_gain_pct"] for r in rows),
    }
    with open(args.output_dir / "results.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nOverall mean MTTR improvement: {summary['overall_mttr_gain_pct']:.1f}%")
    print(f"Overall mean downtime improvement: {summary['overall_downtime_gain_pct']:.1f}%")
    print(f"Saved to {args.output_dir / 'results.json'}")


if __name__ == "__main__":
    main()

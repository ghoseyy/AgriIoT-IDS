"""Simulated AgriIoT node under attack, for evaluating recovery policies under
resource and connectivity constraints typical of field-deployed edge devices.

The detection tier (Random Forest, per the main IDS evaluation) is assumed to
have already flagged the node; this environment models what happens next --
the recovery decision and its execution under realistic hardware limits.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import random

HEALTHY, COMPROMISED, ISOLATED, RECOVERING = range(4)
WAIT, ISOLATE, ROLLBACK, REROUTE = range(4)

ACTION_COST = {WAIT: 0, ISOLATE: 1, ROLLBACK: 3, REROUTE: 1}


@dataclass
class AgriIoTRecoveryEnv:
    connectivity_reliability: float = 1.0
    compute_budget_per_step: float = 2.0
    attack_start: int = 5
    max_steps: int = 100
    seed: int | None = None
    # Detector-confidence distribution parameters. Defaults reproduce the
    # original assumed values (0.9/0.08 while actively attacked, 0.6/0.2
    # while compromised/isolated/recovering but not actively attacking).
    # hybrid_ablation.py overrides these with values empirically measured
    # from the actual Tier-1+Tier-2 detector's confidence distribution on
    # true positives/negatives, rather than leaving them as an assumption.
    conf_active_mean: float = 0.9
    conf_active_std: float = 0.08
    conf_idle_mean: float = 0.6
    conf_idle_std: float = 0.2

    def __post_init__(self) -> None:
        self.rng = random.Random(self.seed)
        self.reset()

    def reset(self) -> dict:
        self.t = 0
        self.device_state = HEALTHY
        self.recovering_ticks_left = 0
        self.downtime_steps = 0
        self.time_to_recover: int | None = None
        self.attack_active = False
        self.compute_credit = 0.0
        return self._obs()

    def _obs(self) -> dict:
        detector_conf = 0.0
        if self.attack_active:
            detector_conf = min(1.0, max(0.0, self.rng.gauss(self.conf_active_mean, self.conf_active_std)))
        elif self.device_state != HEALTHY:
            detector_conf = min(1.0, max(0.0, self.rng.gauss(self.conf_idle_mean, self.conf_idle_std)))
        return {"device_state": self.device_state, "detector_conf": detector_conf, "t": self.t}

    def step(self, action: int) -> tuple[dict, bool]:
        self.t += 1

        if self.t == self.attack_start and self.device_state == HEALTHY:
            self.device_state = COMPROMISED
            self.attack_active = True

        command_delivered = self.rng.random() < self.connectivity_reliability
        self.compute_credit += self.compute_budget_per_step
        can_afford = ACTION_COST[action] <= self.compute_credit
        if can_afford and action != WAIT:
            self.compute_credit -= ACTION_COST[action]

        if self.device_state == COMPROMISED:
            self.downtime_steps += 1
            if action != WAIT and command_delivered and can_afford:
                if action in (ISOLATE, REROUTE):
                    self.device_state = ISOLATED
                elif action == ROLLBACK:
                    self.device_state = RECOVERING
                    self.recovering_ticks_left = 2
        elif self.device_state == ISOLATED:
            self.downtime_steps += 1
            if action == ROLLBACK and command_delivered and can_afford:
                self.device_state = RECOVERING
                self.recovering_ticks_left = 2
        elif self.device_state == RECOVERING:
            self.downtime_steps += 1
            self.recovering_ticks_left -= 1
            if self.recovering_ticks_left <= 0:
                self.device_state = HEALTHY
                self.attack_active = False
                self.time_to_recover = self.t - self.attack_start

        done = (self.device_state == HEALTHY and self.time_to_recover is not None) or self.t >= self.max_steps
        return self._obs(), done

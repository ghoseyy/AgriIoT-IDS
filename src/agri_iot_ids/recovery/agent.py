"""Recovery policies: a fixed-delay baseline (proxy for manual/ops-driven
response) and a tabular Q-learning agent that learns recovery actions under
resource and connectivity constraints."""
from __future__ import annotations

from collections import defaultdict
import random

from agri_iot_ids.recovery.env import COMPROMISED, ISOLATED, RECOVERING, WAIT, ISOLATE, ROLLBACK, REROUTE, HEALTHY

ACTIONS = [WAIT, ISOLATE, ROLLBACK, REROUTE]


class NaiveBaselinePolicy:
    """Mimics a human/ops-driven response: fixed detection-to-action delay,
    then a fixed isolate-then-rollback sequence, no adaptivity."""

    def __init__(self, response_delay: int = 6):
        self.response_delay = response_delay
        self._steps_since_compromise = 0

    def reset(self) -> None:
        self._steps_since_compromise = 0

    def act(self, obs: dict) -> int:
        if obs["device_state"] in (COMPROMISED, ISOLATED, RECOVERING):
            self._steps_since_compromise += 1
        else:
            self._steps_since_compromise = 0

        if self._steps_since_compromise < self.response_delay:
            return WAIT
        if obs["device_state"] == COMPROMISED:
            return ISOLATE
        if obs["device_state"] == ISOLATED:
            return ROLLBACK
        return WAIT


def _discretize(obs: dict) -> tuple[int, int]:
    conf_bucket = int(obs["detector_conf"] * 4)
    return (obs["device_state"], conf_bucket)


class QLearningPolicy:
    def __init__(self, alpha: float = 0.2, gamma: float = 0.9, epsilon: float = 0.2, seed: int | None = None):
        self.q: dict = defaultdict(lambda: [0.0] * len(ACTIONS))
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.rng = random.Random(seed)
        self.training = True

    def reset(self) -> None:
        pass

    def act(self, obs: dict) -> int:
        s = _discretize(obs)
        if self.training and self.rng.random() < self.epsilon:
            return self.rng.choice(ACTIONS)
        qvals = self.q[s]
        return ACTIONS[max(range(len(ACTIONS)), key=lambda i: qvals[i])]

    def update(self, obs: dict, action: int, reward: float, next_obs: dict, done: bool) -> None:
        s = _discretize(obs)
        s2 = _discretize(next_obs)
        a_idx = ACTIONS.index(action)
        target = reward + (0 if done else self.gamma * max(self.q[s2]))
        self.q[s][a_idx] += self.alpha * (target - self.q[s][a_idx])


def reward_for(device_state: int, prev_state: int) -> float:
    if device_state == HEALTHY and prev_state != HEALTHY:
        return 10.0
    if device_state in (COMPROMISED, ISOLATED, RECOVERING):
        return -1.0
    return 0.0

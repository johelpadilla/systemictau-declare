"""Synthetic fixtures. G0 must not produce an event claim."""

from __future__ import annotations

import numpy as np


def g0_independent_ar(
    T: int = 400,
    N: int = 4,
    phi: float = 0.5,
    seed: int = 0,
) -> np.ndarray:
    """Independent AR(1) columns — null of no cross-variable ordinal structure."""
    rng = np.random.default_rng(seed)
    X = np.zeros((T, N))
    for j in range(N):
        e = rng.normal(size=T)
        for t in range(1, T):
            X[t, j] = phi * X[t - 1, j] + e[t]
    return X


def coupled_logistic(
    T: int = 800,
    N: int = 4,
    r: float = 3.7,
    eps: float = 0.12,
    seed: int = 1,
    burn: int = 200,
) -> np.ndarray:
    """Weakly coupled logistic maps (demo series, not a theorem)."""
    rng = np.random.default_rng(seed)
    x = rng.uniform(0.1, 0.9, size=N)
    out = np.zeros((T + burn, N))
    for t in range(T + burn):
        mx = float(np.mean(x))
        x = (1.0 - eps) * r * x * (1.0 - x) + eps * r * mx * (1.0 - mx)
        x = np.clip(x, 1e-9, 1.0 - 1e-9)
        out[t] = x
    return out[burn:]

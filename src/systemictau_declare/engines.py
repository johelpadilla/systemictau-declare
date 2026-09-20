"""Thin wrappers around systemictau and nested-recd.

This module does not reimplement Kendall τ, the RECD gate, or excess³.
"""

from __future__ import annotations

import importlib.metadata
import importlib.util
import sys
import types
from typing import Tuple

import numpy as np

_ST_ERR = (
    "systemictau >= 4.6.0 is required. "
    "Install with: pip install 'systemictau>=4.6.0,<5'"
)
_NR_ERR = (
    "nested-recd >= 0.2.0 is required. "
    "Install with: pip install 'nested-recd>=0.2.0'"
)

# Explicit parameters of nested-recd 0.2.0's compute_recd_from_conjunctions.
# That release forwards **alpha_kwargs into alpha_weights(); extra names such
# as compute_res (added later, default False) therefore explode. declare()
# never needs Res_pair.
_NESTED_CONJUNCTION_KW = frozenset(
    {
        "tau_s",
        "m",
        "d",
        "theta3",
        "window_tau",
        "lam_override",
        "stride",
        "alpha_syn",
        "alpha_surp",
    }
)


def call_compute_recd_from_conjunctions(fn, X, **kwargs):
    """Call nested-recd with only the 0.2.0 explicit kwargs.

    ``compute_res`` is dropped on purpose: 0.2.0 has no such argument
    (it lands in **alpha_kwargs and alpha_weights() raises); 0.2.2+
    defaults it to False.
    """
    filtered = {k: v for k, v in kwargs.items() if k in _NESTED_CONJUNCTION_KW}
    return fn(X, **filtered)


def _pkg_version(name: str) -> str:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return "unknown"


def _systemictau_from_submodules() -> dict:
    """Load core / recd / layers without executing systemictau/__init__.py.

    PyPI 4.6.0 imports panel.py at package import, and panel.py uses Union
    without importing it. declare() only needs Kendall τ, the gate, and RQA.
    """
    spec = importlib.util.find_spec("systemictau")
    if spec is None or not spec.submodule_search_locations:
        raise ImportError(_ST_ERR)
    for key in [k for k in sys.modules if k == "systemictau" or k.startswith("systemictau.")]:
        del sys.modules[key]
    stub = types.ModuleType("systemictau")
    stub.__path__ = list(spec.submodule_search_locations)
    stub.__package__ = "systemictau"
    stub.__file__ = spec.origin
    stub.__version__ = _pkg_version("systemictau")
    sys.modules["systemictau"] = stub
    from systemictau.core import compute_taus
    from systemictau.layers import hyper_persistence, rolling_rqa
    from systemictau.recd import accumulate_time, gate_function

    return {
        "compute_taus": compute_taus,
        "accumulate_time": accumulate_time,
        "gate_function": gate_function,
        "hyper_persistence": hyper_persistence,
        "rolling_rqa": rolling_rqa,
        "version": stub.__version__,
    }


def require_systemictau():
    try:
        from systemictau.core import compute_taus
        from systemictau.layers import hyper_persistence, rolling_rqa
        from systemictau.recd import accumulate_time, gate_function
        import systemictau as st_mod
    except Exception:
        try:
            return _systemictau_from_submodules()
        except Exception as exc:
            raise ImportError(_ST_ERR) from exc
    return {
        "compute_taus": compute_taus,
        "accumulate_time": accumulate_time,
        "gate_function": gate_function,
        "hyper_persistence": hyper_persistence,
        "rolling_rqa": rolling_rqa,
        "version": getattr(st_mod, "__version__", _pkg_version("systemictau")),
    }


def require_nested_recd():
    try:
        import nested_recd
        from nested_recd import compute_recd_from_conjunctions
        from nested_recd.surrogates import (
            phase_shuffle_independent,
            random_permutation_independent,
        )
    except ImportError as exc:
        raise ImportError(_NR_ERR) from exc
    return {
        "compute_recd_from_conjunctions": compute_recd_from_conjunctions,
        "phase_shuffle_independent": phase_shuffle_independent,
        "random_permutation_independent": random_permutation_independent,
        "version": getattr(nested_recd, "__version__", _pkg_version("nested-recd")),
    }


def pad_to(arr: np.ndarray, length: int, fill=np.nan) -> np.ndarray:
    """Right-align a shorter nested series onto laboratory length T."""
    a = np.asarray(arr)
    if a.ndim != 1:
        a = np.asarray(arr).ravel()
    if len(a) == length:
        return a.astype(float, copy=False)
    out = np.full(length, fill, dtype=float)
    n = min(len(a), length)
    out[-n:] = a[-n:]
    return out


def regime_labels(tau_s: np.ndarray, tau_st: float, tau_ch: float) -> np.ndarray:
    """Return string labels aligned with tau_s.

    stable      : tau_s >= tau_st
    chaotic     : |tau_s| < tau_ch
    anti-sync   : tau_s <= -tau_ch
    intermediate: otherwise (including the closed gate  tau_ch <= tau_s < tau_st)
    """
    tau = np.asarray(tau_s, dtype=float)
    labels = np.full(tau.shape, "undefined", dtype=object)
    finite = np.isfinite(tau)
    labels[finite & (tau >= tau_st)] = "stable"
    labels[finite & (np.abs(tau) < tau_ch)] = "chaotic"
    labels[finite & (tau <= -tau_ch)] = "anti-sync"
    labels[finite & (tau >= tau_ch) & (tau < tau_st)] = "intermediate"
    return labels


def rolling_variance_lag1(
    X: np.ndarray, window: int
) -> Tuple[np.ndarray, np.ndarray]:
    """Mean across columns of rolling variance and lag-1 autocorrelation."""
    X = np.asarray(X, dtype=float)
    T, N = X.shape
    var = np.full(T, np.nan)
    lag1 = np.full(T, np.nan)
    if window < 3 or T < window:
        return var, lag1
    for t in range(window - 1, T):
        w = X[t - window + 1 : t + 1]
        col_var = np.nanvar(w, axis=0, ddof=1)
        var[t] = float(np.nanmean(col_var))
        acs = []
        for j in range(N):
            col = w[:, j]
            if np.sum(np.isfinite(col)) < 3:
                continue
            a, b = col[:-1], col[1:]
            mask = np.isfinite(a) & np.isfinite(b)
            if mask.sum() < 2:
                continue
            if np.std(a[mask]) == 0 or np.std(b[mask]) == 0:
                acs.append(0.0)
            else:
                acs.append(float(np.corrcoef(a[mask], b[mask])[0, 1]))
        lag1[t] = float(np.nanmean(acs)) if acs else np.nan
    return var, lag1

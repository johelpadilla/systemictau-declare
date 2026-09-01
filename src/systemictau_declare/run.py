"""``declare()`` — the only public scientific entry point.

It does not predict outbreaks, crashes, or deaths. It declares which time
generator is being used, computes frozen-protocol contrasts, and seals FAR.
"""

from __future__ import annotations

from typing import Optional, Sequence, Union

import numpy as np

from .engines import (
    pad_to,
    regime_labels,
    require_nested_recd,
    require_systemictau,
    rolling_variance_lag1,
)
from .protocol import Protocol, require_no_weight_fit
from .schema import (
    AmplitudeContrast,
    DeclarationReport,
    GateGenerator,
    NestedDepth,
)
from .seals import make_seal

ArrayLike = Union[np.ndarray, Sequence[Sequence[float]]]


def _as_matrix(X: ArrayLike) -> np.ndarray:
    arr = np.asarray(X, dtype=float)
    if arr.ndim != 2:
        raise ValueError("X must be a 2-d array of shape (T, N) with N >= 2.")
    if arr.shape[1] < 2:
        raise ValueError("At least two variables are required (N >= 2).")
    if arr.shape[0] < 8:
        raise ValueError("Series is too short to declare a generator.")
    return arr


def _split_indices(n: int, basal_frac: float, contrast_frac: float):
    n_b = max(3, int(round(n * basal_frac)))
    n_c = max(3, int(round(n * contrast_frac)))
    if n_b + n_c > n:
        n_b = max(3, n // 3)
        n_c = max(3, n // 3)
    basal = np.arange(0, n_b)
    contrast = np.arange(n - n_c, n)
    return basal, contrast


def _finite(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    return x[np.isfinite(x)]


def _mean_delta_z(series: np.ndarray, basal_idx, contrast_idx):
    s = np.asarray(series, dtype=float)
    b = _finite(s[basal_idx])
    c = _finite(s[contrast_idx])
    if len(b) == 0 or len(c) == 0:
        return float("nan"), float("nan")
    delta = float(np.mean(c) - np.mean(b))
    sd = float(np.std(b, ddof=1)) if len(b) > 1 else 0.0
    z = float(delta / sd) if sd > 0 else (0.0 if delta == 0 else float("nan"))
    return delta, z


def _sign_int(a: float, b: float) -> int:
    if not (np.isfinite(a) and np.isfinite(b)) or a == 0 or b == 0:
        return 0
    return 1 if np.sign(a) == np.sign(b) else -1


def _joint_stat(delta_tau: float, delta_ex: float) -> float:
    if not (np.isfinite(delta_tau) and np.isfinite(delta_ex)):
        return float("nan")
    return float(np.hypot(delta_tau, delta_ex))


def _phase_shuffle(X: np.ndarray, seed: int, nested) -> np.ndarray:
    return nested["phase_shuffle_independent"](X, seed=seed)


def _permute(X: np.ndarray, seed: int, nested) -> np.ndarray:
    return nested["random_permutation_independent"](X, seed=seed)


def _surrogate_one(X: np.ndarray, method: str, seed: int, nested) -> np.ndarray:
    if method in ("phase_shuffle", "phase", "iaaft"):
        return _phase_shuffle(X, seed, nested)
    if method in ("permute", "permutation"):
        return _permute(X, seed, nested)
    raise ValueError(f"Unknown surrogate method: {method}")


def _tau_and_nested(X, protocol, st, nested):
    taus, _ = st["compute_taus"](X, window_size=protocol.window, stride=protocol.stride)
    T_n, dtk, g, depth = st["accumulate_time"](taus, window_size=protocol.window)
    nested_out = nested["compute_recd_from_conjunctions"](
        X,
        tau_s=taus,
        m=protocol.m,
        d=protocol.d_persist,
        theta3=protocol.theta3,
        window_tau=protocol.window,
        stride=protocol.stride,
        alpha_syn=protocol.alpha_syn,
        alpha_surp=protocol.alpha_surp,
        compute_res=False,
    )
    return taus, T_n, dtk, g, depth, nested_out


def declare(
    X: ArrayLike,
    time=None,
    protocol: Optional[Protocol] = None,
    controls: Optional[Sequence[ArrayLike]] = None,
    event_only: bool = False,
    events=None,  # noqa: ARG001 — reserved; lead-time labels are not inferred here
) -> DeclarationReport:
    """Declare the generator on a multivariate series.

    Parameters
    ----------
    X :
        Array of shape (T, N), N >= 2.
    time :
        Optional laboratory time vector of length T. If omitted, ``np.arange(T)``.
    protocol :
        ``Protocol.frozen_v1()`` by default. Any other object should come from
        ``Protocol.exploratory(...)``.
    controls :
        Optional sequence of control arrays, each shape (T_c, N). Absence
        forces ``FAR: undefined``.
    event_only :
        If True and no controls, seal is ``event-only`` (sensitivity without FAR).

    Returns
    -------
    DeclarationReport
        Two clocks, nested depth, amplitude contrast, surrogate p, and seal.

    Notes
    -----
    This function is named ``declare``, not ``predict_outbreak``.
    """
    protocol = protocol or Protocol.frozen_v1()
    require_no_weight_fit(protocol)
    X = _as_matrix(X)
    T, N = X.shape
    t = np.arange(T, dtype=float) if time is None else np.asarray(time, dtype=float)
    if t.shape[0] != T:
        raise ValueError("time must have length T.")

    st = require_systemictau()
    nested = require_nested_recd()

    taus, T_n, dtk, g, depth, nested_out = _tau_and_nested(X, protocol, st, nested)
    taus = np.asarray(taus, dtype=float)
    T_n = np.asarray(T_n, dtype=float)
    dtk = np.asarray(dtk, dtype=float)
    g = np.asarray(g, dtype=float)
    depth = np.asarray(depth, dtype=float)

    # Signed gate increment actually accumulated (g * dtk). Keep dT as that
    # increment, distinct from nested excess3.
    dT = g * dtk

    excess3 = pad_to(nested_out["excess3"], T)
    phi1 = pad_to(nested_out["phi1"], T)
    phi2 = pad_to(nested_out["phi2"], T)
    phi3 = pad_to(nested_out["phi3"], T)

    hp_z, core_hyper = st["hyper_persistence"](
        taus, window_size=max(protocol.window, 20), threshold_chaos=protocol.tau_ch
    )
    lam_all, tt_all = st["rolling_rqa"](
        taus,
        window_size=protocol.rqa_window,
        min_line_length=protocol.rqa_min_line,
    )
    lam_core = np.full(T, np.nan)
    tt_core = np.full(T, np.nan)
    if protocol.rqa == "core_hyper_only":
        mask = np.asarray(core_hyper, dtype=bool)
        lam_core[mask] = np.asarray(lam_all, dtype=float)[mask]
        tt_core[mask] = np.asarray(tt_all, dtype=float)[mask]
    else:
        lam_core = np.asarray(lam_all, dtype=float)
        tt_core = np.asarray(tt_all, dtype=float)

    var, lag1 = rolling_variance_lag1(X, protocol.window)
    regime = regime_labels(taus, protocol.tau_st, protocol.tau_ch)

    valid = np.where(np.isfinite(taus))[0]
    if len(valid) < 8:
        basal_idx = np.arange(min(8, T))
        contrast_idx = np.arange(max(0, T - 8), T)
    else:
        rel_b, rel_c = _split_indices(len(valid), protocol.basal_frac, protocol.contrast_frac)
        basal_idx = valid[rel_b]
        contrast_idx = valid[rel_c]

    delta_tau, z_tau = _mean_delta_z(taus, basal_idx, contrast_idx)
    delta_ex, z_ex = _mean_delta_z(excess3, basal_idx, contrast_idx)
    delta_T, _ = _mean_delta_z(T_n, basal_idx, contrast_idx)
    delta_var, z_var = _mean_delta_z(var, basal_idx, contrast_idx)
    delta_lag1, z_lag1 = _mean_delta_z(lag1, basal_idx, contrast_idx)

    obs_stat = _joint_stat(delta_tau, delta_ex)

    rng = np.random.default_rng(protocol.surrogate_seed)
    null_stats = []
    B = int(protocol.B)
    for _ in range(B):
        seed = int(rng.integers(0, 2**31 - 1))
        Xs = _surrogate_one(X, protocol.surrogate, seed, nested)
        try:
            taus_s, *_rest, nested_s = _tau_and_nested(Xs, protocol, st, nested)
        except Exception:
            continue
        ex_s = pad_to(nested_s["excess3"], T)
        d_tau_s, _ = _mean_delta_z(np.asarray(taus_s, dtype=float), basal_idx, contrast_idx)
        d_ex_s, _ = _mean_delta_z(ex_s, basal_idx, contrast_idx)
        null_stats.append(_joint_stat(d_tau_s, d_ex_s))
    null = np.asarray(null_stats, dtype=float)
    null = null[np.isfinite(null)]
    if np.isfinite(obs_stat) and len(null) > 0:
        p_surr = (1.0 + float(np.sum(np.abs(null) >= abs(obs_stat)))) / (1.0 + len(null))
        n_surr = int(len(null))
    else:
        p_surr = float("nan")
        n_surr = int(len(null))

    event_candidate = bool(
        (np.isfinite(z_tau) and abs(z_tau) >= protocol.z_abs_threshold)
        or (np.isfinite(z_ex) and abs(z_ex) >= protocol.z_abs_threshold)
    )

    control_arrays = None
    n_ctrl = 0
    n_ctrl_alarms = None
    if controls is not None:
        control_arrays = [_as_matrix(c) for c in controls]
        n_ctrl = len(control_arrays)
        n_ctrl_alarms = 0
        for C in control_arrays:
            # Same frozen protocol, no nested surrogate loop (FAR uses candidate).
            try:
                taus_c, *_r, nested_c = _tau_and_nested(C, protocol, st, nested)
            except Exception:
                continue
            Tc = C.shape[0]
            valid_c = np.where(np.isfinite(taus_c))[0]
            if len(valid_c) < 8:
                continue
            rb, rc = _split_indices(len(valid_c), protocol.basal_frac, protocol.contrast_frac)
            b_c, c_c = valid_c[rb], valid_c[rc]
            _, z_tau_c = _mean_delta_z(np.asarray(taus_c, dtype=float), b_c, c_c)
            ex_c = pad_to(nested_c["excess3"], Tc)
            _, z_ex_c = _mean_delta_z(ex_c, b_c, c_c)
            cand = (
                (np.isfinite(z_tau_c) and abs(z_tau_c) >= protocol.z_abs_threshold)
                or (np.isfinite(z_ex_c) and abs(z_ex_c) >= protocol.z_abs_threshold)
            )
            if cand:
                n_ctrl_alarms += 1

    seal = make_seal(
        controls=control_arrays,
        event_only=event_only,
        event_candidate=event_candidate,
        p_surrogate=p_surr,
        p_threshold=protocol.p_threshold,
        n_control_alarms=n_ctrl_alarms,
        n_controls=n_ctrl,
    )

    notes = []
    if protocol.exploratory:
        notes.append(
            "EXPLORATORY: protocol departed from frozen_v1 ("
            + ", ".join(protocol.exploratory_overrides)
            + ")."
        )
    notes.extend(protocol.non_identification)

    versions = {
        "systemictau_declare": "0.1.1",
        "systemictau": st["version"],
        "nested_recd": nested["version"],
        "protocol_hash": protocol.yaml_hash,
    }

    return DeclarationReport(
        t=t,
        X_shape=(T, N),
        protocol_name=protocol.name,
        protocol_hash=protocol.yaml_hash,
        exploratory=protocol.exploratory,
        tau_s=taus,
        gate=GateGenerator(
            T_n=T_n,
            dT=dT,
            g=g,
            depth=depth,
            delta_T=delta_T,
        ),
        nested=NestedDepth(
            phi1=phi1,
            phi2=phi2,
            phi3=phi3,
            excess3=excess3,
            delta_excess3=delta_ex,
            z_excess3=z_ex,
        ),
        regime=regime,
        lam_core=lam_core,
        tt_core=tt_core,
        core_hyper=np.asarray(core_hyper, dtype=bool),
        amp=AmplitudeContrast(
            variance=var,
            lag1=lag1,
            delta_variance=delta_var,
            delta_lag1=delta_lag1,
            z_variance=z_var,
            z_lag1=z_lag1,
            sign_vs_tau=_sign_int(delta_var, delta_tau),
            sign_vs_excess3=_sign_int(delta_var, delta_ex),
        ),
        delta_tau_s=delta_tau,
        z_tau_s=z_tau,
        p_surrogate=p_surr,
        n_surrogates=n_surr,
        surrogate_method=protocol.surrogate,
        sign_tau_excess3=_sign_int(delta_tau, delta_ex),
        sign_tau_variance=_sign_int(delta_tau, delta_var),
        seal=seal,
        non_identification=protocol.non_identification,
        versions=versions,
        notes=tuple(notes),
    )

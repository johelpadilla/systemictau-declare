"""Calls into nested-recd must not feed extras into 0.2.0's **alpha_kwargs."""

import pytest

from systemictau_declare.engines import call_compute_recd_from_conjunctions


def _alpha_weights(lam, alpha10=1.0, beta1=2.0):
    return lam, alpha10, beta1


def compute_recd_from_conjunctions_020(X, tau_s=None, m=3, d=4, **alpha_kwargs):
    """Mimic nested-recd 0.2.0: unknown kwargs go to alpha_weights()."""
    _alpha_weights(0.0, **alpha_kwargs)
    return {"excess3": [0.0], "phi1": [0], "phi2": [0], "phi3": [0], "m": m, "d": d, "tau_s": tau_s, "X": X}


def test_compute_res_must_not_reach_alpha_kwargs():
    out = call_compute_recd_from_conjunctions(
        compute_recd_from_conjunctions_020,
        [[1.0, 2.0]],
        tau_s=[0.1],
        m=3,
        d=4,
        compute_res=False,
    )
    assert out["m"] == 3
    assert out["tau_s"] == [0.1]


def test_bare_020_with_compute_res_explodes():
    with pytest.raises(TypeError):
        compute_recd_from_conjunctions_020([[1.0, 2.0]], compute_res=False)

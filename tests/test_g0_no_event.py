"""G0 (independent AR) must not produce an event claim."""

import numpy as np

from systemictau_declare import Protocol, declare, g0_independent_ar


def test_g0_without_controls_far_undefined_no_claim():
    X = g0_independent_ar(T=180, N=3, seed=7)
    P = Protocol.exploratory(B=5, surrogate="permute")
    rep = declare(X, protocol=P, controls=None)
    assert rep.seal.far == "undefined"
    assert rep.seal.event_claimed is False
    assert "dT" in rep.as_dict()
    assert "excess3" in rep.as_dict()
    assert np.asarray(rep.gate.dT).shape == np.asarray(rep.nested.excess3).shape


def test_g0_event_only_still_unclaimed():
    X = g0_independent_ar(T=180, N=3, seed=11)
    P = Protocol.exploratory(B=5, surrogate="permute")
    rep = declare(X, protocol=P, controls=None, event_only=True)
    assert rep.seal.far == "event-only"
    assert rep.seal.event_claimed is False

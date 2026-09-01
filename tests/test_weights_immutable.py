from dataclasses import FrozenInstanceError

import pytest

from systemictau_declare import Protocol


def test_frozen_weights_are_a_priori():
    P = Protocol.frozen_v1()
    assert P.weights == (0.6, 0.4)
    assert P.alpha_syn == 0.6
    assert P.alpha_surp == 0.4
    assert not hasattr(Protocol, "fit")
    with pytest.raises(AttributeError):
        P.weights = (0.5, 0.5)  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        P.alpha_syn = 0.9  # type: ignore[misc]


def test_exploratory_is_marked_when_weights_change():
    P = Protocol.exploratory(alpha_syn=0.5, alpha_surp=0.5)
    assert P.exploratory is True
    assert P.name == "exploratory"
    assert "alpha_syn" in P.exploratory_overrides
    assert Protocol.frozen_v1().is_frozen is True
    assert P.is_frozen is False

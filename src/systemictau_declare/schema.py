"""Result schema. Gate RECD and nested Level-3 occupy distinct fields.

Do not identify ``dT`` with ``excess3``. Do not identify ``T_n`` with
laboratory time ``t``. Do not call ``Sigma_RECD`` entropy production.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import numpy as np


@dataclass
class Seal:
    """False-alarm / claim seal.

    ``far`` is one of:
      - ``undefined``  — no control series were supplied
      - ``event-only`` — events without matched controls
      - ``estimated``  — controls present; ``far_value`` is a rate in [0, 1]
    """

    far: str
    far_value: Optional[float] = None
    event_candidate: bool = False
    event_claimed: bool = False
    n_controls: int = 0
    event_only: bool = False
    reason: str = ""

    def as_dict(self) -> dict:
        return {
            "far": self.far,
            "far_value": self.far_value,
            "event_candidate": self.event_candidate,
            "event_claimed": self.event_claimed,
            "n_controls": self.n_controls,
            "event_only": self.event_only,
            "reason": self.reason,
        }


@dataclass
class AmplitudeContrast:
    """Univariate amplitude channel, kept for sign comparison only."""

    variance: np.ndarray
    lag1: np.ndarray
    delta_variance: float
    delta_lag1: float
    z_variance: float
    z_lag1: float
    sign_vs_tau: int
    sign_vs_excess3: int


@dataclass
class NestedDepth:
    """Nested ordinal depth. Continuous excess3 is the primary Level-3 readout."""

    phi1: np.ndarray
    phi2: np.ndarray
    phi3: np.ndarray
    excess3: np.ndarray
    delta_excess3: float
    z_excess3: float


@dataclass
class GateGenerator:
    """Gate RECD generator. Not nested excess3. Not laboratory t."""

    T_n: np.ndarray
    dT: np.ndarray
    g: np.ndarray
    depth: np.ndarray
    delta_T: float


@dataclass
class DeclarationReport:
    """Single object returned by ``declare()``.

    Fields are aligned to laboratory index ``t`` (NaN where undefined).
    """

    t: np.ndarray
    X_shape: tuple
    protocol_name: str
    protocol_hash: str
    exploratory: bool
    tau_s: np.ndarray
    gate: GateGenerator
    nested: NestedDepth
    regime: np.ndarray
    lam_core: np.ndarray
    tt_core: np.ndarray
    core_hyper: np.ndarray
    amp: AmplitudeContrast
    delta_tau_s: float
    z_tau_s: float
    p_surrogate: float
    n_surrogates: int
    surrogate_method: str
    sign_tau_excess3: int
    sign_tau_variance: int
    seal: Seal
    non_identification: tuple
    versions: Dict[str, str] = field(default_factory=dict)
    notes: tuple = field(default_factory=tuple)

    def as_dict(self) -> Dict[str, Any]:
        """JSON-friendly summary. Series stay as lists; two clocks stay separate."""
        return {
            "t": _to_list(self.t),
            "X_shape": list(self.X_shape),
            "protocol_name": self.protocol_name,
            "protocol_hash": self.protocol_hash,
            "exploratory": self.exploratory,
            "tau_s": _to_list(self.tau_s),
            "T_n": _to_list(self.gate.T_n),
            "dT": _to_list(self.gate.dT),
            "g": _to_list(self.gate.g),
            "depth": _to_list(self.gate.depth),
            "excess3": _to_list(self.nested.excess3),
            "Phi1": _to_list(self.nested.phi1),
            "Phi2": _to_list(self.nested.phi2),
            "Phi3": _to_list(self.nested.phi3),
            "regime": _to_list(self.regime),
            "lam_core": _to_list(self.lam_core),
            "tt_core": _to_list(self.tt_core),
            "core_hyper": _to_list(self.core_hyper.astype(float)),
            "variance": _to_list(self.amp.variance),
            "lag1": _to_list(self.amp.lag1),
            "delta_tau_s": self.delta_tau_s,
            "delta_excess3": self.nested.delta_excess3,
            "delta_T_n": self.gate.delta_T,
            "delta_variance": self.amp.delta_variance,
            "z_tau_s": self.z_tau_s,
            "z_excess3": self.nested.z_excess3,
            "p_surrogate": self.p_surrogate,
            "n_surrogates": self.n_surrogates,
            "surrogate_method": self.surrogate_method,
            "sign_tau_excess3": self.sign_tau_excess3,
            "sign_tau_variance": self.sign_tau_variance,
            "seal": self.seal.as_dict(),
            "non_identification": list(self.non_identification),
            "versions": dict(self.versions),
            "notes": list(self.notes),
        }

    def summary(self) -> Dict[str, Any]:
        """One-page scalars. No series."""
        return {
            "protocol": self.protocol_name,
            "protocol_hash": self.protocol_hash[:12],
            "exploratory": self.exploratory,
            "n_obs": int(self.X_shape[0]),
            "n_var": int(self.X_shape[1]),
            "delta_tau_s": self.delta_tau_s,
            "delta_excess3": self.nested.delta_excess3,
            "delta_T_n": self.gate.delta_T,
            "delta_variance": self.amp.delta_variance,
            "z_tau_s": self.z_tau_s,
            "z_excess3": self.nested.z_excess3,
            "p_surrogate": self.p_surrogate,
            "sign_tau_excess3": self.sign_tau_excess3,
            "sign_tau_variance": self.sign_tau_variance,
            "far": self.seal.far,
            "event_claimed": self.seal.event_claimed,
            "event_candidate": self.seal.event_candidate,
        }


def _to_list(x) -> list:
    arr = np.asarray(x)
    out = []
    for v in arr.ravel().tolist():
        if v is None:
            out.append(None)
        elif isinstance(v, (float, np.floating)) and not np.isfinite(v):
            out.append(None)
        elif isinstance(v, (np.floating,)):
            out.append(float(v))
        elif isinstance(v, (np.integer,)):
            out.append(int(v))
        elif isinstance(v, bytes):
            out.append(v.decode("utf-8"))
        else:
            out.append(v)
    return out

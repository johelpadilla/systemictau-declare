"""Frozen and exploratory protocol objects.

``Protocol.frozen_v1()`` is the only object a citable scientific run should
use. Any deviation constructs ``Protocol.exploratory(...)`` and the report is
marked as such. Weights have no setter.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Mapping, Optional, Tuple

import yaml

_HASH_EXCLUDE = frozenset({"canonical_hash", "notes", "changelog"})

_FROZEN_NAME = "frozen_v1"


def _protocol_yaml_path(name: str = _FROZEN_NAME) -> Path:
    here = Path(__file__).resolve().parent
    packaged = here / "protocols" / f"{name}.yaml"
    if packaged.exists():
        return packaged
    repo = here.parents[2] / "protocols" / f"{name}.yaml"
    if repo.exists():
        return repo
    raise FileNotFoundError(
        f"Protocol YAML '{name}' not found. Expected {packaged} or {repo}."
    )


def _load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"Protocol file {path} is not a mapping.")
    return data


def canonical_payload(data: Mapping[str, Any]) -> dict:
    """Return the hashed subset of a protocol mapping."""
    return {k: data[k] for k in sorted(data) if k not in _HASH_EXCLUDE}


def protocol_hash(data: Mapping[str, Any]) -> str:
    payload = canonical_payload(data)
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Protocol:
    """Immutable run contract.

    Attributes
    ----------
    weights :
        ``(alpha_syn, alpha_surp)``. Frozen at (0.6, 0.4). There is no setter.
    exploratory :
        True if any field departed from frozen_v1.
    """

    name: str
    version: str
    window: int
    stride: int
    m: int
    delay: int
    d_persist: int
    theta3: float
    alpha_syn: float
    alpha_surp: float
    tau_st: float
    tau_ch: float
    delta_feigenbaum: float
    detector: str
    basal_frac: float
    contrast_frac: float
    z_abs_threshold: float
    surrogate: str
    B: int
    surrogate_seed: int
    rqa: str
    rqa_window: int
    rqa_min_line: int
    core_hyper_run: int
    p_threshold: float
    pins: Mapping[str, str] = field(default_factory=dict)
    non_identification: Tuple[str, ...] = field(default_factory=tuple)
    yaml_hash: str = ""
    exploratory: bool = False
    exploratory_overrides: Tuple[str, ...] = field(default_factory=tuple)
    source_path: str = ""

    @property
    def weights(self) -> Tuple[float, float]:
        return (float(self.alpha_syn), float(self.alpha_surp))

    @property
    def is_frozen(self) -> bool:
        return (not self.exploratory) and self.name == _FROZEN_NAME

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
            "window": self.window,
            "stride": self.stride,
            "m": self.m,
            "delay": self.delay,
            "d_persist": self.d_persist,
            "theta3": self.theta3,
            "alpha_syn": self.alpha_syn,
            "alpha_surp": self.alpha_surp,
            "tau_st": self.tau_st,
            "tau_ch": self.tau_ch,
            "delta_feigenbaum": self.delta_feigenbaum,
            "detector": self.detector,
            "basal_frac": self.basal_frac,
            "contrast_frac": self.contrast_frac,
            "z_abs_threshold": self.z_abs_threshold,
            "surrogate": self.surrogate,
            "B": self.B,
            "surrogate_seed": self.surrogate_seed,
            "rqa": self.rqa,
            "rqa_window": self.rqa_window,
            "rqa_min_line": self.rqa_min_line,
            "core_hyper_run": self.core_hyper_run,
            "p_threshold": self.p_threshold,
            "pins": dict(self.pins),
            "non_identification": list(self.non_identification),
            "yaml_hash": self.yaml_hash,
            "exploratory": self.exploratory,
            "exploratory_overrides": list(self.exploratory_overrides),
        }

    @classmethod
    def from_mapping(
        cls,
        data: Mapping[str, Any],
        *,
        source_path: str = "",
        exploratory: bool = False,
        overrides: Tuple[str, ...] = (),
    ) -> "Protocol":
        pins = data.get("pins") or {}
        non_id = tuple(data.get("non_identification") or ())
        return cls(
            name=str(data["name"]),
            version=str(data.get("version", "0")),
            window=int(data["window"]),
            stride=int(data.get("stride", 1)),
            m=int(data["m"]),
            delay=int(data.get("delay", 1)),
            d_persist=int(data.get("d_persist", 4)),
            theta3=float(data["theta3"]),
            alpha_syn=float(data["alpha_syn"]),
            alpha_surp=float(data["alpha_surp"]),
            tau_st=float(data["tau_st"]),
            tau_ch=float(data["tau_ch"]),
            delta_feigenbaum=float(data["delta_feigenbaum"]),
            detector=str(data["detector"]),
            basal_frac=float(data.get("basal_frac", 0.3)),
            contrast_frac=float(data.get("contrast_frac", 0.3)),
            z_abs_threshold=float(data.get("z_abs_threshold", 2.0)),
            surrogate=str(data["surrogate"]),
            B=int(data["B"]),
            surrogate_seed=int(data.get("surrogate_seed", 0)),
            rqa=str(data.get("rqa", "core_hyper_only")),
            rqa_window=int(data.get("rqa_window", 25)),
            rqa_min_line=int(data.get("rqa_min_line", 2)),
            core_hyper_run=int(data.get("core_hyper_run", 7)),
            p_threshold=float(data.get("p_threshold", 0.05)),
            pins=dict(pins),
            non_identification=non_id,
            yaml_hash=protocol_hash(data),
            exploratory=exploratory,
            exploratory_overrides=overrides,
            source_path=source_path,
        )

    @classmethod
    def frozen_v1(cls) -> "Protocol":
        path = _protocol_yaml_path(_FROZEN_NAME)
        data = _load_yaml(path)
        proto = cls.from_mapping(data, source_path=str(path), exploratory=False)
        if proto.weights != (0.6, 0.4):
            raise RuntimeError(
                "frozen_v1 weights are not (0.6, 0.4). The YAML was tampered with."
            )
        return proto

    @classmethod
    def exploratory(cls, **overrides: Any) -> "Protocol":
        """Return a marked copy of frozen_v1 with explicit deviations.

        Weights still cannot be *fit*; they can only be overridden here, and
        the report is labelled exploratory. There is no ``fit()``.
        """
        base = cls.frozen_v1()
        forbidden = {"name", "yaml_hash", "is_frozen", "weights"}
        unknown = [k for k in overrides if k in forbidden or not hasattr(base, k)]
        if unknown:
            raise TypeError(f"Unknown or forbidden exploratory fields: {unknown}")
        if not overrides:
            return replace(
                base,
                exploratory=True,
                name="exploratory",
                exploratory_overrides=("marked_without_field_change",),
            )
        patched = replace(
            base,
            exploratory=True,
            name="exploratory",
            exploratory_overrides=tuple(sorted(overrides)),
            **overrides,
        )
        return patched


def require_no_weight_fit(protocol: Protocol) -> None:
    """Guard: this package has no weight estimator."""
    if protocol.weights != (0.6, 0.4) and not protocol.exploratory:
        raise RuntimeError("Non-default weights are only legal on Protocol.exploratory.")

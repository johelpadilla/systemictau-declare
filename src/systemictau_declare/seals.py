"""FAR seal. The product is the refusal to claim an event without controls."""

from __future__ import annotations

from typing import Optional, Sequence

import numpy as np

from .schema import Seal


def make_seal(
    *,
    controls: Optional[Sequence[np.ndarray]],
    event_only: bool,
    event_candidate: bool,
    p_surrogate: float,
    p_threshold: float,
    n_control_alarms: Optional[int] = None,
    n_controls: int = 0,
) -> Seal:
    """Construct the claim seal.

    Rules
    -----
    - No controls, not event_only → FAR: undefined. event_claimed is False.
    - event_only without controls → FAR: event-only. event_claimed is False.
    - Controls present → FAR: estimated. event_claimed requires candidate,
      p < threshold, and is never True solely from sensitivity on events.
    """
    if controls is None and not event_only:
        return Seal(
            far="undefined",
            far_value=None,
            event_candidate=bool(event_candidate),
            event_claimed=False,
            n_controls=0,
            event_only=False,
            reason="No control series supplied. FAR is undefined; no event is claimed.",
        )
    if event_only and (controls is None or n_controls == 0):
        return Seal(
            far="event-only",
            far_value=None,
            event_candidate=bool(event_candidate),
            event_claimed=False,
            n_controls=0,
            event_only=True,
            reason="Event-only design. Sensitivity without FAR is not a claim.",
        )

    far_value = None
    if n_controls > 0 and n_control_alarms is not None:
        far_value = float(n_control_alarms) / float(n_controls)

    p_ok = np.isfinite(p_surrogate) and (p_surrogate < p_threshold)
    claimed = bool(event_candidate) and bool(p_ok)
    reason = (
        "Controls present. Event claimed only if candidate and surrogate p "
        f"< {p_threshold}."
        if claimed
        else "Controls present. Candidate did not meet surrogate threshold, "
        "or no candidate."
    )
    return Seal(
        far="estimated",
        far_value=far_value,
        event_candidate=bool(event_candidate),
        event_claimed=claimed,
        n_controls=int(n_controls),
        event_only=False,
        reason=reason,
    )

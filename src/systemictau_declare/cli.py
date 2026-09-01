"""CLI: recd-declare data.csv --protocol frozen_v1 --out report.html"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np

from .protocol import Protocol
from .report import write_report
from .run import declare


def _read_csv(path: Path) -> Tuple[Optional[np.ndarray], np.ndarray]:
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh)
        rows = [r for r in reader if r and any(c.strip() for c in r)]
    if not rows:
        raise ValueError(f"{path} is empty.")
    header = rows[0]
    numeric_header = True
    for h in header:
        try:
            float(h)
        except ValueError:
            numeric_header = False
            break
    body = rows if numeric_header else rows[1:]
    names = header if not numeric_header else [f"x{i}" for i in range(len(header))]
    data = []
    for r in body:
        data.append([float(c) if c.strip() not in ("", "nan", "NaN") else np.nan for c in r])
    arr = np.asarray(data, dtype=float)
    time = None
    first = names[0].strip().lower()
    if first in {"t", "time", "date", "index", "week", "timestamp"}:
        time = arr[:, 0]
        arr = arr[:, 1:]
    if arr.ndim != 2 or arr.shape[1] < 2:
        raise ValueError(
            f"{path}: need at least two variable columns (got shape {arr.shape}). "
            "Optional first column named t/time is treated as laboratory time."
        )
    return time, arr


def _load_controls(path: Optional[Path]) -> Optional[List[np.ndarray]]:
    if path is None:
        return None
    # A controls file may be one matrix, or a directory of CSVs.
    if path.is_dir():
        files = sorted(path.glob("*.csv"))
        if not files:
            raise ValueError(f"No CSV files in {path}")
        out = []
        for f in files:
            _, X = _read_csv(f)
            out.append(X)
        return out
    _, X = _read_csv(path)
    return [X]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="recd-declare",
        description=(
            "Declare the time generator on a multivariate CSV. "
            "Does not predict outbreaks. Without --controls, FAR is undefined."
        ),
    )
    p.add_argument("data", type=Path, help="CSV with optional t column + N>=2 variables")
    p.add_argument(
        "--protocol",
        default="frozen_v1",
        help="frozen_v1 (default). Any other token is rejected; use Python for exploratory.",
    )
    p.add_argument("--controls", type=Path, default=None, help="Control CSV or directory of CSVs")
    p.add_argument("--event-only", action="store_true", help="Seal FAR as event-only (no claim)")
    p.add_argument("--out", type=Path, default=Path("report.html"), help="HTML report path")
    p.add_argument("--json", type=Path, default=None, help="Optional JSON dump of summary()")
    p.add_argument(
        "--B",
        type=int,
        default=None,
        help="Override surrogate count (marks the run exploratory)",
    )
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    if args.protocol != "frozen_v1":
        print(
            "CLI only ships frozen_v1. For Protocol.exploratory(...) use the Python API.",
            file=sys.stderr,
        )
        return 2
    protocol = Protocol.frozen_v1()
    if args.B is not None:
        protocol = Protocol.exploratory(B=int(args.B))
        print("Warning: --B marks this run EXPLORATORY.", file=sys.stderr)

    time, X = _read_csv(args.data)
    controls = _load_controls(args.controls)
    rep = declare(
        X,
        time=time,
        protocol=protocol,
        controls=controls,
        event_only=args.event_only,
    )
    out = write_report(rep, args.out)
    print(f"wrote {out}")
    print(f"FAR: {rep.seal.far}")
    print(f"event_claimed: {rep.seal.event_claimed}")
    print(f"protocol_hash: {rep.protocol_hash}")
    if args.json:
        args.json.write_text(json.dumps(rep.summary(), indent=2), encoding="utf-8")
        print(f"wrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

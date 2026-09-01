# systemictau-declare

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22237497.svg)](https://doi.org/10.5281/zenodo.22237497)
[![PyPI](https://img.shields.io/pypi/v/systemictau-declare.svg)](https://pypi.org/project/systemictau-declare/)

**Declare the time generator. Do not predict without controls.**

`systemictau-declare` is a thin protocol layer on top of
[`systemictau`](https://pypi.org/project/systemictau/) 4.6.x and
[`nested-recd`](https://github.com/johelpadilla/nested-recd).
It does **not** replace the motor. It freezes the operational contract that
scientific runs should share: window, weights, gate bands, surrogate, and a
FAR seal that refuses to claim an event when no controls were supplied.

```python
from systemictau_declare import Protocol, declare

P = Protocol.frozen_v1()          # window=13, m=3, θ3=0.08, weights=(0.6, 0.4)
rep = declare(X, time=t, protocol=P, controls=None)
print(rep.seal.far)               # 'undefined'  — no event is claimed
```

```bash
pip install "systemictau-declare[report]"
recd-declare data.csv --protocol frozen_v1 --out report.html
recd-declare data.csv --controls controls.csv --out report.html
```

The top-level function is named `declare`, not `predict_outbreak`.

## What this package is for

Complex-systems papers routinely index series by laboratory time \(t\) and then
speak of “the time of the system”. RECD constructs a second generator \(T_n\)
from ordinal concordance. Nested `excess³` measures depth of reorganization.
None of that is usable as science if every notebook retunes \(\theta_3\) and
paints a red light without a false-alarm rate.

This package exists so that:

1. **The protocol is frozen** (`protocols/frozen_v1.yaml`, hashed).
2. **The two clocks stay two fields** (\(t\) vs \(T_n\); \(\Delta T_n\) is not \(\Delta\mathrm{excess}^3\)).
3. **FAR is a seal**, not a footnote: `undefined` | `event-only` | `estimated`.
4. **A one-page report** can be cited. Ontology, Polo, and crash buttons are out of scope.

Read the software paper: [`papers/why_systemictau_declare.pdf`](papers/why_systemictau_declare.pdf)  
(Español: [`papers/por_que_existe_systemictau_declare.pdf`](papers/por_que_existe_systemictau_declare.pdf))  
Usage manual: [`docs/MANUAL.pdf`](docs/MANUAL.pdf)

## What this package is not

- Not a replacement for the SI second.
- Not a proof that \(\Sigma^{\mathrm{RECD}}\) is Clausius production (CT-4C remains open).
- Not a Williams–Beer PID atom.
- Not a dengue / Holter / market predictor.
- Not Module CT. Lean is cited, not imported at runtime.

## Install

```bash
python -m pip install "systemictau-declare[report]"
# or from this repository
python -m pip install -e ".[report,dev]"
```

Requires `systemictau>=4.6.0,<5` and `nested-recd>=0.2.0`.

## Minimal example

```python
import numpy as np
from systemictau_declare import Protocol, declare, g0_independent_ar, write_report

X = g0_independent_ar(T=400, N=4, seed=0)
rep = declare(X, protocol=Protocol.frozen_v1())
assert rep.seal.far == "undefined"
assert rep.seal.event_claimed is False
write_report(rep, "report.html")
```

Any deviation from `frozen_v1` must go through `Protocol.exploratory(...)`.
The report is then marked **EXPLORATORY**. Weights cannot be `fit()`.

## Citation

See `CITATION.cff` and the paper in `papers/`.

- This version: [10.5281/zenodo.22237497](https://doi.org/10.5281/zenodo.22237497)
- Concept DOI (all versions): [10.5281/zenodo.22237496](https://doi.org/10.5281/zenodo.22237496)

## License

MIT. Author: Johel Padilla-Villanueva.

# Changelog

## 0.1.2 — 2026-09-01

Cold-install fix against the pins in `frozen_v1` (`systemictau>=4.6.0,<5`, `nested-recd>=0.2.0`). Protocol hash unchanged.

- Stop passing `compute_res=False` into `compute_recd_from_conjunctions`. On nested-recd 0.2.0 that kwarg is swallowed by `**alpha_kwargs` and `alpha_weights()` raises; 0.2.2+ already defaults it to False. `declare()` does not use Res_pair.
- Load `systemictau.core` / `.recd` / `.layers` even if `import systemictau` fails (PyPI 4.6.0 `panel.py` uses `Union` without importing it).

## 0.1.1 — 2026-09-01

- GitHub release for Zenodo archiving (hook enabled after v0.1.0).
- Software paper and usage manual as PDF assets.
- Zenodo version DOI: [10.5281/zenodo.22237497](https://doi.org/10.5281/zenodo.22237497) (concept [10.5281/zenodo.22237496](https://doi.org/10.5281/zenodo.22237496)).
- PyPI: [systemictau-declare 0.1.1](https://pypi.org/project/systemictau-declare/).

## 0.1.0 — 2026-09-01

- Initial companion package: `Protocol.frozen_v1`, `declare()`, FAR seal, CLI `recd-declare`.
- Tests: protocol hash, immutable weights, event-only seal, non-identification of \(\Delta T_n\) and \(\Delta\mathrm{excess}^3\), G0 fixture.
- Manual (`docs/MANUAL.md`) and software papers (`papers/`).

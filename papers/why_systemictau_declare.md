# Declaring the generator: why `systemictau-declare` exists, and what it is for

**Johel Padilla-Villanueva**  
Department of Environmental Health, University of Puerto Rico  
ORCID: [0000-0002-5797-6931](https://orcid.org/0000-0002-5797-6931)  
<johelpadilla@gmail.com>

Software paper, version 0.1.0 · 1 September 2026  
Package: `systemictau-declare` · Protocol: `frozen_v1`

---

## Abstract

The Systemic Tau / RECD programme already has a motor (`systemictau` 4.6), a nested ordinal layer (`nested-recd`), and a machine-checked confrontation between the RECD accumulant \(T_n\) and classical thermodynamic time (Module CT in Lean). What it did not have is a **citable operational contract**: a single function that (i) freezes the hyperparameters that scientific runs must share, (ii) reports laboratory time \(t\) and gate time \(T_n\) as distinct objects, (iii) compares the relational channel \((\Delta\tau_s,\,\Delta\mathrm{excess}^3)\) with the amplitude channel (variance, lag-1) without declaring a winner, and (iv) **refuses to claim an event when no controls were supplied**. `systemictau-declare` is that contract. Its top-level function is named `declare`, not `predict_outbreak`. This paper explains why that naming is the scientific contribution, what the package may be used for, and what it is forbidden to become.

**Keywords:** Systemic Tau, RECD, early-warning signals, protocol, false-alarm rate, software contract

---

## 1. The gap this package fills

A foundations paper can show that \(\tau_s\) is an ordinal concordance, that the RECD tick

\[
\Delta T_n = g(\tau_s)\,\delta^{-k}\,|\tau_s|
\]

is not the laboratory second, and that \(\mathrm{excess}^3 = 0.6\,\mathrm{Syn} + 0.4\,\mathrm{Surp}\) is a pre-specified Level-3 proxy rather than a Williams–Beer atom. Lean can discharge CT-1–CT-4 / OP-CT-8 with 0 `sorry`. None of that prevents a notebook from retuning \(\theta_3\) on the test season, identifying \(\Delta T_n\) with \(\Delta\mathrm{excess}^3\), and painting a red “outbreak risk” in a Streamlit app.

The failure mode is not lack of theory. It is lack of a **frozen entry point**. Epidemiology, Holter analysis, and synthetic maps were accumulating local thresholds. Sensitivity on events without a false-alarm rate was being read as a detector. The public API of `systemictau` still exports `compute_dengue_outbreak_risk` and `compute_market_crash_risk`. Those names teach the wrong verb.

`systemictau-declare` is deliberately small. It does not reimplement Kendall \(\tau\), the Feigenbaum gate, or `excess³`. It pins them, hashes the pin, and wraps them in a function whose return value includes a **seal**:

| `seal.far` | Meaning | `event_claimed` |
|------------|---------|-----------------|
| `undefined` | no controls | always false |
| `event-only` | events without matched controls | always false |
| `estimated` | controls present | true only if candidate **and** surrogate \(p < 0.05\) |

That table is the product. Everything else is instrumentation.

## 2. Why a package, not another preprint

The corpus already contains theory, Lean, `excess³` methods, dengue, Holter, RQA, and ontological notes — sometimes twice. Another synthesis would not change what a cardiologist or an epidemiologist can *run*. Three properties had to live in software, not in prose:

1. **Immutability of weights.** \(0.6/0.4\) is an a-priori design choice. There is no `fit()`. Assigning `Protocol.frozen_v1().weights` raises. Any other pair requires `Protocol.exploratory(...)` and marks the report.

2. **Non-identification in the schema.** \(\Delta T_n\) and \(\Delta\mathrm{excess}^3\) are two fields, two docstrings. A JSON dump that silently aliased them would be a scientific bug, not a style issue. Tests assert the alias does not exist.

3. **A FAR that cannot be omitted.** If `controls is None`, the seal is `FAR: undefined`. The HTML report prints it in a box. There is no code path from “sensitivity 1.0 on ten events” to a claimed alarm.

A paper can *recommend* these rules. A package can *enforce* them. That is why the artefact is Python.

## 3. What the package is for (intended use)

### 3.1 Declaring which generator is in play

Given \(X\in\mathbb{R}^{T\times N}\), `declare(X)` returns laboratory \(t\), gate \(T_n\), the sign of the tick \(g(\tau_s)\), renormalization depth, and a regime label (`stable` / `chaotic` / `anti-sync` / `intermediate`). In the stable band with frozen depth, Module CT says \(T_n\) is locally bi-Lipschitz to a discrete classical clock (CT-1). In recurrent anti-synchronization, no orientation-respecting bridge to a classical clock exists (CT-2, OP-CT-8). The package does not prove those theorems. It **exposes the regime in which they would apply**, so that a methods section can stop saying “time” as if it were unique.

### 3.2 Comparing two early-warning channels without a trophy

Classical EWS watch variance and lag-1 autocorrelation (critical slowing down). The relational channel watches \(\Delta\tau_s\) and \(\Delta\mathrm{excess}^3\). The scientifically interesting case is already reported in Holter work: the two relational increments can be extreme and sign-concordant with each other *while opposing the amplitude channel*. `declare()` always computes both channels and the two sign agreements. It never returns a “winner”. A later controlled paper can use this API as the frozen detector; it cannot use this API as a scoreboard.

### 3.3 Writing the paper that can fail

The missing empirical article is not another framework. It is a pre-registered, controlled test of relational versus amplitude channels (Holter with non-event controls; vector surveillance with non-outbreak seasons). That article should call `declare()` and nothing else. If the package is doing its job, a change of \(\theta_3\) after seeing the events is impossible without the word EXPLORATORY appearing on the report.

### 3.4 Giving studios a single hook

Existing Streamlit surfaces should call `declare()` or be frozen. They should not keep private copies of the gate. The CLI `recd-declare` is the app: CSV in, one-page HTML out. A wrapper of eighty lines is permitted. A new “ontology studio” is not.

## 4. What the package is not for

The following uses are in scope for the *programme* and out of scope for *this repository*:

- Closing CT-4C (Schnakenberg bridge). Lean lives in `systemic-tau-formal`. This package cites the pin; it does not import Lean.
- Identifying \(\Sigma^{\mathrm{RECD}}\) with Clausius production.
- Identifying \(\mathrm{excess}^3\) with \(\mathrm{Res}_{\mathrm{pair}}\) or with a PID synergy atom.
- Claiming retrocausality, or that a receding clock violates the second law. The split clock / production is exactly what allows \(\Sigma^{\mathrm{RECD}}\ge 0\) when \(T_n\) decreases.
- Replacing the SI second.
- Deploying a dengue dashboard to an agency before a paper with a defined FAR.
- Finance “crash risk” or any red-button predictor. Those names are the anti-pattern this package exists to starve.

A run that needs different \(B\), a permutation null, or a different window is legal. It is not `frozen_v1`. It is `Protocol.exploratory`, and the report says so.

## 5. Architecture (so the paper can be audited)

```
systemictau-declare
├── protocols/frozen_v1.yaml     pin + hash payload
├── protocol.py                  Protocol.frozen_v1 / .exploratory
├── run.py                       declare()
├── seals.py                     FAR logic
├── report.py                    one-page HTML
├── cli.py                       recd-declare
└── tests/                       hash, weights, seal, non-ID, G0
```

Runtime dependencies: `systemictau` (motor: `compute_taus`, `accumulate_time`, RQA) and `nested-recd` ( \(\Phi_{1,2,3}\), `excess3`). RQA is applied only inside the core-hyper mask (\(\lvert\tau_s\rvert<0.41\) with run length \(\ge 7\)). Inference is on the joint statistic \(\sqrt{(\Delta\tau_s)^2+(\Delta\mathrm{excess}^3)^2}\) against column-wise phase-shuffle surrogates (\(B=99\)), not on a difference of means.

The independent-AR fixture G0 is a negative control of the *software*: it must not produce `event_claimed=True`. It is not a proof that real series lack structure.

## 6. Epistemic labels

Every public object in this repository is one of:

- **[OPERATIONAL]** — `frozen_v1` numbers, including Feigenbaum \(\delta\) as a tick scale.
- **[THEOREM]** — none here. Theorems live in Module CT.
- **[CONJECTURE]** — none here. CT-4C is cited as open.
- **[READING]** — none here. Polo, Whitehead, and kairós are not imported.

The point of the package is to make mixing those labels *harder*, not to settle ontology.

## 7. How to cite, and what a citation means

Cite the software (this version) if you used `declare()` or `recd-declare` as the detector. Cite Module CT if you claim non-identity of \(T_n\) and \(t\) as a theorem. Cite the `excess³` methods DOI if you claim the hybrid proxy. Do not cite this package as evidence that a Holter series “proved extramental time”. The package cannot say that. Its most affirmative scientific sentence is:

> Under protocol `frozen_v1` (hash …), the relational contrast \((\Delta\tau_s,\,\Delta\mathrm{excess}^3)\) had surrogate \(p=\ldots\) relative to phase-shuffle; FAR was `undefined` | `event-only` | `estimated` (\(=\ldots\)). Laboratory lead, if reported, is in \(t\), not identified with \(\Delta T_n\).

If that sentence cannot be filled, the run is not yet a result.

## 8. Conclusion

`systemictau-declare` exists because a second time generator is only scientifically usable when the protocol that estimates it cannot quietly move, and when a missing control cannot be displayed as a detection. It is for declaring \(t\) versus \(T_n\), comparing relational and amplitude channels, and sealing FAR. It is not for prediction, ontology, or a fifth ecosystem. The rest of the programme — controlled Holter and dengue papers, CT-4C, studios — should call this API or explain why they will not.

---

## References (programme pins)

- Padilla-Villanueva, J. *Systemic Tau and Hierarchical Ordinal Conjunctions: A Relational Theory of Critical Transitions* (foundations manuscript, 2026).
- `nested-recd` 0.2.x, DOI [10.5281/zenodo.21937204](https://doi.org/10.5281/zenodo.21937204).
- `excess³` methods, DOI [10.5281/zenodo.21385937](https://doi.org/10.5281/zenodo.21385937).
- Module CT, `systemic-tau-formal` v0.1.11, DOI [10.5281/zenodo.21581189](https://doi.org/10.5281/zenodo.21581189).
- Scheffer, M. et al. (2009). Early-warning signals for critical transitions. *Nature*.
- Bandt, C. & Pompe, B. (2002). Permutation entropy. *Phys. Rev. Lett.*
- Marwan, N. et al. (2007). Recurrence plots for the analysis of complex systems. *Phys. Rep.*

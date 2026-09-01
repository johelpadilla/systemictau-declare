# Manual de uso — systemictau-declare 0.1.0

Este manual es el contrato operativo. Si un paso no está aquí, no forma
parte de `frozen_v1`.

## 1. Instalación

```bash
python -m pip install "systemictau-declare[report]"
```

Compruebe las versiones:

```python
import systemictau, nested_recd, systemictau_declare
print(systemictau.__version__)          # 4.6.x
print(nested_recd.__version__)          # >= 0.2.0
print(systemictau_declare.__version__)  # 0.1.0
```

## 2. Datos de entrada

Una matriz \(X \in \mathbb{R}^{T \times N}\) con \(N \ge 2\).

CSV aceptado por el CLI:

| t | x1 | x2 | x3 |
|---|----|----|----|
| 0 | …  | …  | …  |

- La columna `t` / `time` / `week` / `index` es opcional. Si existe, es el
  **tiempo de laboratorio** (codificador). No es \(T_n\).
- Las demás columnas son variables. No se interpola hacia adelante.
- No hay umbral de “riesgo de brote” en el archivo.

## 3. El protocolo congelado (`frozen_v1`)

```python
from systemictau_declare import Protocol
P = Protocol.frozen_v1()
assert P.weights == (0.6, 0.4)
print(P.yaml_hash)
```

| Campo | Valor | Etiqueta |
|-------|-------|----------|
| `window` | 13 | operacional |
| `m` | 3 | operacional (Bandt–Pompe) |
| `theta3` | 0.08 | operacional (binario \(\Phi_3\); la lectura primaria es continua) |
| `alpha_syn`, `alpha_surp` | 0.6, 0.4 | a priori; nunca `fit()` |
| `tau_st`, `tau_ch` | 0.50, 0.41 | bandas de la compuerta |
| `detector` | `abs_z_vs_basal` | contraste vs primer 30 % |
| `surrogate` | `phase_shuffle` | inferencia sobre el estadístico **conjunto** |
| `B` | 99 | número de surrogados |
| `rqa` | `core_hyper_only` | LAM/TT solo dentro de \(\lvert\tau_s\rvert < 0.41\) con racha ≥ 7 |

Cualquier desvío:

```python
P = Protocol.exploratory(B=19, surrogate="permute")
# el informe sale marcado EXPLORATORY
```

No existe `Protocol.fit`. No existe `declare(...).tune()`.

## 4. La función `declare`

```python
from systemictau_declare import declare, Protocol

rep = declare(X, time=t, protocol=Protocol.frozen_v1(), controls=None)
```

`rep` trae, alineados al índice de \(t\):

| Campo | Qué es | Qué no es |
|-------|--------|-----------|
| `tau_s` | coherencia ordinal (media de Kendall por pares) | varianza |
| `gate.T_n`, `gate.dT`, `gate.g`, `gate.depth` | generador gate RECD | `excess3` |
| `nested.excess3`, `Phi1/2/3` | profundidad nested | \(\Delta T_n\) |
| `regime` | stable / chaotic / anti-sync / intermediate | diagnóstico clínico |
| `lam_core`, `tt_core` | RQA **solo** en núcleo hiperpersistente | RQA global |
| `amp.variance`, `amp.lag1` | canal de amplitud, para contrastar signo | EWS que “gana” |
| `delta_tau_s`, `nested.delta_excess3` | contraste vs basal | lead time causal |
| `p_surrogate` | p sobre \(\sqrt{(\Delta\tau_s)^2+(\Delta\mathrm{excess}^3)^2}\) | media contra media |
| `seal` | FAR | botón rojo |

### Sellos FAR

| `seal.far` | Cuándo | `event_claimed` |
|------------|--------|-----------------|
| `undefined` | `controls is None` | siempre `False` |
| `event-only` | `event_only=True` sin controles | siempre `False` |
| `estimated` | hay controles | `True` solo si hay candidato **y** \(p < 0.05\) |

Sensibilidad 1.0 en eventos con FAR indefinida **no es un resultado
publicable de alarma**. El paquete se niega a fingirlo.

## 5. CLI

```bash
recd-declare data.csv --protocol frozen_v1 --out report.html
recd-declare data.csv --controls controls.csv --out report.html
recd-declare data.csv --event-only --out report.html
recd-declare data.csv --controls ./controls_dir/ --json summary.json --out report.html
```

`--B N` está permitido y **marca el run como exploratorio**.
El CLI no acepta otro protocolo que `frozen_v1`. Para desviaciones use Python.

El HTML abre con:

1. los dos relojes (\(t\) vs \(T_n\));
2. \(\tau_s\) y `excess³` frente a varianza;
3. el sello FAR;
4. la lista de no-identificaciones.

No hay ontología, no hay Polo, no hay “riesgo de crash”.

## 6. Controles

`controls` es una secuencia de matrices, cada una un registro de control
(Holter sin evento, temporada sin brote, ciudad negativa). El FAR estimado
es la fracción de controles que disparan el mismo detector `abs_z_vs_basal`.

Un solo archivo CSV se trata como un control. Un directorio de CSV se trata
como varios.

## 7. Surrogados

La inferencia no es “la media de \(\tau_s\) cambió”. Es el estadístico
conjunto \((\Delta\tau_s,\,\Delta\mathrm{excess}^3)\) bajo barajado de fase
independiente por columna (IAAFT en `nested-recd`). p usa suavizado
\((1 + \#\{|n| \ge |o|\})/(1+B)\).

`permute` (permutación temporal por columna) solo es legal en
`Protocol.exploratory`.

## 8. Lo que el informe se niega a identificar

Estas frases están en el YAML y se copian a cada reporte:

- \(\Delta T_n\) (gate RECD) no es \(\Delta\mathrm{excess}^3\) (Level-3 nested).
- \(\Sigma^{\mathrm{RECD}}\) no es producción de Clausius / Schnakenberg (CT-4C abierto).
- \(\Phi_3\) binario no es la lectura primaria de Level-3; lo es `excess3` continuo.
- El adelanto, si se afirma, se afirma en \(t\) de laboratorio; no se identifica con \(\Delta T_n\).

## 9. Tests que importan más que features

```bash
pytest
```

Cubren:

- hash de `frozen_v1` estable;
- `weights == (0.6, 0.4)` y ausencia de setter / `fit`;
- `controls is None` ⇒ `FAR: undefined`;
- \(\Delta T_n\) y \(\Delta\mathrm{excess}^3\) no se identifican en el schema;
- fixture G0 (AR independientes) no dispara sello de evento.

## 10. Relación con el resto del ecosistema

| Repo | Rol |
|------|-----|
| `systemictau` 4.6.x | motor: `compute_taus`, `accumulate_time` |
| `nested-recd` ≥ 0.2 | \(\Phi_1\)–\(\Phi_3\), `excess3 = 0.6 Syn + 0.4 Surp` |
| `systemic-tau-formal` | Lean Module CT — **no** se importa en runtime |
| `cctp-sddb-systemic-tau` | cliente del protocolo, no otro motor |
| Studios Streamlit | se enganchan a `declare()` o se congelan |

Una sola función de entrada para ciencia que quiera citarse.

## 11. Limitaciones honestas

- `B=99` con phase-shuffle es lento. Eso es el costo del protocolo, no un bug.
- Sin controles, el paquete **no** estima FAR. Punto.
- El Holter SDDB histórico (solo eventos) debe llamarse con `event_only=True`.
- Feigenbaum \(\delta\) es escala operativa del tic, no ley demostrada de la naturaleza.
- Este software no cierra CT-4C.

## 12. Reproducir el informe de ejemplo

```bash
python examples/demo_declare.py
# escribe examples/demo_report.html
```

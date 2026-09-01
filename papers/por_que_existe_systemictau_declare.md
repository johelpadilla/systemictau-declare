# Por qué existe `systemictau-declare`, y para qué

**Johel Padilla-Villanueva**  
Universidad de Puerto Rico · ORCID 0000-0002-5797-6931  
1 de septiembre de 2026 · software 0.1.1 · protocolo `frozen_v1`

Este texto es la versión en español del paper de software
[`why_systemictau_declare.md`](why_systemictau_declare.md). No es una
nueva teoría del tiempo. Es la justificación del *paquete*.

---

## La frase que el paquete materializa

> El tiempo no es un solo objeto; uno de esos objetos puede construirse a
> partir de concordancia ordinal, chequearse en Lean, estimarse en ventanas
> y —en regímenes concretos— adelantar reorganizaciones que el tiempo de
> laboratorio y la varianza no ven; y todo eso puede afirmarse sin confundir
> teorema, protocolo y metafísica.

Esa frase ya tenía Lean, tenía \(\tau_s\), tenía `excess³`. No tenía un
objeto de software que **obligara** a no confundir las capas. Cada
notebook de dengue o de Holter podía (y a veces debía) retocar un umbral.
El API público de `systemictau` todavía ofrece `compute_dengue_outbreak_risk`
y `compute_market_crash_risk`. Esos nombres enseñan el verbo equivocado.

`systemictau-declare` existe para cambiar el verbo: **declarar** el
generador, no **predecir** el brote.

## Para qué sirve

1. **Congelar el protocolo** antes de ver los eventos de test. Ventana 13,
   \(m=3\), \(\theta_3=0.08\), pesos \(0.6/0.4\), detector \(|z|\) vs basal,
   surrogato de fase sobre el estadístico conjunto \((\Delta\tau_s,\,\Delta\mathrm{excess}^3)\),
   RQA solo en el núcleo hiperpersistente. El YAML se hashea. Si alguien
   cambia \(\theta_3\), el informe se llama exploratorio.

2. **Mostrar dos relojes** en la primera página: \(t\) de muestreo y \(T_n\)
   gated. En régimen estable con profundidad congelada se parecen (CT-1).
   En anti-sincronización no hay puente que respete orientación (CT-2).
   El paquete no demuestra eso; **diagnostica el régimen** en el que
   aplicaría.

3. **Comparar canal relacional y canal de amplitud** sin copa. El hallazgo
   valioso no es “ganamos a la varianza”. Es si \(\Delta\tau_s\) y
   \(\Delta\mathrm{excess}^3\) concuerdan en signo *aunque* vayan contra
   el aumento clásico de fluctuación.

4. **Sellar la falsa alarma.** Sin controles, `FAR: undefined` y
   `event_claimed = False`. Solo eventos: `event-only`. Con controles:
   `estimated`. Sensibilidad 1.0 en diez Holters de FV sin FAR no puede
   salir de este paquete como alarma.

5. **Ser la API del paper empírico que falta.** El artículo controlado
   (Holter + no-evento; dengue/trampas + temporadas sin brote) debe
   llamarse contra `declare()`, no contra un umbral local del notebook.

## Para qué no sirve

- No sustituye el segundo de cesio.
- No cierra CT-4C ni llama a \(\Sigma^{\mathrm{RECD}}\) producción de Clausius.
- No convierte `excess³` en un átomo de Williams–Beer.
- No demuestra retrocausalidad. Un reloj que retrocede no viola la
  termodinámica: reloj y producción son objetos distintos.
- No es un dashboard para agencias antes del paper con FAR.
- No es un Studio de ontología del presente.
- No reimplementa el motor: llama a `systemictau` y `nested-recd`.

## Cómo se usa, en tres líneas

```python
from systemictau_declare import Protocol, declare
rep = declare(X, protocol=Protocol.frozen_v1(), controls=None)
print(rep.seal.far)   # 'undefined' — no hay evento reclamado
```

```bash
recd-declare data.csv --protocol frozen_v1 --out report.html
```

El manual completo está en [`docs/MANUAL.md`](../docs/MANUAL.md).

## Lo que cambiaría si este paquete se volviera el default

No cambiaría Newton en el laboratorio. Cambiaría el hábito de paper:

- dejaría de ser lícito publicar un EWS que “adelanta seis semanas” sin
  decir *en qué generador*, con qué signo frente a la varianza, con qué
  pesos, y con qué FAR;
- los Studios dejarían de tener umbrales privados;
- un revisor podría pedir el hash de `frozen_v1` igual que pide la semilla
  de la simulación.

Eso es menos romántico que una ontología del persistir, y más útil. El
persistir, Polo y Whitehead siguen siendo lectura. El paquete se niega a
mezclarlos con el YAML.

## Cierre

`systemictau-declare` existe para que “hay un segundo generador de tiempo”
pueda afirmarse como **protocolo verificable**, no como literatura, y para
que esa afirmación se caiga cuando faltan controles o cuando alguien
retoca los pesos sobre el mismo dataset. El resto del programa —FAR en
Holter, dengue con temporadas negativas, CT-4C— es trabajo. Este paquete
es la herramienta que no deja mentir mientras ese trabajo se hace.

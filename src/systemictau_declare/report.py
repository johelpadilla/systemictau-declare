"""One-page HTML report. No ontology, no red crash button."""

from __future__ import annotations

import html
from pathlib import Path
from typing import Optional, Union

import numpy as np

from .schema import DeclarationReport

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from io import BytesIO
    import base64

    _HAS_MPL = True
except Exception:
    _HAS_MPL = False


def _fig_to_data_uri(fig) -> str:
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def _two_clocks_figure(rep: DeclarationReport) -> Optional[str]:
    if not _HAS_MPL:
        return None
    t = np.asarray(rep.t)
    fig, axes = plt.subplots(3, 1, figsize=(8.2, 6.4), sharex=True)
    axes[0].plot(t, rep.tau_s, color="#1f4e79", lw=1.2)
    axes[0].axhline(0.50, color="#2e7d32", ls="--", lw=0.8, label=r"$\tau_{st}=0.50$")
    axes[0].axhline(0.41, color="#ef6c00", ls=":", lw=0.8)
    axes[0].axhline(-0.41, color="#c62828", ls="--", lw=0.8, label=r"$\tau_{ch}=\pm 0.41$")
    axes[0].set_ylabel(r"$\tau_s$")
    axes[0].legend(loc="upper right", fontsize=7, frameon=False)
    axes[0].set_title("Laboratory index vs RECD accumulant (two clocks)")

    axes[1].plot(t, rep.gate.T_n, color="#6a1b9a", lw=1.2)
    axes[1].set_ylabel(r"$T_n$ (gate RECD)")

    axes[2].plot(t, rep.nested.excess3, color="#00695c", lw=1.2, label=r"excess$^3$")
    axes[2].plot(t, rep.amp.variance, color="#90a4ae", lw=1.0, alpha=0.85, label="variance")
    axes[2].set_ylabel("depth / amplitude")
    axes[2].set_xlabel("laboratory t")
    axes[2].legend(loc="upper right", fontsize=7, frameon=False)
    fig.tight_layout()
    return _fig_to_data_uri(fig)


def _fmt(x, digits=4):
    if x is None:
        return "—"
    try:
        v = float(x)
    except (TypeError, ValueError):
        return html.escape(str(x))
    if not np.isfinite(v):
        return "—"
    return f"{v:.{digits}g}"


def render_html(rep: DeclarationReport) -> str:
    s = rep.summary()
    seal = rep.seal
    img = _two_clocks_figure(rep)
    img_tag = f'<img alt="two clocks" src="{img}"/>' if img else "<p><em>matplotlib not installed; clocks omitted.</em></p>"
    mark = "EXPLORATORY" if rep.exploratory else "FROZEN v1"
    far_color = {
        "undefined": "#b71c1c",
        "event-only": "#e65100",
        "estimated": "#1b5e20",
    }.get(seal.far, "#333")
    non_id = "".join(f"<li>{html.escape(x)}</li>" for x in rep.non_identification)
    notes = "".join(f"<li>{html.escape(x)}</li>" for x in rep.notes)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>RECD declaration — {html.escape(rep.protocol_name)}</title>
<style>
  body {{ font-family: "Palatino Linotype", Palatino, serif; margin: 28px auto; max-width: 820px; color: #1a1a1a; }}
  h1 {{ font-size: 1.35rem; margin-bottom: 0.2rem; }}
  .sub {{ color: #555; margin-top: 0; }}
  .seal {{ border: 2px solid {far_color}; padding: 10px 14px; margin: 16px 0; }}
  .seal strong {{ color: {far_color}; }}
  table {{ border-collapse: collapse; width: 100%; margin: 12px 0 20px; font-size: 0.92rem; }}
  th, td {{ border: 1px solid #ccc; padding: 6px 8px; text-align: left; }}
  th {{ background: #f4f4f4; width: 42%; }}
  img {{ width: 100%; height: auto; }}
  .mark {{ display: inline-block; font-size: 0.75rem; letter-spacing: 0.08em; border: 1px solid #333; padding: 2px 8px; }}
  footer {{ font-size: 0.8rem; color: #555; margin-top: 24px; }}
  code {{ font-family: Menlo, Consolas, monospace; font-size: 0.85em; }}
</style>
</head>
<body>
<p class="mark">{html.escape(mark)}</p>
<h1>Declaration of the time generator</h1>
<p class="sub">systemictau-declare 0.1.1 · protocol hash <code>{html.escape(rep.protocol_hash[:16])}</code></p>

<div class="seal">
  <strong>FAR: {html.escape(seal.far)}</strong>
  {" · value " + _fmt(seal.far_value) if seal.far_value is not None else ""}
  <br/>event candidate: {str(seal.event_candidate).lower()}
  · event claimed: {str(seal.event_claimed).lower()}
  <br/>{html.escape(seal.reason)}
</div>

{img_tag}

<table>
  <tr><th>Shape (T, N)</th><td>{rep.X_shape[0]} × {rep.X_shape[1]}</td></tr>
  <tr><th>Δτ<sub>s</sub> (contrast − basal)</th><td>{_fmt(s["delta_tau_s"])} &nbsp; z = {_fmt(s["z_tau_s"])}</td></tr>
  <tr><th>Δ excess<sup>3</sup></th><td>{_fmt(s["delta_excess3"])} &nbsp; z = {_fmt(s["z_excess3"])}</td></tr>
  <tr><th>Δ T<sub>n</sub> (gate RECD, not identified with excess<sup>3</sup>)</th><td>{_fmt(s["delta_T_n"])}</td></tr>
  <tr><th>Δ variance (amplitude channel)</th><td>{_fmt(s["delta_variance"])}</td></tr>
  <tr><th>Sign(Δτ<sub>s</sub>, Δ excess<sup>3</sup>)</th><td>{s["sign_tau_excess3"]} &nbsp; (+1 concordant, −1 discordant, 0 undefined)</td></tr>
  <tr><th>Sign(Δτ<sub>s</sub>, Δ variance)</th><td>{s["sign_tau_variance"]}</td></tr>
  <tr><th>Surrogate p (joint |Δτ<sub>s</sub>, Δ excess<sup>3</sup>|)</th><td>{_fmt(s["p_surrogate"])} &nbsp; B = {rep.n_surrogates} &nbsp; {html.escape(rep.surrogate_method)}</td></tr>
  <tr><th>Core-hyper RQA points</th><td>{int(np.sum(rep.core_hyper))}</td></tr>
</table>

<h2>What this report does not say</h2>
<ul>{non_id}</ul>
<ul>{notes}</ul>

<footer>
Versions: systemictau {html.escape(rep.versions.get("systemictau", "?"))}
 · nested-recd {html.escape(rep.versions.get("nested_recd", "?"))}
 · declare {html.escape(rep.versions.get("systemictau_declare", "?"))}<br/>
The top-level function is <code>declare</code>, not <code>predict_outbreak</code>.
</footer>
</body>
</html>
"""


def write_report(
    rep: DeclarationReport, path: Union[str, Path]
) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = render_html(rep)
    path.write_text(text, encoding="utf-8")
    return path

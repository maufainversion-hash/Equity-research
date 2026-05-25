"""
Compare radar chart — 6-axis profile comparison.

One Plotly polar trace per ticker. Six axes, each ticker's raw value
normalised to 0-100 across the *selected group* (not the entire
universe) so the radar shows relative positioning, not absolute
rankings.

Axes (default):
- Gross margin %        (higher is better)
- Operating margin %    (higher is better)
- FCF margin %          (higher is better)
- ROIC %                (higher is better)
- Revenue CAGR 5y %     (higher is better)
- Quality of growth     (inverted leverage: 100 = D/E ≤ 0.25; 0 = D/E ≥ 3)

The inverted leverage axis means a clean balance sheet always
helps the radar shape; high leverage punishes it. That keeps "more
area = better" intuitive across all six axes.

Reads the same ``_Headline`` objects the verdict-cards + heatmap
table already build, so no extra computation per ticker.
"""
from __future__ import annotations
from typing import Optional

import math
import streamlit as st


# Trace colours (matches the rest of Compare)
_TRACE_COLORS = ["#3B82F6", "#C9A961", "#10B981"]


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    """Convert a "#RRGGBB" string to ``rgba(r,g,b,alpha)``.

    Plotly's strict colour validator rejects 8-digit hex
    (``#RRGGBBAA``), so the fill colour has to go in as
    rgba(). Falls back to ``rgba(128,128,128,alpha)`` on a
    malformed input — never raises into the chart render."""
    s = (hex_color or "").lstrip("#")
    if len(s) != 6:
        return f"rgba(128,128,128,{alpha})"
    try:
        r = int(s[0:2], 16)
        g = int(s[2:4], 16)
        b = int(s[4:6], 16)
        return f"rgba({r},{g},{b},{alpha})"
    except ValueError:
        return f"rgba(128,128,128,{alpha})"


# Absolute thresholds per metric: (value at 0, value at 100).
# A linear ramp between the two, clamped 0..100 outside.
#
# Why absolute and not min-max-within-the-pair: with only 2 tickers
# min-max always plots one as 100 and the other as 0 on every axis,
# which collapses the visual into "one full polygon, one dot" and
# carries zero information about quality. Absolute thresholds make
# each ticker readable on its own — a great company looks great
# regardless of who it's compared against.
#
# Thresholds calibrated to equity-research convention: the "100"
# end is roughly best-in-class; the "0" end is breakeven (or 0% for
# scale-free metrics like ROIC). Tweak the constants if a different
# anchor makes sense.
_AXIS_SCALES: dict[str, tuple[float, float]] = {
    "Gross margin":     (0.0,  70.0),
    "Op margin":        (0.0,  35.0),
    "FCF margin":       (0.0,  30.0),
    "ROIC":             (0.0,  40.0),
    "Revenue 5y CAGR":  (0.0,  25.0),
    "Balance strength": (0.0, 100.0),     # already on a 0-100 scale
}


def _normalize_to_100(value: Optional[float], axis: str) -> float:
    """Map an absolute raw value onto a 0..100 quality scale for the
    given axis. Missing data returns 50 so the polygon still closes."""
    if value is None or not math.isfinite(value):
        return 50.0
    lo, hi = _AXIS_SCALES.get(axis, (0.0, 100.0))
    if hi == lo:
        return 50.0
    pct = (value - lo) / (hi - lo) * 100.0
    return max(0.0, min(100.0, pct))


def _leverage_score(de: Optional[float]) -> Optional[float]:
    """Map Debt/Equity → 0..100 where 100 = clean balance sheet.

    Piecewise: 100 below 0.25, linear down to 0 between 0.25 and 3.0,
    floored at 0 beyond 3.0. Returns None when D/E is missing — the
    normaliser then assigns 50."""
    if de is None or not math.isfinite(de) or de < 0:
        return None
    if de <= 0.25:
        return 100.0
    if de >= 3.0:
        return 0.0
    return 100.0 * (1.0 - (de - 0.25) / (3.0 - 0.25))


def _name_root(name: str) -> str:
    """Strip share-class suffixes so "Alphabet Inc. — Class A" and
    "Alphabet Inc. — Class C" reduce to the same root for duplicate
    detection."""
    s = (name or "").lower()
    for marker in (" — ", " - ", " (", " class "):
        if marker in s:
            s = s.split(marker, 1)[0]
    return s.strip().rstrip(",.")


def render_compare_radar(headlines: list) -> None:
    """Render a polar radar chart comparing the headline metrics.

    ``headlines`` is the list emitted by
    :func:`ui.components.compare_summary.build_headlines`."""
    if not headlines or len(headlines) < 2:
        return

    try:
        import plotly.graph_objects as go
    except ImportError:
        return

    axes = [
        "Gross margin", "Op margin", "FCF margin",
        "ROIC", "Revenue 5y CAGR", "Balance strength",
    ]

    # Collect raw values per ticker, per axis.
    raw: dict[str, list[Optional[float]]] = {}
    for h in headlines:
        m = h.metrics
        raw[h.ticker] = [
            m.get("Gross margin %"),
            m.get("Op margin %"),
            m.get("FCF margin %"),
            m.get("ROIC %"),
            m.get("Revenue CAGR 5y %"),
            _leverage_score(m.get("Debt/Equity")),
        ]

    # Drop tickers that have <3 usable metrics — plotting them would
    # be a flat polygon-of-50s that just clutters the chart and the
    # legend. Most common offender: provider returned an empty bundle
    # (e.g. GOOG when GOOGL already pulled the financials).
    skipped: list[str] = []
    usable: list = []
    for h in headlines:
        n_finite = sum(1 for v in raw[h.ticker]
                       if v is not None and math.isfinite(v))
        if n_finite < 3:
            skipped.append(h.ticker)
        else:
            usable.append(h)

    if len(usable) < 2:
        # Not enough material for a useful radar — render nothing,
        # but tell the user why.
        st.markdown(
            '<div class="eq-section-label" style="margin-top:18px;">'
            'RADAR · 6-AXIS PROFILE</div>',
            unsafe_allow_html=True,
        )
        st.caption(
            "Radar omitido: no hay suficientes datos por ticker para "
            "trazarlo. Probablemente uno o más tickers caen en clases "
            "de acciones cuyos financials no están disponibles "
            "(ej.: clase A vs clase C del mismo emisor)."
        )
        return

    # Same-issuer pair detection (e.g. GOOG + GOOGL). Warn the user;
    # don't filter — they explicitly chose both.
    name_roots = [_name_root(h.name) for h in usable]
    dupes: list[str] = []
    seen: dict[str, str] = {}
    for h, root in zip(usable, name_roots):
        if root and root in seen:
            dupes.append(f"{seen[root]} y {h.ticker}")
        else:
            seen[root] = h.ticker

    st.markdown(
        '<div class="eq-section-label" style="margin-top:18px;">'
        'RADAR · 6-AXIS PROFILE</div>',
        unsafe_allow_html=True,
    )

    # Lower the fill alpha when 3 traces are stacked — keeps each
    # polygon distinguishable instead of muddying into one shape.
    fill_alpha = 0.18 if len(usable) <= 2 else 0.10

    fig = go.Figure()
    for idx, h in enumerate(usable):
        scores: list[float] = []
        hover: list[str] = []
        for i in range(len(axes)):
            v = raw[h.ticker][i]
            s = _normalize_to_100(v, axes[i])
            scores.append(s)
            if v is None or not math.isfinite(v):
                hover.append(f"{axes[i]}: —")
            elif i == 5:                                  # leverage already 0-100
                hover.append(f"{axes[i]}: {v:.0f}/100")
            else:
                hover.append(f"{axes[i]}: {v:.1f}%")
        # Close the polygon
        scores.append(scores[0])
        hover.append(hover[0])
        theta = axes + [axes[0]]
        color = _TRACE_COLORS[idx % len(_TRACE_COLORS)]
        fig.add_trace(go.Scatterpolar(
            r=scores, theta=theta,
            name=h.ticker,
            fill="toself",
            fillcolor=_hex_to_rgba(color, fill_alpha),
            line=dict(color=color, width=2.2),
            marker=dict(size=6, color=color),
            hovertext=hover,
            hoverinfo="text+name",
        ))

    fig.update_layout(
        polar=dict(
            bgcolor="#131826",
            radialaxis=dict(
                visible=True, range=[0, 100],
                gridcolor="#1F2937", linecolor="#1F2937",
                tickfont=dict(color="#4B5563", size=9),
                tickvals=[25, 50, 75, 100],
            ),
            angularaxis=dict(
                gridcolor="#1F2937", linecolor="#334155",
                tickfont=dict(color="#9CA3AF", size=11),
            ),
        ),
        showlegend=True,
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.08,
            xanchor="center", x=0.5,
            bgcolor="rgba(0,0,0,0)", font=dict(color="#E8EAED"),
        ),
        paper_bgcolor="#131826",
        height=440,
        margin=dict(l=40, r=40, t=20, b=20),
    )
    st.plotly_chart(fig, width="stretch",
                    config={"displayModeBar": False})
    # Warnings (skipped tickers + same-issuer pairs) — surface them so
    # the user understands why the chart looks different from input.
    if skipped:
        st.warning(
            f"Omitidos del radar por datos insuficientes: "
            f"{', '.join(skipped)}. Probable caso de clases de acción "
            f"sin financials independientes (ej.: GOOG vs GOOGL).",
            icon="⚠️",
        )
    if dupes:
        st.info(
            f"Aviso: {', '.join(dupes)} parecen ser distintas clases "
            f"del mismo emisor — sus polígonos van a coincidir.",
            icon="ℹ️",
        )

    st.caption(
        "Escala absoluta de calidad, no relativa al par. 100 = nivel "
        "best-in-class del eje (Gross margin 70%, Op margin 35%, "
        "FCF margin 30%, ROIC 40%, Revenue CAGR 25%, Balance strength = "
        "D/E ≤ 0.25). 0 = breakeven. Cada empresa se lee por sí misma — "
        "la forma del polígono refleja calidad, no posición relativa."
    )

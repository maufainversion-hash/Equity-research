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


def _normalize_to_100(
    value: Optional[float], all_values: list[Optional[float]],
    higher_better: bool = True,
) -> float:
    """Min-max scale ``value`` to 0..100 against the peer group.

    Returns 50 for missing values / no spread — keeps the polygon
    closed instead of poking towards origin and looking like a
    "weak" axis when really we have no data."""
    clean = [v for v in all_values if v is not None and math.isfinite(v)]
    if not clean or value is None or not math.isfinite(value):
        return 50.0
    lo, hi = min(clean), max(clean)
    if hi == lo:
        return 50.0
    pct = (value - lo) / (hi - lo) * 100.0
    return pct if higher_better else (100.0 - pct)


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

    st.markdown(
        '<div class="eq-section-label" style="margin-top:18px;">'
        'RADAR · 6-AXIS PROFILE</div>',
        unsafe_allow_html=True,
    )

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

    # Normalise per-axis: peer-group min-max → 0..100.
    per_axis_values: list[list[Optional[float]]] = []
    for i in range(len(axes)):
        per_axis_values.append([raw[h.ticker][i] for h in headlines])

    fig = go.Figure()
    for idx, h in enumerate(headlines):
        scores: list[float] = []
        hover: list[str] = []
        for i in range(len(axes)):
            v = raw[h.ticker][i]
            s = _normalize_to_100(v, per_axis_values[i], higher_better=True)
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
            fillcolor=color.replace(")", ",0.18)").replace("rgb", "rgba")
                       if color.startswith("rgb") else f"{color}30",
            line=dict(color=color, width=2),
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
    st.caption(
        "Cada eje se normaliza 0–100 dentro del grupo seleccionado "
        "(0 = peor del grupo, 100 = mejor). Balance strength se deriva "
        "de Debt/Equity: 100 si D/E ≤ 0.25, 0 si D/E ≥ 3."
    )

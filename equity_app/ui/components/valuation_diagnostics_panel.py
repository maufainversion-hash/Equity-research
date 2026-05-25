"""
Valuation diagnostics — sensitivity matrix + MoS + DCF cross-checks.

Three pieces, all rendered against an already-computed
:class:`core.valuation_pipeline.ValuationResults`:

- :func:`render_valuation_diagnostics_cards` — Margin of Safety,
  Terminal Value % of PV, Implied steady-state ROIC, each in a
  small card with a colour flag (green / gold / red).
- :func:`render_sensitivity_matrix` — 5×5 grid of intrinsic value
  per share over (WACC ±0.5pp/1pp) × (g_terminal ±0.5pp/1pp). Each
  cell shows the implied price and a heat colour for upside %
  versus current price.

The sensitivity matrix re-runs the DCF 25 times. Each run is fast
(~50ms on cached statements) because we pass the pre-computed
``reorg`` / ``lifecycle`` / ``growth`` invariants — that's the
whole reason ``run_dcf`` accepts them as kwargs.
"""
from __future__ import annotations
from typing import Optional, Any

import math
import numpy as np
import pandas as pd
import streamlit as st


# ============================================================
# Card-style diagnostics row
# ============================================================
def _flag_color(flag: str) -> tuple[str, str]:
    """(bg-with-alpha, fg) per status."""
    return {
        "green":  ("#10B98122", "#10B981"),
        "gold":   ("#C9A96122", "#C9A961"),
        "red":    ("#EF444422", "#F87171"),
        "muted":  ("#33415522", "#94A3B8"),
    }.get(flag, ("#33415522", "#94A3B8"))


def _diag_card(label: str, value: str, flag: str, sub: str) -> str:
    bg, fg = _flag_color(flag)
    return (
        f'<div style="background:#0f172a;border:1px solid #334155;'
        f'border-left:3px solid {fg};border-radius:8px;'
        f'padding:14px 16px;">'
        f'<div style="font-size:10px;color:#94A3B8;letter-spacing:0.08em;'
        f'text-transform:uppercase;margin-bottom:6px;">{label}</div>'
        f'<div style="font-size:22px;font-weight:700;color:{fg};'
        f'font-variant-numeric:tabular-nums;line-height:1.1;">{value}</div>'
        f'<div style="font-size:11px;color:#94A3B8;margin-top:4px;'
        f'line-height:1.4;">{sub}</div>'
        f'</div>'
    )


def render_valuation_diagnostics_cards(results: Any) -> None:
    """3 small cards: MoS, Terminal Value % of PV, Implied steady ROIC.

    Reads from ``results.aggregator`` (margin_of_safety,
    dcf_terminal_pct, dcf_implied_ronic, dcf_health_flags) — these
    are populated by ``core.valuation_pipeline.run_valuation``."""
    agg = getattr(results, "aggregator", None)
    if agg is None:
        return

    mos = getattr(agg, "margin_of_safety", None)
    tv_pct = getattr(agg, "dcf_terminal_pct", None)
    ronic = getattr(agg, "dcf_implied_ronic", None)
    flags = list(getattr(agg, "dcf_health_flags", []) or [])

    # Hide entirely when there's nothing to show.
    if mos is None and tv_pct is None and ronic is None:
        return

    st.markdown(
        '<div class="eq-section-label" style="margin-top:14px;">'
        'VALUATION DIAGNOSTICS</div>',
        unsafe_allow_html=True,
    )

    cards: list[str] = []

    # 1. Margin of safety vs the conservative range_p25
    if mos is not None and math.isfinite(mos):
        if mos > 0.20:
            flag = "green"; sub = "Incluso el escenario conservador deja upside material."
        elif mos > 0:
            flag = "gold"; sub = "Margen positivo pero estrecho."
        else:
            flag = "red";  sub = "El extremo conservador del rango ya está por debajo del precio."
        cards.append(_diag_card(
            "Margin of safety", f"{mos*100:+.1f}%", flag, sub,
        ))
    else:
        cards.append(_diag_card(
            "Margin of safety", "—", "muted",
            "Sin rango intrínseco computable.",
        ))

    # 2. Terminal value as % of total DCF PV
    if tv_pct is not None and math.isfinite(tv_pct):
        if tv_pct > 0.75:
            flag = "red"; sub = "Modelo muy dependiente de la perpetuidad — alta sensibilidad."
        elif tv_pct > 0.60:
            flag = "gold"; sub = "Peso terminal alto, típico en growth — controlar assumptions."
        else:
            flag = "green"; sub = "Forecast explícito sostiene la mayor parte del valor."
        cards.append(_diag_card(
            "Terminal value / PV", f"{tv_pct*100:.0f}%", flag, sub,
        ))
    else:
        cards.append(_diag_card(
            "Terminal value / PV", "—", "muted",
            "DCF no aplicable o no se pudo descomponer.",
        ))

    # 3. Implied steady-state ROIC
    if ronic is not None and math.isfinite(ronic):
        if ronic > 0.25:
            flag = "red"; sub = "Asume retornos extraordinarios a perpetuidad."
        elif ronic > 0.15:
            flag = "gold"; sub = "Asume moat persistente bien por encima del WACC."
        else:
            flag = "green"; sub = "Retornos steady-state plausibles para una empresa madura."
        cards.append(_diag_card(
            "Implied steady ROIC", f"{ronic*100:.1f}%", flag, sub,
        ))
    else:
        cards.append(_diag_card(
            "Implied steady ROIC", "—", "muted",
            "DCF no aplicable o RONIC no disponible.",
        ))

    st.markdown(
        '<div style="display:grid;grid-template-columns:repeat(3,1fr);'
        'gap:12px;margin-top:6px;">'
        + "".join(cards) + '</div>',
        unsafe_allow_html=True,
    )

    if flags:
        st.markdown(
            '<div style="margin-top:10px;padding:10px 14px;'
            'background:#1c1306;border-left:3px solid #F59E0B;'
            'border-radius:0 6px 6px 0;font-size:12px;color:#E8EAED;'
            'line-height:1.6;">'
            '<b>Cross-checks del DCF:</b><ul style="margin:6px 0 0 18px;">'
            + "".join(f"<li>{f}</li>" for f in flags)
            + '</ul></div>',
            unsafe_allow_html=True,
        )


# ============================================================
# Sensitivity matrix WACC × g_terminal
# ============================================================
def _heat_color(pct: float) -> str:
    """Same gradient palette used in the financial-table heatmap."""
    p = max(-50.0, min(50.0, pct))
    if p >= 0:
        t = p / 50.0
        r = int(0xC9 + (0x10 - 0xC9) * t)
        g = int(0xA9 + (0xB9 - 0xA9) * t)
        b = int(0x61 + (0x81 - 0x61) * t)
    else:
        t = (p + 50.0) / 50.0
        r = int(0xEF + (0xC9 - 0xEF) * t)
        g = int(0x44 + (0xA9 - 0x44) * t)
        b = int(0x44 + (0x61 - 0x44) * t)
    return f"rgb({r},{g},{b})"


@st.cache_data(ttl=900, show_spinner=False)
def _compute_sensitivity_matrix(
    ticker: str, base_wacc: float, base_g: float,
    *, n_steps: int = 5, step: float = 0.005,
) -> Optional[dict]:
    """Run a 5×5 DCF sweep around (base_wacc, base_g).

    Cached per (ticker, base assumptions) for 15 min. Returns
    ``None`` when the DCF can't run for this ticker."""
    try:
        from analysis.parallel_loader import load_bundle
        from analysis.koller_reorg import reorganize
        from analysis.lifecycle_classifier import classify_lifecycle
        from valuation.fundamental_growth import estimate_fundamental_growth
        from valuation.dcf_three_stage import run_dcf
    except Exception:
        return None

    bundle = load_bundle(ticker)
    if bundle is None or bundle.income.empty:
        return None

    # Hoist invariants so each cell's DCF skips ~43ms of repeated work.
    try:
        reorg = reorganize(bundle.income, bundle.balance, bundle.cash,
                           wacc=base_wacc)
        lifecycle = classify_lifecycle(
            bundle.income, bundle.cash, ticker=ticker,
            sector=(bundle.info or {}).get("sector"),
        )
        growth = estimate_fundamental_growth(
            reorg, bundle.income, bundle.balance,
            stage=lifecycle["stage"],
            cash=bundle.cash,
        )
    except Exception:
        return None

    offsets = [(-2) * step, (-1) * step, 0.0, step, 2 * step]
    waccs = [round(base_wacc + d, 4) for d in offsets]
    gs    = [round(base_g + d,    4) for d in offsets]

    grid = np.full((len(waccs), len(gs)), np.nan, dtype=float)
    for i, w in enumerate(waccs):
        for j, g in enumerate(gs):
            if w <= g:                                  # discount must exceed growth
                continue
            try:
                r = run_dcf(
                    bundle.income, bundle.balance, bundle.cash,
                    wacc=w,
                    terminal_growth=g,
                    ticker=ticker,
                    sector=(bundle.info or {}).get("sector"),
                    reorg=reorg, lifecycle=lifecycle, growth=growth,
                )
                v = float(r.intrinsic_value_per_share)
                if math.isfinite(v) and v > 0:
                    grid[i, j] = v
            except Exception:
                continue
    return {
        "waccs": waccs, "gs": gs, "grid": grid.tolist(),
        "base_wacc": base_wacc, "base_g": base_g,
    }


def render_sensitivity_matrix(
    *, ticker: str, results: Any, current_price: Optional[float],
) -> None:
    """Render the WACC × g_terminal heatmap.

    Skips entirely when DCF was not applicable (bank/insurer/REIT) or
    when the underlying compute returns nothing."""
    dcf = getattr(results, "dcf", None)
    if dcf is None or getattr(dcf, "skipped_reason", None):
        return
    base_wacc = float(getattr(getattr(results, "wacc", None), "wacc", float("nan")))
    base_g    = float(getattr(dcf, "terminal_growth", float("nan")))
    if not (math.isfinite(base_wacc) and math.isfinite(base_g)):
        return

    sens = _compute_sensitivity_matrix(ticker, base_wacc, base_g)
    if not sens:
        return

    st.markdown(
        '<div class="eq-section-label" style="margin-top:18px;">'
        'SENSITIVITY · DCF (WACC × G_TERMINAL)</div>',
        unsafe_allow_html=True,
    )

    waccs = sens["waccs"]
    gs    = sens["gs"]
    grid  = sens["grid"]

    # Header
    th = '<th style="padding:8px 12px;font-size:10px;color:#9CA3AF;' \
         'letter-spacing:0.06em;text-transform:uppercase;text-align:right;">' \
         'WACC \\ g_T</th>'
    for g in gs:
        th += (
            f'<th style="padding:8px 12px;font-size:11px;color:#C9A961;'
            f'text-align:right;font-variant-numeric:tabular-nums;">'
            f'{g*100:+.2f}%</th>'
        )

    rows = ""
    for i, w in enumerate(waccs):
        row = (
            f'<td style="padding:8px 12px;font-size:11px;color:#C9A961;'
            f'text-align:right;font-variant-numeric:tabular-nums;'
            f'font-weight:600;">{w*100:.2f}%</td>'
        )
        for j, g in enumerate(gs):
            v = grid[i][j]
            if v is None or (isinstance(v, float) and math.isnan(v)):
                cell = (
                    f'<td style="padding:8px 12px;text-align:right;'
                    f'color:#4B5563;">—</td>'
                )
            else:
                if current_price and current_price > 0:
                    upside = (v - current_price) / current_price * 100.0
                    color = _heat_color(upside)
                    tip = f"Upside {upside:+.1f}%"
                else:
                    color = "#E8EAED"
                    tip = ""
                cell = (
                    f'<td title="{tip}" style="padding:8px 12px;'
                    f'text-align:right;color:{color};font-weight:600;'
                    f'font-variant-numeric:tabular-nums;">${v:.2f}</td>'
                )
            row += cell
        # Highlight the base-case row
        row_style = ("background:rgba(201,169,97,0.06);"
                     if abs(w - sens["base_wacc"]) < 1e-9 else "")
        rows += f'<tr style="{row_style}">{row}</tr>'

    st.markdown(
        '<div style="background:#131826;border:1px solid #1F2937;'
        'border-radius:8px;overflow:auto;">'
        '<table style="width:100%;border-collapse:collapse;">'
        f'<thead><tr style="background:#1A2033;">{th}</tr></thead>'
        f'<tbody>{rows}</tbody>'
        '</table></div>',
        unsafe_allow_html=True,
    )
    st.caption(
        f"Base case: WACC = {sens['base_wacc']*100:.2f}%, "
        f"g_terminal = {sens['base_g']*100:.2f}%. Cada celda es "
        f"intrinsic value/acción del DCF re-corrido con esa "
        f"combinación. Color = upside vs precio actual."
    )

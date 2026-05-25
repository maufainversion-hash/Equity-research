"""
Compare-page summary: verdict cards, heatmap side-by-side, key differences.

Three pieces, all rule-based on the data already in the bundles
(no extra API calls):

- :func:`render_verdict_cards` — one card per ticker with name,
  lifecycle profile (chip), market cap and four headline metrics
  (ROIC, operating margin, revenue 5y CAGR, market-implied growth).
- :func:`render_heatmap_table` — replaces the prior st.dataframe
  side-by-side. Best value per row is highlighted in green, worst
  in red, middle in gold. Core lines (margins, ROIC, growth) are
  rendered bolder than secondary lines.
- :func:`render_key_differences` — short bullet list calling out
  the largest gaps between the tickers (margin spread, growth
  spread, valuation spread). Output is rule-based, never invented.

Lifecycle is read via :func:`analysis.lifecycle_classifier.classify_lifecycle`
which is fast (no I/O — runs on the already-loaded income/cash).
Everything else comes straight out of ``calculate_ratios`` and the
already-extracted metric rows.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

import math
import pandas as pd
import streamlit as st


# ============================================================
# Lifecycle profile chip — color per Damodaran stage
# ============================================================
_STAGE_COLORS: dict[str, tuple[str, str]] = {
    # (bg, fg)
    "young_growth":   ("#7C3AED22", "#A78BFA"),     # purple
    "high_growth":    ("#10B98122", "#10B981"),     # green
    "mature_growth":  ("#3B82F622", "#60A5FA"),     # blue
    "mature_stable":  ("#C9A96122", "#C9A961"),     # gold
    "cyclical":       ("#F59E0B22", "#FBBF24"),     # amber
    "declining":      ("#EF444422", "#F87171"),     # red
}
_STAGE_LABELS: dict[str, str] = {
    "young_growth":   "Young growth",
    "high_growth":    "High growth",
    "mature_growth":  "Mature growth",
    "mature_stable":  "Mature stable",
    "cyclical":       "Cyclical",
    "declining":      "Declining",
}


def _profile_chip(stage: Optional[str]) -> str:
    if not stage:
        return ""
    bg, fg = _STAGE_COLORS.get(stage, ("#33415522", "#94A3B8"))
    label = _STAGE_LABELS.get(stage, stage.replace("_", " ").title())
    return (
        f'<span style="display:inline-block;padding:2px 8px;'
        f'border-radius:4px;background:{bg};color:{fg};'
        f'font-size:10px;font-weight:600;letter-spacing:0.05em;'
        f'text-transform:uppercase;">{label}</span>'
    )


# ============================================================
# Headline-metric extractor
# ============================================================
@dataclass
class _Headline:
    ticker: str
    name: str
    market_cap: Optional[float]
    profile: Optional[str]
    roic: Optional[float]
    op_margin: Optional[float]
    revenue_cagr_5y: Optional[float]
    implied_growth: Optional[float]
    # full metric dict — used by heatmap table + key differences
    metrics: dict[str, Optional[float]]


def _safe_num(v) -> Optional[float]:
    if v is None:
        return None
    try:
        f = float(v)
        return f if math.isfinite(f) else None
    except (TypeError, ValueError):
        return None


def _revenue_cagr(income: pd.DataFrame, years: int = 5) -> Optional[float]:
    if "revenue" not in income.columns:
        return None
    s = income["revenue"].dropna()
    if len(s) < years + 1 or float(s.iloc[-years - 1]) <= 0:
        return None
    return float(s.iloc[-1] / s.iloc[-years - 1]) ** (1.0 / years) - 1.0


def _last_ratio(ratios: pd.DataFrame, col: str) -> Optional[float]:
    if col not in ratios.columns:
        return None
    s = ratios[col].dropna()
    return _safe_num(s.iloc[-1]) if not s.empty else None


def build_headlines(
    bundles: dict, implied_growth: dict[str, Optional[float]],
) -> list[_Headline]:
    """Compact, render-ready snapshot for each ticker.

    Inputs:
      bundles:         {ticker: TickerBundle} — already hydrated.
      implied_growth:  {ticker: implied stage-1 growth} or {ticker: None}.
                       The Compare page already computes this for the
                       reverse-DCF spread section; we reuse it.
    """
    from analysis.ratios import calculate_ratios
    from analysis.lifecycle_classifier import classify_lifecycle

    out: list[_Headline] = []
    for t, b in bundles.items():
        info = b.info or {}
        name = (info.get("longName") or info.get("shortName")
                or info.get("name") or t)
        mc = _safe_num(info.get("marketCap") or info.get("market_cap"))

        # Lifecycle — cheap, runs over income + cash.
        try:
            stage = classify_lifecycle(
                b.income, b.cash, ticker=t,
                sector=info.get("sector"),
            ).get("stage")
        except Exception:
            stage = None

        # Ratios — cached upstream, cheap.
        try:
            ratios = calculate_ratios(b.income, b.balance, b.cash)
        except Exception:
            ratios = pd.DataFrame()

        roic       = _last_ratio(ratios, "ROIC %")
        op_margin  = _last_ratio(ratios, "Operating Margin %")
        gross      = _last_ratio(ratios, "Gross Margin %")
        net_margin = _last_ratio(ratios, "Net Margin %")
        fcf_margin = _last_ratio(ratios, "FCF Margin %")
        roe        = _last_ratio(ratios, "ROE %")
        de         = _last_ratio(ratios, "Debt/Equity")
        rev_cagr   = _revenue_cagr(b.income, 5)
        ig         = implied_growth.get(t)

        metrics = {
            "Gross margin %":  gross,
            "Op margin %":     op_margin,
            "Net margin %":    net_margin,
            "FCF margin %":    fcf_margin,
            "ROIC %":          roic,
            "ROE %":           roe,
            "Revenue CAGR 5y %": (rev_cagr * 100.0) if rev_cagr is not None else None,
            "Implied growth %": (ig * 100.0) if ig is not None else None,
            "Debt/Equity":     de,
        }

        out.append(_Headline(
            ticker=t, name=str(name)[:32], market_cap=mc, profile=stage,
            roic=roic, op_margin=op_margin,
            revenue_cagr_5y=rev_cagr, implied_growth=ig,
            metrics=metrics,
        ))
    return out


# ============================================================
# Verdict cards — one per ticker, side by side
# ============================================================
def _format_pct(v: Optional[float], sign: bool = False) -> str:
    if v is None:
        return "—"
    return (f"{v:+.1f}%" if sign else f"{v:.1f}%")


def _format_growth_pct(v: Optional[float]) -> str:
    """Decimal growth (0.14) → '+14.0%'."""
    if v is None:
        return "—"
    return f"{v * 100:+.1f}%"


def _money_compact(v: Optional[float]) -> str:
    if v is None:
        return "—"
    a = abs(v)
    if a >= 1e12: return f"${a / 1e12:.2f}T"
    if a >= 1e9:  return f"${a / 1e9:.2f}B"
    if a >= 1e6:  return f"${a / 1e6:.2f}M"
    return f"${a:,.0f}"


def render_verdict_cards(headlines: list[_Headline]) -> None:
    """One card per ticker with profile + 4 headline metrics."""
    if not headlines:
        return
    st.markdown(
        '<div class="eq-section-label">SNAPSHOT</div>',
        unsafe_allow_html=True,
    )
    cols = st.columns(len(headlines), gap="small")
    for col, h in zip(cols, headlines):
        with col:
            st.markdown(
                f"""
<div style="background:#0f172a;border:1px solid #334155;
border-radius:8px;padding:14px 16px;">
  <div style="display:flex;justify-content:space-between;
align-items:baseline;margin-bottom:6px;">
    <div style="font-size:18px;font-weight:700;color:#F3F4F6;
letter-spacing:0.03em;">{h.ticker}</div>
    <div style="font-size:11px;color:#94A3B8;">{_money_compact(h.market_cap)}</div>
  </div>
  <div style="font-size:12px;color:#94A3B8;margin-bottom:8px;
white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{h.name}</div>
  <div style="margin-bottom:12px;">{_profile_chip(h.profile)}</div>
  <div style="display:grid;grid-template-columns:1fr 1fr;
gap:8px 12px;font-size:12px;">
    <div>
      <div style="color:#94A3B8;font-size:10px;letter-spacing:0.05em;
text-transform:uppercase;">ROIC</div>
      <div style="color:#E8EAED;font-weight:600;
font-variant-numeric:tabular-nums;">{_format_pct(h.roic)}</div>
    </div>
    <div>
      <div style="color:#94A3B8;font-size:10px;letter-spacing:0.05em;
text-transform:uppercase;">Op margin</div>
      <div style="color:#E8EAED;font-weight:600;
font-variant-numeric:tabular-nums;">{_format_pct(h.op_margin)}</div>
    </div>
    <div>
      <div style="color:#94A3B8;font-size:10px;letter-spacing:0.05em;
text-transform:uppercase;">Revenue 5y</div>
      <div style="color:#E8EAED;font-weight:600;
font-variant-numeric:tabular-nums;">{_format_growth_pct(h.revenue_cagr_5y)}</div>
    </div>
    <div>
      <div style="color:#94A3B8;font-size:10px;letter-spacing:0.05em;
text-transform:uppercase;">Implied growth</div>
      <div style="color:#E8EAED;font-weight:600;
font-variant-numeric:tabular-nums;">{_format_growth_pct(h.implied_growth)}</div>
    </div>
  </div>
</div>
""",
                unsafe_allow_html=True,
            )


# ============================================================
# Heatmap side-by-side table
# ============================================================
# Whether higher is better. Used to flip the heatmap colour direction.
_HIGHER_IS_BETTER: dict[str, bool] = {
    "Gross margin %":     True,
    "Op margin %":        True,
    "Net margin %":       True,
    "FCF margin %":       True,
    "ROIC %":             True,
    "ROE %":              True,
    "Revenue CAGR 5y %":  True,
    "Implied growth %":   False,        # lower implied growth = cheaper, that's better
    "Debt/Equity":        False,        # lower leverage = safer
}

_CORE_METRICS: frozenset[str] = frozenset({
    "Gross margin %", "Op margin %", "Net margin %", "FCF margin %",
    "ROIC %", "Revenue CAGR 5y %", "Implied growth %",
})


def _rank_color(value: Optional[float], all_values: list[Optional[float]],
                higher_better: bool) -> str:
    """Green for best, red for worst, gold for mid (or single)."""
    clean = [v for v in all_values if v is not None]
    if value is None or not clean:
        return "#6B7280"
    if len(clean) == 1:
        return "#C9A961"
    best = max(clean) if higher_better else min(clean)
    worst = min(clean) if higher_better else max(clean)
    if value == best and value != worst:
        return "#10B981"                                # green
    if value == worst and value != best:
        return "#EF4444"                                # red
    return "#C9A961"                                    # gold (middle)


def _fmt_metric_cell(label: str, value: Optional[float]) -> str:
    if value is None:
        return "—"
    if "Debt/Equity" in label:
        return f"{value:.2f}"
    return f"{value:.1f}%"


def render_heatmap_table(headlines: list[_Headline]) -> None:
    if not headlines:
        return
    st.markdown(
        '<div class="eq-section-label" style="margin-top:14px;">'
        'SIDE-BY-SIDE · HEATMAP</div>',
        unsafe_allow_html=True,
    )

    # Compose: rows = metrics, cols = tickers
    metric_keys = list(headlines[0].metrics.keys())

    header_cells = (
        '<th style="padding:10px 14px;font-size:11px;letter-spacing:0.06em;'
        'text-transform:uppercase;color:#9CA3AF;font-weight:500;'
        'text-align:left;">METRIC</th>'
    )
    for h in headlines:
        header_cells += (
            f'<th style="padding:10px 14px;font-size:11px;letter-spacing:0.06em;'
            f'text-transform:uppercase;color:#F3F4F6;font-weight:600;'
            f'text-align:right;">{h.ticker}</th>'
        )

    body_rows = ""
    for i, metric in enumerate(metric_keys):
        is_core = metric in _CORE_METRICS
        font_size = "13px" if is_core else "12px"
        font_weight = "600" if is_core else "400"
        label_color = "#F3F4F6" if is_core else "#9CA3AF"
        zebra = ("background:rgba(255,255,255,0.02);"
                 if i % 2 == 1 else "")

        cells = (
            f'<td style="padding:9px 14px;color:{label_color};'
            f'font-weight:{font_weight};font-size:{font_size};'
            f'text-align:left;">{metric}</td>'
        )
        values = [h.metrics.get(metric) for h in headlines]
        higher_better = _HIGHER_IS_BETTER.get(metric, True)
        for v in values:
            color = _rank_color(v, values, higher_better)
            cells += (
                f'<td style="padding:9px 14px;color:{color};'
                f'font-weight:{font_weight};font-size:{font_size};'
                f'text-align:right;font-variant-numeric:tabular-nums;">'
                f'{_fmt_metric_cell(metric, v)}</td>'
            )

        body_rows += f'<tr style="{zebra}">{cells}</tr>'

    st.markdown(
        '<div style="background:#131826;border:1px solid #1F2937;'
        'border-radius:8px;overflow:hidden;">'
        '<table style="width:100%;border-collapse:collapse;'
        'font-family:Inter,-apple-system,sans-serif;">'
        f'<thead><tr style="background:#1A2033;">{header_cells}</tr></thead>'
        f'<tbody>{body_rows}</tbody>'
        '</table></div>',
        unsafe_allow_html=True,
    )


# ============================================================
# Key differences — rule-based bullets
# ============================================================
def _gap(values: list[tuple[str, Optional[float]]]) -> Optional[tuple[str, str, float]]:
    """Return (winner_ticker, loser_ticker, abs_gap) over a list of
    (ticker, value) tuples. None when fewer than 2 finite values."""
    clean = [(t, v) for t, v in values if v is not None]
    if len(clean) < 2:
        return None
    clean.sort(key=lambda kv: kv[1], reverse=True)
    top, bottom = clean[0], clean[-1]
    if top[1] == bottom[1]:
        return None
    return (top[0], bottom[0], top[1] - bottom[1])


def render_key_differences(headlines: list[_Headline]) -> None:
    if len(headlines) < 2:
        return

    bullets: list[str] = []

    def _push(metric_label: str, gap_obj, unit_suffix: str = "pp",
              higher_better: bool = True):
        if gap_obj is None:
            return
        winner, loser, gap = gap_obj
        # When lower is better (Debt/Equity, Implied growth), flip the
        # narrative: the "loser" in raw ranking is actually the winner.
        if not higher_better:
            winner, loser = loser, winner
        if abs(gap) < 0.5 and unit_suffix == "pp":
            return                                       # not material
        bullets.append(
            f'<li><b>{metric_label}:</b> {winner} '
            f'<span style="color:#10B981;">supera</span> a {loser} '
            f'por <b>{abs(gap):.1f}{unit_suffix}</b>.</li>'
        )

    pairs = [(h.ticker, h.metrics) for h in headlines]

    _push("Gross margin",
          _gap([(t, m.get("Gross margin %")) for t, m in pairs]))
    _push("Operating margin",
          _gap([(t, m.get("Op margin %")) for t, m in pairs]))
    _push("FCF margin",
          _gap([(t, m.get("FCF margin %")) for t, m in pairs]))
    _push("ROIC",
          _gap([(t, m.get("ROIC %")) for t, m in pairs]))
    _push("Revenue growth 5y",
          _gap([(t, m.get("Revenue CAGR 5y %")) for t, m in pairs]))
    _push("Apalancamiento (D/E)",
          _gap([(t, m.get("Debt/Equity")) for t, m in pairs]),
          unit_suffix="x", higher_better=False)
    _push("Premium implícito (lower=cheaper)",
          _gap([(t, m.get("Implied growth %")) for t, m in pairs]),
          higher_better=False)

    if not bullets:
        return

    st.markdown(
        '<div class="eq-section-label" style="margin-top:14px;">'
        'KEY DIFFERENCES</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="background:#0b1220;border-left:3px solid #C9A961;'
        'border-radius:0 6px 6px 0;padding:12px 16px;'
        'font-size:13px;color:#cbd5e1;line-height:1.7;">'
        '<ul style="margin:0;padding-left:18px;">'
        + "".join(bullets[:7])
        + '</ul></div>',
        unsafe_allow_html=True,
    )

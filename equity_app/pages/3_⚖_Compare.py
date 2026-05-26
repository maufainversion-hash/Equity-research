"""
Compare — side-by-side analysis of 2-3 tickers (P11.B1).

One page, dense table, projected FCF chart. Every ticker reuses the
cached :func:`load_bundle` so subsequent visits hit the cache instead
of refetching.
"""
from __future__ import annotations
import logging
import sys
from pathlib import Path

log = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from typing import Optional

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from analysis.parallel_loader import load_bundle
from analysis.ratios import calculate_ratios


# ============================================================
# Direct yfinance fallback — used when the cached bundle is partial
# (FMP rate-limited / Finnhub down / yfinance scrape-blocked at the
# time the bundle was hydrated). Bypasses the bundle cache so we
# get fresh metadata without burning an FMP call.
#
# Returns a dict so the caller can pull `price`, `market_cap`,
# `sector`, `name` independently — each field falls back to None
# if yfinance doesn't have it (rare for major US tickers).
# ============================================================
@st.cache_data(ttl=300, show_spinner=False)
def _yf_meta(ticker: str) -> dict:
    out: dict = {"price": None, "market_cap": None,
                  "sector": None, "name": None}
    try:
        import yfinance as yf
    except Exception:
        return out

    try:
        t = yf.Ticker(ticker)
    except Exception:
        return out

    # ---- fast_info (cheap, no scrape) — price + market_cap ----
    try:
        fi = t.fast_info
        # price
        for key in ("last_price", "lastPrice",
                    "regular_market_price", "regularMarketPrice"):
            try:
                v = fi[key] if key in fi else getattr(fi, key, None)
            except (KeyError, TypeError):
                v = getattr(fi, key, None)
            if v is not None:
                try:
                    p = float(v)
                    if p > 0:
                        out["price"] = p
                        break
                except (TypeError, ValueError):
                    continue
        # market_cap
        for key in ("market_cap", "marketCap"):
            try:
                v = fi[key] if key in fi else getattr(fi, key, None)
            except (KeyError, TypeError):
                v = getattr(fi, key, None)
            if v is not None:
                try:
                    mc = float(v)
                    if mc > 0:
                        out["market_cap"] = mc
                        break
                except (TypeError, ValueError):
                    continue
    except Exception as e:
        log.debug("compare metric extraction failed: %s", e)

    # ---- .info (slower, scrape — only call if we need sector/name) ----
    if out["sector"] is None or out["name"] is None:
        try:
            full = t.info or {}
            out["sector"] = (out["sector"] or full.get("sector")
                              or full.get("sectorDisp"))
            out["name"] = (out["name"]
                            or full.get("longName")
                            or full.get("shortName"))
            # market_cap fallback from .info if fast_info didn't have it
            if out["market_cap"] is None and full.get("marketCap"):
                try:
                    out["market_cap"] = float(full["marketCap"])
                except (TypeError, ValueError):
                    pass
        except Exception as e:
            log.debug("compare profile fetch failed: %s", e)
    return out


# ============================================================
# Header
# ============================================================
st.markdown(
    '<div class="eq-section-label">⚖ COMPARE</div>',
    unsafe_allow_html=True,
)
st.caption("Side-by-side analysis of 2-3 tickers. Reuses the cached bundle.")


# ============================================================
# Ticker inputs — País / Industria filters + 3 ticker dropdowns
# ============================================================
# Reuses the curated company_catalog so the user picks from a list
# instead of typing. Country and Industry are cascading filters that
# narrow the ticker dropdowns below.
from data.company_catalog import (
    countries as _catalog_countries,
    sectors   as _catalog_sectors,
    companies as _catalog_companies,
    all_companies as _catalog_all,
    company_for as _catalog_company_for,
)

_ALL = "— Todos —"
_NONE = "— Ninguno —"

# ---- Country + Industry filters ----
filt_c, filt_s = st.columns([1, 1])
with filt_c:
    country_options = [_ALL] + _catalog_countries()
    country_sel = st.selectbox("Country", country_options, index=0,
                                key="compare_country")
with filt_s:
    if country_sel == _ALL:
        # Union of sectors across all countries, keeping taxonomy order.
        from data.company_catalog import _SECTOR_ORDER as _SO
        present = sorted({c.sector for c in _catalog_all()},
                         key=lambda s: _SO.index(s) if s in _SO else 999)
        sector_options = [_ALL] + present
    else:
        sector_options = [_ALL] + _catalog_sectors(country_sel)
    sector_sel = st.selectbox("Industry", sector_options, index=0,
                               key="compare_sector")

# ---- Resolve the filtered company list ----
def _filtered() -> list:
    pool = list(_catalog_all())
    if country_sel != _ALL:
        pool = [c for c in pool if c.country == country_sel]
    if sector_sel != _ALL:
        pool = [c for c in pool if c.sector == sector_sel]
    return sorted(pool, key=lambda c: c.name.lower())

_pool = _filtered()
if not _pool:
    st.warning("No companies match this country / industry filter.")
    st.stop()


def _label(c) -> str:
    return f"{c.ticker} — {c.name}"


_labels = [_label(c) for c in _pool]
_by_label: dict[str, str] = {_label(c): c.ticker for c in _pool}

# ---- Pick safe defaults that exist in the current pool ----
# Backwards-compat with the prior AAPL / MSFT / "" pre-fills: only
# use them when they survive the filter.
def _idx_or_zero(preferred: str) -> int:
    for i, c in enumerate(_pool):
        if c.ticker.upper() == preferred.upper():
            return i
    return 0


def _idx_or_first_other(preferred: str, avoid: str) -> int:
    for i, c in enumerate(_pool):
        if c.ticker.upper() == preferred.upper() and c.ticker != avoid:
            return i
    for i, c in enumerate(_pool):
        if c.ticker != avoid:
            return i
    return 0


_default1 = _idx_or_zero("AAPL")
_default2 = _idx_or_first_other("MSFT", _pool[_default1].ticker)

c1, c2, c3 = st.columns(3)
with c1:
    sel1 = st.selectbox("Ticker 1", _labels, index=_default1,
                         key=f"compare_t1_{country_sel}_{sector_sel}")
with c2:
    sel2 = st.selectbox("Ticker 2", _labels, index=_default2,
                         key=f"compare_t2_{country_sel}_{sector_sel}")
with c3:
    sel3 = st.selectbox("Ticker 3 (optional)", [_NONE] + _labels, index=0,
                         key=f"compare_t3_{country_sel}_{sector_sel}")

t1 = _by_label.get(sel1, "")
t2 = _by_label.get(sel2, "")
t3 = "" if sel3 == _NONE else _by_label.get(sel3, "")

tickers = [t for t in (t1, t2, t3) if t]
# De-dupe while preserving order — selecting the same name twice
# would otherwise load the bundle twice for the same ticker.
tickers = list(dict.fromkeys(tickers))
if len(tickers) < 2:
    st.info("Pick at least 2 distinct tickers to compare.")
    st.stop()


# ============================================================
# Bundle hydration (cached, parallel)
# ============================================================
with st.spinner(f"Loading {len(tickers)} tickers…"):
    bundles = {t: load_bundle(t) for t in tickers}


# ============================================================
# Metric extraction per ticker
# ============================================================
def _money_compact(v: Optional[float]) -> str:
    if v is None or not isinstance(v, (int, float)):
        return "—"
    av = abs(v)
    if av >= 1e12:
        return f"${av/1e12:.2f}T"
    if av >= 1e9:
        return f"${av/1e9:.1f}B"
    if av >= 1e6:
        return f"${av/1e6:.1f}M"
    return f"${av:,.0f}"


def _pct(v) -> str:
    if v is None or not isinstance(v, (int, float)) or pd.isna(v):
        return "—"
    return f"{v:.1f}%"


def _ratio(v) -> str:
    if v is None or not isinstance(v, (int, float)) or pd.isna(v):
        return "—"
    return f"{v:.2f}"


def _last(ratios: pd.DataFrame, col: str):
    if ratios is None or ratios.empty or col not in ratios.columns:
        return None
    s = ratios[col].dropna()
    return float(s.iloc[-1]) if not s.empty else None


def _try_implied_growth(bundle, current_price, shares) -> Optional[float]:
    """Best-effort reverse DCF — fails silently for banks/REITs."""
    if not (current_price and shares and shares > 0):
        return None
    try:
        from valuation.reverse_dcf import run_reverse_dcf
        # Implied per-share growth = run_reverse_dcf with target = current price
        # The function expects target_price as TOTAL equity / share;
        # since shares × per-share = mcap, target_price as a per-share works.
        res = run_reverse_dcf(
            income=bundle.income, balance=bundle.balance, cash=bundle.cash,
            target_price=float(current_price),
            wacc=0.10,            # rough default for cross-ticker comparison
        )
        return res.implied_growth if res and res.implied_growth is not None else None
    except Exception:
        return None


def _extract_metrics(ticker: str, bundle) -> dict:
    if bundle.income.empty:
        return {"Ticker": ticker, "Status": "no_data"}
    info = bundle.info or {}
    ratios = calculate_ratios(bundle.income, bundle.balance, bundle.cash)
    price = bundle.quote.get("price") if bundle.quote else None
    market_cap = info.get("marketCap") or info.get("market_cap")
    sector = info.get("sector")
    name = info.get("name") or info.get("longName") or info.get("shortName")

    # If the cached bundle is thin (FMP rate-limited / yfinance scrape
    # blocked at the time), fall back to a direct yfinance fast_info
    # lookup. This is cheap, cached 5min, and doesn't burn an FMP call.
    if (price is None or price <= 0) or not market_cap or not sector or not name:
        yf_meta = _yf_meta(ticker)
        if price is None or price <= 0:
            price = yf_meta.get("price")
        if not market_cap:
            market_cap = yf_meta.get("market_cap")
        if not sector:
            sector = yf_meta.get("sector")
        if not name:
            name = yf_meta.get("name")
    if not name:
        name = ticker

    shares = (info.get("sharesOutstanding")
              or info.get("shares_outstanding"))
    implied = _try_implied_growth(bundle, price, shares)

    return {
        "Ticker":      ticker,
        "Name":        str(name)[:30],
        "Sector":      sector or "—",
        "Price":       f"${price:.2f}" if price else "—",
        "Mkt Cap":     _money_compact(market_cap),
        "Gross Margin %":     _pct(_last(ratios, "Gross Margin %")),
        "Op Margin %":        _pct(_last(ratios, "Operating Margin %")),
        "Net Margin %":       _pct(_last(ratios, "Net Margin %")),
        "FCF Margin %":       _pct(_last(ratios, "FCF Margin %")),
        "ROIC %":      _pct(_last(ratios, "ROIC %")),
        "ROE %":       _pct(_last(ratios, "ROE %")),
        "Debt/Equity": _ratio(_last(ratios, "Debt/Equity")),
        "Implied growth": _pct(implied * 100.0 if implied is not None else None),
    }


rows = [_extract_metrics(t, b) for t, b in bundles.items()]
df = pd.DataFrame(rows)

# ============================================================
# Verdict cards + heatmap side-by-side + key differences
# ============================================================
# Replaces the old st.dataframe with three richer pieces:
#   1. one snapshot card per ticker (profile chip + headline metrics)
#   2. heatmap side-by-side table (best in green, worst in red)
#   3. key differences bullet list (rule-based, material gaps only)
from ui.components.compare_summary import (
    build_headlines, render_verdict_cards, render_heatmap_table,
    render_key_differences,
)

# Reuse the implied_growth values that _extract_metrics already
# computed via _try_implied_growth — avoid a second reverse-DCF pass.
_implied_for_summary: dict[str, Optional[float]] = {
    t: _try_implied_growth(
        b,
        (b.quote.get("price") if b.quote else None),
        ((b.info or {}).get("sharesOutstanding")
         or (b.info or {}).get("shares_outstanding")),
    )
    for t, b in bundles.items()
}
_headlines = build_headlines(bundles, _implied_for_summary)
render_verdict_cards(_headlines)
render_heatmap_table(_headlines)
render_key_differences(_headlines)

# 6-axis radar — visual fingerprint comparing margins, returns,
# growth and balance-sheet strength.
from ui.components.compare_radar import render_compare_radar
render_compare_radar(_headlines)


# ============================================================
# Historical price loader for multiples spread (cached 6h)
# ============================================================
@st.cache_data(ttl=21_600, show_spinner=False)
def _hist_prices(_tickers: tuple[str, ...]) -> dict:
    from data.market_data import _yfinance
    yf = _yfinance()
    if yf is None:
        return {}
    out: dict[str, pd.DataFrame] = {}
    for t in _tickers:
        try:
            hist = yf.Ticker(t).history(period="5y")[["Close"]]
            if not hist.empty:
                out[t] = hist
        except Exception:
            continue
    return out


prices_hist = _hist_prices(tuple(tickers))
prices_now = {t: bundles[t].quote.get("price") for t in tickers}

# Per-ticker WACC: default 10% across the board for cross-ticker
# comparability. Computing a real WACC per ticker would need a beta
# regression + cost-of-debt resolution and the extra precision rarely
# changes the reverse-DCF conclusion at this resolution.
waccs = {t: 0.10 for t in tickers}


# ============================================================
# Trajectory overlays
# ============================================================
st.markdown(
    '<div class="eq-section-label" style="margin-top:18px;">'
    'TRAJECTORY</div>',
    unsafe_allow_html=True,
)
from ui.components.compare_trajectories import render_compare_trajectories
render_compare_trajectories(bundles)


# ============================================================
# Quality scorecard
# ============================================================
st.markdown(
    '<div class="eq-section-label" style="margin-top:18px;">'
    'QUALITY SCORECARD</div>',
    unsafe_allow_html=True,
)
from ui.components.compare_quality_scorecard import render_quality_scorecard
market_caps = {t: bundles[t].market_cap for t in tickers}
render_quality_scorecard(bundles, market_caps)


# ============================================================
# Capital allocation (cumulative 5y)
# ============================================================
st.markdown(
    '<div class="eq-section-label" style="margin-top:18px;">'
    'CAPITAL ALLOCATION · CUMULATIVE 5Y</div>',
    unsafe_allow_html=True,
)
from ui.components.compare_capital_allocation import render_compare_capital_allocation
render_compare_capital_allocation(bundles)


# ============================================================
# Reverse DCF spread cards
# ============================================================
st.markdown(
    '<div class="eq-section-label" style="margin-top:18px;">'
    'REVERSE DCF · IMPLIED GROWTH</div>',
    unsafe_allow_html=True,
)
from ui.components.compare_reverse_dcf_spread import render_reverse_dcf_spread
render_reverse_dcf_spread(bundles, prices_now, waccs)


# ============================================================
# Forecasted FCF chart
# ============================================================
st.markdown(
    '<div class="eq-section-label" style="margin-top:18px;">'
    'PROJECTED FREE CASH FLOW · 5-YEAR</div>',
    unsafe_allow_html=True,
)

_LINE_COLORS = ["#3B82F6", "#C9A961", "#10B981"]

# Rebased index — base year = 100 so 3 tickers with very different
# magnitudes (e.g. GOOGL ~$100B FCF vs DIS ~$5B) become visually
# comparable. The chart answers "who's growing faster", not "who
# generates more cash" — the latter is already covered by Capital
# Allocation Cumulative 5Y above.
fig = go.Figure()
all_years: set[int] = set()
skipped_fcf: list[str] = []
for i, (ticker, bundle) in enumerate(bundles.items()):
    if bundle.income.empty:
        skipped_fcf.append(ticker)
        continue
    try:
        from analysis.financial_forecast import (
            _default_inputs_from_history, project_financials,
        )
        info = bundle.info or {}
        shares = (info.get("sharesOutstanding")
                  or info.get("shares_outstanding"))
        inp = _default_inputs_from_history(bundle.income, bundle.balance,
                                            bundle.cash, years=5)
        result = project_financials(
            bundle.income, bundle.balance, bundle.cash,
            inputs=inp, years=5, shares_outstanding=shares,
        )
        if result.fcff_per_year is None or result.fcff_per_year.empty:
            skipped_fcf.append(ticker)
            continue
        years_axis = [d.year if isinstance(d, pd.Timestamp) else int(d)
                      for d in result.fcff_per_year.index]
        all_years.update(years_axis)
        raw_vals = result.fcff_per_year.values
        base = float(raw_vals[0]) if len(raw_vals) > 0 else 0.0
        if base <= 0:
            # Negative / zero base year breaks the rebase math — can't
            # plot a meaningful index. Skip with a note.
            skipped_fcf.append(ticker)
            continue
        index_vals = [(float(v) / base) * 100.0 for v in raw_vals]
        absolute_b = [float(v) / 1e9 for v in raw_vals]
        hover_text = [
            f"{ticker} {y}<br>Index: {idx:.0f}<br>FCF: ${ab:.1f}B"
            for y, idx, ab in zip(years_axis, index_vals, absolute_b)
        ]
        fig.add_trace(go.Scatter(
            x=years_axis,
            y=index_vals,
            name=ticker, mode="lines+markers",
            line=dict(color=_LINE_COLORS[i % len(_LINE_COLORS)], width=2.2),
            marker=dict(size=8),
            hovertext=hover_text,
            hoverinfo="text",
        ))
    except Exception:
        skipped_fcf.append(ticker)
        continue

# Horizontal reference line at index 100 (= base year)
if all_years:
    fig.add_hline(y=100, line_dash="dot", line_color="#374151",
                  line_width=1, opacity=0.6)

fig.update_layout(
    plot_bgcolor="#131826", paper_bgcolor="#131826",
    font=dict(color="#9CA3AF", family="Inter, sans-serif", size=11),
    height=380,
    margin=dict(l=0, r=0, t=20, b=0),
    yaxis=dict(title="FCF Index (Año base = 100)",
               gridcolor="#1F2937", color="#6B7280"),
    xaxis=dict(gridcolor="#1F2937", color="#6B7280",
               tickmode="linear", dtick=1,
               tickformat="d"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02,
                xanchor="left", x=0, bgcolor="rgba(0,0,0,0)"),
)
st.plotly_chart(fig, width="stretch",
                config={"displayModeBar": False})

if skipped_fcf:
    st.caption(
        f"⚠️ FCF not projectable for: {', '.join(skipped_fcf)} "
        f"(base-year FCF ≤ 0 or no statements available)."
    )
st.caption(
    "Y-axis = index rebased to the base year (= 100), not $B — lets "
    "growth trajectories be compared across tickers with very "
    "different magnitudes. Hover shows absolute FCF in $B. Forecast "
    "uses each ticker's own historical CAGR + 3y-avg margins."
)


# ============================================================
# Multiples spread (pair-trade z-score) — only when N == 2
# ============================================================
if len(tickers) == 2:
    st.markdown(
        '<div class="eq-section-label" style="margin-top:18px;">'
        'MULTIPLES SPREAD · PAIR-TRADE Z-SCORE</div>',
        unsafe_allow_html=True,
    )
    from ui.components.compare_multiples_spread import render_multiples_spread
    render_multiples_spread(bundles, prices_hist)

"""
Investor Expectations — 4-signal synthesis panel.

Consolidates four already-computed-upstream signals about what the
*market* (and the *players close to the company*) expect, then emits
a synthesis paragraph that flags consonance or dissonance among them.

Signals:

1. **MERCADO** — reverse-DCF stage-1 growth that today's price requires.
2. **ANALISTAS** — Finnhub sell-side price-target consensus + rating
   distribution.
3. **MÚLTIPLOS** — current P/E (LTM and forward) + EV/EBITDA + P/S
   from the provider snapshot. No historical z-score yet: that needs
   price history we don't load here.
4. **INSIDERS** — net 6-month insider buying/selling from the existing
   ``analyze_insider_activity`` output.

The synthesis is rule-based and conservative — it only labels
"dissonance" when at least two signals point in opposite directions
(e.g. market pricing aggressive growth + insiders dumping).

Defensive design: any individual signal that's missing (no API key,
no data) is dropped silently; the panel still renders whatever is
available, and the synthesis takes that into account.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Any

import streamlit as st


# ============================================================
# Per-signal mini-renders
# ============================================================
def _format_pct(x: Optional[float], digits: int = 1, scale: float = 100.0) -> str:
    if x is None:
        return "—"
    try:
        return f"{x * scale:+.{digits}f}%"
    except Exception:
        return "—"


def _format_mult(x: Optional[float], suffix: str = "x") -> str:
    if x is None:
        return "—"
    try:
        v = float(x)
        if v != v or v <= 0:                          # NaN or ≤0
            return "—"
        return f"{v:.1f}{suffix}"
    except Exception:
        return "—"


def _format_usd_short(x: Optional[float]) -> str:
    if x is None:
        return "—"
    try:
        v = float(x)
    except Exception:
        return "—"
    sign = "−" if v < 0 else "+"
    av = abs(v)
    if av >= 1e9:
        return f"{sign}${av / 1e9:.1f}B"
    if av >= 1e6:
        return f"{sign}${av / 1e6:.1f}M"
    if av >= 1e3:
        return f"{sign}${av / 1e3:.1f}K"
    return f"{sign}${av:.0f}"


# ============================================================
# Signal dataclasses — what each card needs to render + synthesise
# ============================================================
@dataclass
class _MarketSignal:
    available: bool
    implied_growth: Optional[float] = None        # decimal
    historical_cagr: Optional[float] = None       # decimal
    gap: Optional[float] = None                   # implied − historical


@dataclass
class _AnalystSignal:
    available: bool
    pt_mean: Optional[float] = None
    pt_upside: Optional[float] = None             # decimal vs current price
    n_analysts: Optional[int] = None
    pct_buy: Optional[float] = None               # 0-1 share of buy/strong_buy
    pct_sell: Optional[float] = None              # 0-1 share of sell/strong_sell


@dataclass
class _MultiplesSignal:
    available: bool
    pe_ttm: Optional[float] = None
    pe_forward: Optional[float] = None
    ev_ebitda: Optional[float] = None
    ps: Optional[float] = None
    # Crude verdict: "stretched" / "elevated" / "normal" / "depressed"
    label: Optional[str] = None


@dataclass
class _InsiderSignal:
    available: bool
    net_6m_usd: Optional[float] = None
    trend: Optional[str] = None                   # "increasing" / "stable" / "decreasing"
    score: Optional[int] = None                   # 0-100 from insider_analysis


# ============================================================
# Signal builders
# ============================================================
def _build_market(implied_growth: Optional[float],
                  historical_cagr: Optional[float]) -> _MarketSignal:
    if implied_growth is None:
        return _MarketSignal(available=False)
    gap = (implied_growth - historical_cagr
           if historical_cagr is not None else None)
    return _MarketSignal(
        available=True,
        implied_growth=implied_growth,
        historical_cagr=historical_cagr,
        gap=gap,
    )


def _build_analysts(ticker: str, current_price: Optional[float]) -> _AnalystSignal:
    """Pulls Finnhub price-target + recommendation distribution.

    Returns ``available=False`` (silent) when no FINNHUB_API_KEY or
    Finnhub returns nothing. Does not raise."""
    try:
        from data.finnhub_provider import (
            is_available, fetch_price_target, fetch_recommendation_trends,
        )
    except Exception:
        return _AnalystSignal(available=False)
    if not is_available():
        return _AnalystSignal(available=False)
    try:
        target = fetch_price_target(ticker) or {}
    except Exception:
        target = {}
    try:
        recs = fetch_recommendation_trends(ticker)
    except Exception:
        recs = None

    pt_mean = target.get("targetMean") if isinstance(target, dict) else None
    n_analysts = target.get("numberOfAnalysts") if isinstance(target, dict) else None

    pct_buy = pct_sell = None
    if recs is not None and not recs.empty:
        latest = recs.iloc[0]
        sb = int(latest.get("strongBuy", 0) or 0)
        b  = int(latest.get("buy", 0) or 0)
        h  = int(latest.get("hold", 0) or 0)
        s  = int(latest.get("sell", 0) or 0)
        ss = int(latest.get("strongSell", 0) or 0)
        total = sb + b + h + s + ss
        if total > 0:
            pct_buy = (sb + b) / total
            pct_sell = (s + ss) / total

    if pt_mean is None and pct_buy is None:
        return _AnalystSignal(available=False)

    pt_upside = None
    if (pt_mean and current_price and current_price > 0
            and float(pt_mean) > 0):
        try:
            pt_upside = float(pt_mean) / float(current_price) - 1.0
        except Exception:
            pt_upside = None

    return _AnalystSignal(
        available=True,
        pt_mean=float(pt_mean) if pt_mean else None,
        pt_upside=pt_upside,
        n_analysts=int(n_analysts) if n_analysts else None,
        pct_buy=pct_buy,
        pct_sell=pct_sell,
    )


def _build_multiples(info: dict) -> _MultiplesSignal:
    """Snapshot multiples from the provider info dict.

    Uses yfinance / Finviz field names: ``trailingPE``, ``forwardPE``,
    ``enterpriseToEbitda``, ``priceToSalesTrailing12Months`` /
    ``priceToSales``. Anything missing stays None."""
    if not isinstance(info, dict):
        return _MultiplesSignal(available=False)

    def _g(*keys: str) -> Optional[float]:
        for k in keys:
            v = info.get(k)
            if v is None:
                continue
            try:
                f = float(v)
                if f > 0 and f == f:                  # not NaN, not zero
                    return f
            except Exception:
                continue
        return None

    pe_ttm     = _g("trailingPE", "trailing_pe", "P/E")
    pe_forward = _g("forwardPE", "forward_pe", "Forward P/E")
    ev_ebitda  = _g("enterpriseToEbitda", "ev_to_ebitda", "EV/EBITDA")
    ps         = _g("priceToSalesTrailing12Months", "priceToSales", "P/S")

    if all(v is None for v in (pe_ttm, pe_forward, ev_ebitda, ps)):
        return _MultiplesSignal(available=False)

    # Crude label off TTM P/E — defensible rules of thumb, not gospel.
    label: Optional[str] = None
    if pe_ttm is not None:
        if pe_ttm >= 50:
            label = "stretched"
        elif pe_ttm >= 30:
            label = "elevated"
        elif pe_ttm >= 12:
            label = "normal"
        elif pe_ttm > 0:
            label = "depressed"

    return _MultiplesSignal(
        available=True,
        pe_ttm=pe_ttm,
        pe_forward=pe_forward,
        ev_ebitda=ev_ebitda,
        ps=ps,
        label=label,
    )


@st.cache_data(ttl=900, show_spinner=False)
def _cached_insider_activity(ticker: str, months: int = 24):
    """Per-session cache wrapper around ``analyze_insider_activity``.

    Lets this panel and the downstream insider tab share the same
    computation: whichever runs first pays the cost, the second hits
    the Streamlit cache. Falls back to ``None`` on any failure."""
    try:
        from analysis.insider_analysis import analyze_insider_activity
        return analyze_insider_activity(ticker, months=months)
    except Exception:
        return None


def _build_insiders(insider_res: Any) -> _InsiderSignal:
    """Adapter over the existing ``InsiderActivity`` dataclass.

    Reads ``recent_6m_net_usd``, ``trend``, ``score``. Missing /
    no-data → ``available=False``."""
    if insider_res is None:
        return _InsiderSignal(available=False)
    if not getattr(insider_res, "available", False):
        return _InsiderSignal(available=False)
    net_6m = getattr(insider_res, "recent_6m_net_usd", None)
    trend = getattr(insider_res, "trend", None)
    score = getattr(insider_res, "score", None)
    if net_6m is None and trend is None and score is None:
        return _InsiderSignal(available=False)
    return _InsiderSignal(
        available=True,
        net_6m_usd=float(net_6m) if net_6m is not None else None,
        trend=str(trend) if trend else None,
        score=int(score) if score is not None else None,
    )


# ============================================================
# Synthesis — combines the four signals into one paragraph
# ============================================================
def _synthesise(
    m: _MarketSignal, a: _AnalystSignal,
    mu: _MultiplesSignal, i: _InsiderSignal,
) -> str:
    parts: list[str] = []

    # 1. Market reading
    if m.available and m.implied_growth is not None:
        ig_pct = m.implied_growth * 100
        if m.gap is not None and m.gap > 0.05:
            parts.append(
                f"El mercado descuenta **{ig_pct:+.1f}% CAGR**, "
                f"{m.gap*100:+.1f}pp por encima del histórico — "
                f"premium de crecimiento agresivo."
            )
        elif m.gap is not None and m.gap < -0.05:
            parts.append(
                f"El mercado descuenta **{ig_pct:+.1f}% CAGR**, "
                f"{m.gap*100:+.1f}pp por debajo del histórico — "
                f"expectativa pesimista o reversión a la media."
            )
        else:
            parts.append(
                f"El mercado descuenta **{ig_pct:+.1f}% CAGR**, "
                f"en línea con el histórico."
            )

    # 2. Sell-side reading
    if a.available:
        if a.pt_upside is not None:
            tilt = ("upside" if a.pt_upside > 0.05
                    else "downside" if a.pt_upside < -0.05
                    else "fair")
            parts.append(
                f"Los analistas ({a.n_analysts or '—'}) proyectan "
                f"target {_format_pct(a.pt_upside)} → {tilt}."
            )
        elif a.pct_buy is not None:
            parts.append(
                f"El sell-side se inclina "
                f"{int(a.pct_buy*100)}% buy / "
                f"{int((a.pct_sell or 0)*100)}% sell."
            )

    # 3. Multiples reading
    if mu.available and mu.label:
        label_es = {
            "stretched":  "en niveles muy elevados",
            "elevated":   "elevados",
            "normal":     "en zona normal",
            "depressed":  "deprimidos",
        }.get(mu.label, mu.label)
        parts.append(f"Los múltiplos cotizan {label_es}.")

    # 4. Insiders reading
    if i.available and i.net_6m_usd is not None:
        if i.net_6m_usd > 1e6:
            insider_msg = (
                f"Insiders **compraron netos** {_format_usd_short(i.net_6m_usd)} "
                f"en los últimos 6m — convicción interna."
            )
        elif i.net_6m_usd < -1e6:
            insider_msg = (
                f"Insiders **vendieron netos** {_format_usd_short(i.net_6m_usd)} "
                f"en los últimos 6m — descarga interna."
            )
        else:
            insider_msg = "Actividad insider neutra en los últimos 6m."
        parts.append(insider_msg)

    # 5. Dissonance flag — explicit when signals disagree meaningfully
    dissonance: list[str] = []
    aggressive_market = (m.available and m.implied_growth is not None
                         and m.implied_growth >= 0.15)
    insiders_selling = (i.available and i.net_6m_usd is not None
                        and i.net_6m_usd < -1e6)
    stretched_mult = (mu.available and mu.label in ("stretched", "elevated"))
    analyst_downside = (a.available and a.pt_upside is not None
                        and a.pt_upside < -0.05)

    if aggressive_market and insiders_selling:
        dissonance.append(
            "el mercado paga por crecimiento agresivo mientras los "
            "insiders se descargan"
        )
    if stretched_mult and analyst_downside:
        dissonance.append(
            "múltiplos premium con sell-side señalando downside"
        )

    if dissonance:
        parts.append(
            "⚠️ **Disonancia entre señales:** " + " y ".join(dissonance) + "."
        )

    if not parts:
        return "Datos insuficientes para sintetizar la expectativa de los inversores."
    return " ".join(parts)


# ============================================================
# Renderer
# ============================================================
def _card(label: str, value_html: str, sub_html: str = "") -> str:
    """One-cell card. Returns an HTML string (rendered together with the rest)."""
    sub = (f'<div style="font-size:11px;color:#94a3b8;margin-top:4px;'
           f'line-height:1.4;">{sub_html}</div>') if sub_html else ""
    return (
        f'<div style="background:#0f172a;border:1px solid #334155;'
        f'border-radius:8px;padding:14px 16px;">'
        f'<div style="font-size:10px;color:#94a3b8;letter-spacing:0.1em;'
        f'text-transform:uppercase;margin-bottom:6px;">{label}</div>'
        f'<div style="font-size:18px;color:#e2e8f0;font-weight:600;'
        f'line-height:1.2;">{value_html}</div>'
        f'{sub}'
        f'</div>'
    )


def render_investor_expectations(
    *,
    ticker: str,
    current_price: Optional[float],
    implied_growth: Optional[float],
    historical_cagr: Optional[float],
    info: Optional[dict],
    insider_res: Any = None,
) -> None:
    """Render the 4-card grid + synthesis paragraph.

    Most inputs are already-computed upstream artefacts (no fresh API
    calls for them). Two integrations are lazy:

    - Analyst consensus → single Finnhub call, cached at the provider
      layer.
    - Insider activity → if the caller hasn't already analysed it,
      we call ``analyze_insider_activity`` through
      ``_cached_insider_activity`` so the downstream insider tab
      reuses the same result without re-fetching.

    Renders nothing only when *all four* signals are unavailable."""
    m  = _build_market(implied_growth, historical_cagr)
    a  = _build_analysts(ticker, current_price)
    mu = _build_multiples(info or {})
    if insider_res is None:
        insider_res = _cached_insider_activity(ticker, months=24)
    i  = _build_insiders(insider_res)

    if not any((m.available, a.available, mu.available, i.available)):
        return

    st.markdown(
        '<div class="eq-section-label" style="margin-top:18px;">'
        'EXPECTATIVA DE LOS INVERSORES · 4 SEÑALES</div>',
        unsafe_allow_html=True,
    )

    # ---- Card values ----
    if m.available and m.implied_growth is not None:
        m_value = f"{m.implied_growth*100:+.1f}%"
        m_sub = (f"CAGR implícito · histórico "
                 f"{_format_pct(m.historical_cagr)}"
                 if m.historical_cagr is not None
                 else "CAGR implícito (sin histórico)")
    else:
        m_value, m_sub = "—", "Reverse-DCF no disponible"

    if a.available:
        if a.pt_mean is not None:
            a_value = f"${a.pt_mean:,.0f}"
            a_sub = f"PT {_format_pct(a.pt_upside)} · {a.n_analysts or '—'} analistas"
        else:
            a_value = (f"{int(a.pct_buy*100)}% Buy"
                       if a.pct_buy is not None else "—")
            a_sub = f"Distribución sell-side"
    else:
        a_value, a_sub = "—", "Sin cobertura Finnhub"

    if mu.available:
        mu_value = _format_mult(mu.pe_ttm)
        sub_bits: list[str] = []
        if mu.pe_forward is not None:
            sub_bits.append(f"Fwd P/E {_format_mult(mu.pe_forward)}")
        if mu.ev_ebitda is not None:
            sub_bits.append(f"EV/EBITDA {_format_mult(mu.ev_ebitda)}")
        if mu.ps is not None:
            sub_bits.append(f"P/S {_format_mult(mu.ps)}")
        mu_sub = " · ".join(sub_bits) if sub_bits else "P/E TTM"
    else:
        mu_value, mu_sub = "—", "Sin múltiplos en snapshot"

    if i.available and i.net_6m_usd is not None:
        i_value = _format_usd_short(i.net_6m_usd)
        trend_es = {
            "increasing": "↑ aumentando",
            "decreasing": "↓ disminuyendo",
            "stable":     "→ estable",
        }.get(i.trend or "", i.trend or "—")
        i_sub = f"Net 6m · trend {trend_es}"
    else:
        i_value, i_sub = "—", "Sin datos de insiders"

    # ---- Grid 2×2 (CSS grid via plain HTML — keeps everything in one block) ----
    st.markdown(
        '<div style="display:grid;grid-template-columns:1fr 1fr;'
        'gap:12px;margin-top:6px;">'
        + _card("Mercado (implied growth)", m_value, m_sub)
        + _card("Analistas (sell-side)", a_value, a_sub)
        + _card("Múltiplos (actuales)", mu_value, mu_sub)
        + _card("Insiders (6m)", i_value, i_sub)
        + '</div>',
        unsafe_allow_html=True,
    )

    # ---- Synthesis ----
    synth = _synthesise(m, a, mu, i)
    st.markdown(
        '<div style="margin-top:12px;padding:12px 16px;'
        'background:#0b1220;border-left:3px solid #f59e0b;'
        'border-radius:0 6px 6px 0;font-size:13px;'
        'color:#cbd5e1;line-height:1.5;">'
        f'<span style="color:#94a3b8;font-size:10px;letter-spacing:0.1em;'
        f'text-transform:uppercase;font-weight:600;">Síntesis</span><br>'
        f'{synth}'
        '</div>',
        unsafe_allow_html=True,
    )

"""
Latest news for the active ticker — ordered newest → oldest.

Thin wrapper around ``analysis.news_aggregator.fetch_news_for_ticker``
that re-sorts by ``published_at`` (the aggregator's default order is
relevance) and renders a compact list of headlines with source,
relative date, sentiment chip and click-through to the original
article.

API cost: the underlying aggregator is ``@st.cache_data(ttl=1800)``
so re-renders within 30 min do not re-hit yfinance / Finnhub /
Marketaux. The first fetch counts one call per active provider
against the API-usage tracker — visible in the API Usage page.
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional

import streamlit as st


# ============================================================
# Helpers
# ============================================================
def _relative_date(when: Optional[datetime]) -> str:
    """Human-friendly relative date — '2 h', '3 d', '1 sem'."""
    if when is None:
        return "—"
    now = datetime.now(timezone.utc)
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    delta = now - when
    secs = delta.total_seconds()
    if secs < 60:
        return "ahora"
    if secs < 3600:
        return f"{int(secs // 60)} min"
    if secs < 86400:
        return f"{int(secs // 3600)} h"
    if secs < 604800:
        return f"{int(secs // 86400)} d"
    if secs < 2592000:
        return f"{int(secs // 604800)} sem"
    return f"{int(secs // 2592000)} mes"


def _sentiment_chip(score: Optional[float], label: Optional[str]) -> str:
    """Inline HTML chip — green/red/grey by sentiment polarity."""
    if score is None and not label:
        return ""
    if score is not None:
        if score >= 0.15:
            color, text = "#10b981", "POSITIVO"
        elif score <= -0.15:
            color, text = "#ef4444", "NEGATIVO"
        else:
            color, text = "#94a3b8", "NEUTRAL"
    else:
        lab = (label or "").lower()
        if "pos" in lab:
            color, text = "#10b981", "POSITIVO"
        elif "neg" in lab:
            color, text = "#ef4444", "NEGATIVO"
        else:
            color, text = "#94a3b8", "NEUTRAL"
    return (
        f"<span style='display:inline-block;padding:1px 6px;"
        f"border-radius:3px;background:{color}22;color:{color};"
        f"font-size:10px;font-weight:600;letter-spacing:0.05em;'>"
        f"{text}</span>"
    )


# ============================================================
# Public entry point
# ============================================================
def render_latest_news_section(
    ticker: str,
    *,
    lookback_days: int = 30,
    max_items: int = 15,
) -> None:
    """Render the ordered list of latest news for the ticker.

    Newest at top. Falls back to a caption when no news / no API
    keys configured — never raises into the host page."""
    if not ticker:
        return

    st.markdown(
        '<div class="eq-section-label">ÚLTIMAS NOTICIAS</div>',
        unsafe_allow_html=True,
    )

    try:
        from analysis.news_aggregator import fetch_news_for_ticker
        items = fetch_news_for_ticker(
            ticker, lookback_days=lookback_days, max_items=max_items)
    except Exception as e:
        st.caption(f"No se pudieron cargar noticias: {type(e).__name__}")
        return

    if not items:
        st.caption(
            "Sin noticias en los últimos "
            f"{lookback_days} días. Verificá que las API keys de "
            "Finnhub / Marketaux estén configuradas para mayor "
            "cobertura."
        )
        return

    # Re-sort newest → oldest (aggregator ranks by relevance by default).
    items_sorted = sorted(
        items,
        key=lambda x: x.published_at or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )

    st.caption(
        f"{len(items_sorted)} titulares · ordenados de más recientes a "
        f"más antiguos · ventana {lookback_days} días"
    )

    # Render as a stack of compact rows. One markdown block per item
    # so each title is a real clickable anchor.
    for it in items_sorted:
        title = (it.title or "Sin título").replace("<", "&lt;").replace(">", "&gt;")
        url = it.url or "#"
        src = (it.source or "—")
        when = _relative_date(it.published_at)
        chip = _sentiment_chip(it.sentiment_score, it.sentiment_label)
        snippet = (it.snippet or "").replace("<", "&lt;").replace(">", "&gt;")
        if len(snippet) > 240:
            snippet = snippet[:240].rsplit(" ", 1)[0] + "…"

        st.markdown(
            f"""
<div style="border-left:2px solid #334155;padding:8px 12px;
margin-bottom:10px;background:#0f172a;border-radius:0 4px 4px 0;">
  <div style="margin-bottom:4px;">
    <a href="{url}" target="_blank" rel="noopener noreferrer"
       style="color:#e2e8f0;font-weight:600;text-decoration:none;
font-size:14px;line-height:1.35;">
      {title}
    </a>
  </div>
  <div style="display:flex;gap:8px;align-items:center;
font-size:11px;color:#94a3b8;margin-bottom:{'4px' if snippet else '0'};">
    <span style="color:#cbd5e1;">{src}</span>
    <span>·</span>
    <span>{when}</span>
    {chip}
  </div>
  {f'<div style="font-size:12px;color:#94a3b8;line-height:1.4;">{snippet}</div>' if snippet else ''}
</div>
""",
            unsafe_allow_html=True,
        )

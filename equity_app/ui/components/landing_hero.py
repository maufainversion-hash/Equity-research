"""
Hero searchbox para el estado inicial de Equity Analysis.

Un titular centrado sobre un selector en cascada de tres niveles —
País → Sector → Empresa — para que el mismo pipeline de equity research
analice empresas de cualquier mercado del catálogo. Elegís el país, la
lista de sectores se filtra a ese mercado; elegís el sector, la lista de
empresas se filtra a ese país + sector. ``st.selectbox`` es
type-searchable de fábrica.

El catálogo (país · sector · ticker) vive en ``data.company_catalog``.
"""
from __future__ import annotations
from typing import Optional

import streamlit as st

from data.company_catalog import companies, countries, sectors


def _safe_select(label: str, options: list[str], key: str,
                 *, preferred: Optional[str] = None, **kw) -> Optional[str]:
    """``st.selectbox`` robusto ante cascadas: si el valor guardado en
    session_state ya no es válido para las nuevas ``options`` (porque
    cambió un selector de arriba), lo descarta antes de renderizar — así
    el widget no levanta excepción y cae al default."""
    if not options:
        return None
    if key in st.session_state and st.session_state[key] not in options:
        del st.session_state[key]
    index = 0
    if preferred and preferred in options:
        index = options.index(preferred)
    return st.selectbox(label, options=options, index=index, key=key, **kw)


def render_landing_hero(*, key: str = "landing_searchbox") -> Optional[str]:
    """
    Render del titular + selector en cascada País → Sector → Empresa +
    botón Analyze.

    Devuelve el ticker que el usuario eligió Y confirmó (clic en
    Analyze), o ``None`` si todavía no lo hizo.
    """
    st.markdown(
        '<div style="text-align:center; padding-top:36px; padding-bottom:8px;">'
        '<div class="eq-section-label" style="color:var(--accent);">'
        'EQUITY RESEARCH</div>'
        '<div style="color:var(--text-primary); font-size:24px; font-weight:500; '
        'letter-spacing:-0.3px; margin-top:6px;">'
        'Analyze any public company</div>'
        '<div style="color:var(--text-muted); font-size:12px; margin-top:6px;">'
        'Pick country, sector and company, then Analyze. Same analysis '
        'for US, Europe, Asia and Latin America.'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    _, mid, _ = st.columns([1, 5, 1])
    with mid:
        # Country · Sector · Company, side by side.
        co_col, se_col, em_col = st.columns([1.3, 1.5, 3.0])
        with co_col:
            country = _safe_select(
                "Country",
                countries(),
                f"{key}_country",
                preferred="United States",
                label_visibility="collapsed",
            )
        with se_col:
            sector = _safe_select(
                "Sector",
                sectors(country) if country else [],
                f"{key}_sector",
                preferred="Technology",
                label_visibility="collapsed",
            )
        with em_col:
            roster = (companies(country, sector)
                      if country and sector else [])
            labels = [f"{c.ticker} — {c.name}" for c in roster]
            # Default: AAPL if present, else first.
            default_lbl = next(
                (lbl for lbl in labels if lbl.startswith("AAPL ")), None)
            chosen_label = _safe_select(
                "Company",
                labels,
                key,
                preferred=default_lbl,
                label_visibility="collapsed",
                placeholder="🔎  Search company…",
            )
        analyze = st.button(
            "Analyze",
            type="primary",
            width="stretch",
            key=f"{key}_analyze",
        )

    if analyze and chosen_label:
        return chosen_label.split(" — ", 1)[0].strip().upper()
    return None

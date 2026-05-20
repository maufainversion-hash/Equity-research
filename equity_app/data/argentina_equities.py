"""
Acciones del mercado argentino — panel líder del Merval (BYMA).

Las acciones argentinas cotizan localmente en pesos bajo el sufijo
``.BA`` (ej. ``GGAL.BA``), accesible vía yfinance sin API key. La
conversión a dólares usa el CCL de :mod:`data.fx_rates` — precio en
pesos ÷ CCL = valor en USD. No se hardcodea ningún ratio: precios y
tipo de cambio son siempre en vivo.

``MERVAL_PANEL_LIDER`` es una lista curada del panel líder. Los
tickers ``.BA`` y los nombres son estables; el ADR en NYSE es
metadata opcional (para una futura vista de arbitraje). Refrescar la
lista manualmente cuando el panel cambie de constituyentes.
"""
from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Optional

import streamlit as st

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class AREquity:
    """Un constituyente del panel líder."""
    ticker: str                    # ticker BYMA con sufijo .BA
    name:   str
    sector: str
    adr:    Optional[str] = None   # ticker del ADR en NYSE, si existe


# Panel líder del Merval — lista curada (refrescar manualmente al
# cambiar los constituyentes). Tickers .BA + nombres son estables.
MERVAL_PANEL_LIDER: tuple[AREquity, ...] = (
    AREquity("GGAL.BA",  "Grupo Financiero Galicia",        "Bancos",       "GGAL"),
    AREquity("BMA.BA",   "Banco Macro",                     "Bancos",       "BMA"),
    AREquity("BBAR.BA",  "BBVA Argentina",                  "Bancos",       "BBAR"),
    AREquity("SUPV.BA",  "Grupo Supervielle",               "Bancos",       "SUPV"),
    AREquity("VALO.BA",  "Grupo Financiero Valores",        "Bancos",       None),
    AREquity("YPFD.BA",  "YPF",                             "Energía",      "YPF"),
    AREquity("PAMP.BA",  "Pampa Energía",                   "Energía",      "PAM"),
    AREquity("CEPU.BA",  "Central Puerto",                  "Energía",      "CEPU"),
    AREquity("EDN.BA",   "Edenor",                          "Energía",      "EDN"),
    AREquity("TGSU2.BA", "Transportadora de Gas del Sur",   "Energía",      "TGS"),
    AREquity("TGNO4.BA", "Transportadora de Gas del Norte", "Energía",      None),
    AREquity("TRAN.BA",  "Transener",                       "Energía",      None),
    AREquity("METR.BA",  "MetroGAS",                        "Energía",      None),
    AREquity("TXAR.BA",  "Ternium Argentina",               "Materiales",   None),
    AREquity("ALUA.BA",  "Aluar",                           "Materiales",   None),
    AREquity("LOMA.BA",  "Loma Negra",                      "Materiales",   "LOMA"),
    AREquity("TECO2.BA", "Telecom Argentina",               "Comunicación", "TEO"),
    AREquity("CVH.BA",   "Cablevisión Holding",             "Comunicación", None),
    AREquity("CRES.BA",  "Cresud",                          "Agro",         "CRESY"),
    AREquity("MIRG.BA",  "Mirgor",                          "Industrial",   None),
    AREquity("COME.BA",  "Sociedad Comercial del Plata",    "Holding",      None),
    AREquity("BYMA.BA",  "Bolsas y Mercados Argentinos",    "Financiero",   None),
)

_BY_TICKER: dict[str, AREquity] = {e.ticker: e for e in MERVAL_PANEL_LIDER}


def _last_two_closes(ticker: str) -> tuple[Optional[float], Optional[float]]:
    """(último cierre, cierre previo) en ARS vía yfinance. (None, None)
    si falla — los .BA no exponen fast_info.last_price, hay que usar
    el historial."""
    try:
        import yfinance as yf
        h = yf.Ticker(ticker).history(period="7d")
    except Exception as e:
        log.debug("yfinance .BA history failed for %s: %s", ticker, e)
        return None, None
    if h is None or h.empty or "Close" not in h.columns:
        return None, None
    closes = h["Close"].dropna()
    if closes.empty:
        return None, None
    last = float(closes.iloc[-1])
    prev = float(closes.iloc[-2]) if len(closes) >= 2 else None
    return last, prev


@st.cache_data(ttl=900, show_spinner=False)
def fetch_ar_quote(ticker: str) -> dict:
    """Cotización de una acción argentina: precio en ARS, su equivalente
    en USD (vía CCL) y la variación diaria.

    Devuelve ``{}`` si el ticker no resuelve — el caller degrada la fila."""
    eq = _BY_TICKER.get(ticker)
    last_ars, prev_ars = _last_two_closes(ticker)
    if last_ars is None:
        return {}

    from data.fx_rates import get_ccl_rate
    ccl = get_ccl_rate()

    change_pct = None
    if prev_ars and prev_ars > 0:
        change_pct = (last_ars / prev_ars - 1.0) * 100.0

    return {
        "ticker":     ticker,
        "name":       eq.name if eq else ticker,
        "sector":     eq.sector if eq else "—",
        "adr":        eq.adr if eq else None,
        "price_ars":  last_ars,
        "price_usd":  (last_ars / ccl) if ccl else None,
        "ccl_used":   ccl,
        "change_pct": change_pct,
    }


@st.cache_data(ttl=900, show_spinner=False)
def fetch_merval_panel() -> list[dict]:
    """Cotizaciones de todo el panel líder. Ordenado por nombre; las
    filas que no resuelven se omiten silenciosamente."""
    out: list[dict] = []
    for eq in MERVAL_PANEL_LIDER:
        q = fetch_ar_quote(eq.ticker)
        if q:
            out.append(q)
    out.sort(key=lambda r: r["name"])
    return out

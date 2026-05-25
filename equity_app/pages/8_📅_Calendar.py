"""
Calendar — earnings, FOMC, IPOs and economic events.

Four sections, all forward-looking from today:

- EARNINGS this week — market-wide via Finnhub
  /calendar/earnings, capped to keep noise manageable.
- FOMC MEETINGS — hardcoded official schedule (Fed publishes a year
  ahead; refresh manually when each annual schedule drops).
- IPO CALENDAR — upcoming offerings via Finnhub /calendar/ipo.
- ECONOMIC EVENTS — high-impact US macro releases that the FOMC and
  the equity market actually react to (CPI / PPI / NFP / GDP /
  PCE), with their typical release cadence. Also hardcoded — these
  aren't on a free API endpoint that's worth wiring up.

API cost: 2 Finnhub calls per page load, cached 30 min so
revisits don't burn quota. The hardcoded data refreshes only on
deploy.
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from datetime import datetime, timedelta, timezone, date
from typing import Optional

import pandas as pd
import streamlit as st


# ============================================================
# Hardcoded calendars — refresh once a year when the Fed publishes
# the next year's FOMC schedule (federalreserve.gov/monetarypolicy/
# fomccalendars.htm) and when known macro release dates drift.
# ============================================================
# 2-day FOMC meetings — only the second day (statement + presser) is
# the market-moving event. Source: federalreserve.gov, accurate as
# of the 2026 published schedule.
_FOMC_2026: list[tuple[date, str]] = [
    (date(2026,  1, 28), "FOMC · Decisión + conferencia"),
    (date(2026,  3, 18), "FOMC · Decisión + SEP + conferencia"),
    (date(2026,  4, 29), "FOMC · Decisión + conferencia"),
    (date(2026,  6, 17), "FOMC · Decisión + SEP + conferencia"),
    (date(2026,  7, 29), "FOMC · Decisión + conferencia"),
    (date(2026,  9, 16), "FOMC · Decisión + SEP + conferencia"),
    (date(2026, 11,  4), "FOMC · Decisión + conferencia"),
    (date(2026, 12, 16), "FOMC · Decisión + SEP + conferencia"),
]
# Economic releases — typical release dates, BLS / BEA / Census.
# Pattern is consistent enough to publish a quarter ahead. Tag
# means: when in the month the release lands (1=first week, etc.).
_ECON_PATTERN: list[tuple[str, str, str]] = [
    # (label, cadence, when)
    ("Nonfarm Payrolls (NFP)",         "Mensual", "1er viernes"),
    ("CPI (Consumer Price Index)",     "Mensual", "Mid-month (10-14)"),
    ("PPI (Producer Price Index)",     "Mensual", "Mid-month (~día 13)"),
    ("Retail Sales",                   "Mensual", "Mid-month (~día 15)"),
    ("PCE (Personal Income & Outlays)", "Mensual", "Última semana"),
    ("GDP Advance Estimate",           "Trimestral", "Fines del mes posterior al trim."),
    ("Jobless Claims",                 "Semanal", "Cada jueves 8:30am ET"),
]


def _upcoming_fomc(today: date, n: int = 4) -> list[tuple[date, str]]:
    return [(d, label) for d, label in _FOMC_2026 if d >= today][:n]


# ============================================================
# Page header
# ============================================================
st.markdown(
    '<div class="eq-section-label">📅 CALENDAR</div>',
    unsafe_allow_html=True,
)
st.caption(
    "Próximos catalizadores: earnings, FOMC, IPOs y eventos macro "
    "de alto impacto. Earnings + IPOs vienen vivos de Finnhub; "
    "FOMC y macro están hardcodeados (refrescar al cambiar el año)."
)
TODAY = datetime.now(timezone.utc).date()


# ============================================================
# Helpers
# ============================================================
def _fmt_date(d) -> str:
    """ISO date / pd.Timestamp / date → 'Jue 14 may' formato corto."""
    if d is None:
        return "—"
    if isinstance(d, pd.Timestamp):
        if pd.isna(d):
            return "—"
        d = d.date()
    if not isinstance(d, date):
        try:
            d = pd.to_datetime(d).date()
        except Exception:
            return "—"
    _DOW = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    _MES = ["ene", "feb", "mar", "abr", "may", "jun",
            "jul", "ago", "sep", "oct", "nov", "dic"]
    return f"{_DOW[d.weekday()]} {d.day:02d} {_MES[d.month - 1]}"


def _days_to(d: date) -> str:
    if d is None or not isinstance(d, date):
        return "—"
    delta = (d - TODAY).days
    if delta < 0:
        return f"hace {abs(delta)}d"
    if delta == 0:
        return "**hoy**"
    if delta == 1:
        return "mañana"
    if delta < 7:
        return f"en {delta}d"
    if delta < 30:
        weeks = delta // 7
        return f"en {weeks} sem"
    return f"en {delta // 30} mes"


def _section_header(label: str, sub: Optional[str] = None) -> None:
    sub_html = (f'<span style="color:#94A3B8;font-size:11px;'
                f'margin-left:10px;">{sub}</span>' if sub else "")
    st.markdown(
        f'<div class="eq-section-label" style="margin-top:18px;">'
        f'{label}{sub_html}</div>',
        unsafe_allow_html=True,
    )


# ============================================================
# Section 1 — Upcoming earnings
# ============================================================
_section_header("EARNINGS · PRÓXIMOS 14 DÍAS",
                "Cobertura S&P + ADRs principales · vía Finnhub")

try:
    from data.finnhub_provider import (
        is_available as _fh_ok, fetch_market_earnings_calendar,
    )
    if not _fh_ok():
        st.caption("Configurá FINNHUB_API_KEY para ver el calendario "
                   "de earnings.")
    else:
        _earnings_cache_key = TODAY.isoformat()

        @st.cache_data(ttl=1800, show_spinner=False)
        def _load_earnings(_cache_key: str) -> pd.DataFrame:
            return fetch_market_earnings_calendar()

        edf = _load_earnings(_earnings_cache_key)
        if edf.empty:
            st.caption("Sin earnings reportados en la ventana.")
        else:
            # Cap to the top by market cap proxy: Finnhub already
            # returns symbol; we don't have mcap, so cap by row count
            # to keep the table readable.
            edf = edf.head(60).copy()
            # Display columns the user actually scans for.
            cols = []
            for c in ("date", "symbol", "epsEstimate", "revenueEstimate", "hour"):
                if c in edf.columns:
                    cols.append(c)
            disp = edf[cols].copy()
            if "date" in disp.columns:
                disp.insert(1, "Cuándo", disp["date"].apply(
                    lambda d: _days_to(d.date()) if pd.notna(d) else "—"))
                disp["date"] = disp["date"].apply(_fmt_date)
            if "revenueEstimate" in disp.columns:
                disp["revenueEstimate"] = disp["revenueEstimate"].apply(
                    lambda v: f"${v/1e9:.2f}B" if pd.notna(v) and v > 0 else "—")
            if "epsEstimate" in disp.columns:
                disp["epsEstimate"] = disp["epsEstimate"].apply(
                    lambda v: f"${v:.2f}" if pd.notna(v) else "—")
            if "hour" in disp.columns:
                _HOUR_LABEL = {"bmo": "Pre-market",
                                "amc": "After-close",
                                "dmh": "Intra-day"}
                disp["hour"] = disp["hour"].apply(
                    lambda h: _HOUR_LABEL.get(str(h or "").lower(), "—"))
            disp.columns = [c.replace("date", "Fecha")
                              .replace("symbol", "Ticker")
                              .replace("epsEstimate", "EPS est.")
                              .replace("revenueEstimate", "Revenue est.")
                              .replace("hour", "Horario") for c in disp.columns]
            st.dataframe(disp, width="stretch", hide_index=True)
            st.caption(f"{len(edf)} reportes en ventana · "
                       "mostrando los primeros 60.")
except Exception as e:
    st.caption(f"Earnings no disponibles: {type(e).__name__}")


# ============================================================
# Section 2 — FOMC meetings
# ============================================================
_section_header("FOMC · REUNIONES DE POLÍTICA MONETARIA",
                "Federal Reserve · días con statement + conferencia")

upcoming = _upcoming_fomc(TODAY, n=4)
if not upcoming:
    st.caption("Sin reuniones FOMC programadas en lo que queda del "
               "año. Refrescá la lista cuando salga el calendario "
               "del próximo año.")
else:
    fomc_rows = []
    for d, label in upcoming:
        fomc_rows.append({
            "Fecha":     _fmt_date(d),
            "Cuándo":    _days_to(d),
            "Evento":    label,
        })
    st.dataframe(pd.DataFrame(fomc_rows), width="stretch", hide_index=True)
    # Highlight the next meeting as a callout
    next_d, next_label = upcoming[0]
    days = (next_d - TODAY).days
    if 0 <= days <= 14:
        st.warning(
            f"⏰ Próxima reunión en **{days} días** ({_fmt_date(next_d)}) — "
            f"{next_label}. Evitar posiciones grandes nuevas hasta después.",
            icon="📌",
        )


# ============================================================
# Section 3 — IPO calendar
# ============================================================
_section_header("IPOs · PRÓXIMOS 30 DÍAS",
                "Calendario de salidas a bolsa · vía Finnhub")

try:
    from data.finnhub_provider import (
        is_available as _fh_ok2, fetch_ipo_calendar,
    )
    if not _fh_ok2():
        st.caption("Configurá FINNHUB_API_KEY para ver IPOs.")
    else:
        _ipo_cache_key = TODAY.isoformat()

        @st.cache_data(ttl=3600, show_spinner=False)
        def _load_ipos(_cache_key: str) -> pd.DataFrame:
            return fetch_ipo_calendar()

        idf = _load_ipos(_ipo_cache_key)
        if idf.empty:
            st.caption("Sin IPOs anunciadas en la ventana.")
        else:
            cols = []
            for c in ("date", "symbol", "name", "exchange",
                      "numberOfShares", "price", "totalSharesValue", "status"):
                if c in idf.columns:
                    cols.append(c)
            disp = idf[cols].copy()
            if "date" in disp.columns:
                disp.insert(1, "Cuándo", disp["date"].apply(
                    lambda d: _days_to(d.date()) if pd.notna(d) else "—"))
                disp["date"] = disp["date"].apply(_fmt_date)
            if "totalSharesValue" in disp.columns:
                disp["totalSharesValue"] = disp["totalSharesValue"].apply(
                    lambda v: f"${v/1e9:.2f}B" if pd.notna(v) and v >= 1e9
                    else (f"${v/1e6:.1f}M" if pd.notna(v) and v > 0 else "—"))
            if "numberOfShares" in disp.columns:
                disp["numberOfShares"] = disp["numberOfShares"].apply(
                    lambda v: f"{int(v):,}" if pd.notna(v) else "—")
            if "price" in disp.columns:
                disp["price"] = disp["price"].apply(
                    lambda v: str(v) if pd.notna(v) and str(v).strip() else "—")
            disp.columns = [
                c.replace("date", "Fecha")
                 .replace("symbol", "Ticker")
                 .replace("name", "Empresa")
                 .replace("exchange", "Bolsa")
                 .replace("numberOfShares", "# Acciones")
                 .replace("price", "Rango precio")
                 .replace("totalSharesValue", "Tamaño")
                 .replace("status", "Estado")
                for c in disp.columns
            ]
            st.dataframe(disp, width="stretch", hide_index=True)
            st.caption(f"{len(idf)} IPOs en ventana.")
except Exception as e:
    st.caption(f"IPOs no disponibles: {type(e).__name__}")


# ============================================================
# Section 4 — Economic events (cadence-based, hardcoded)
# ============================================================
_section_header("EVENTOS MACRO · CADENCIA DE RELEASES",
                "Releases de alto impacto sobre el equity market")

econ_rows = [
    {"Indicador": label, "Frecuencia": cadence, "Cuándo sale": when}
    for label, cadence, when in _ECON_PATTERN
]
st.dataframe(pd.DataFrame(econ_rows), width="stretch", hide_index=True)
st.caption(
    "Estos no son fechas exactas — son los **patrones de release** "
    "que la prensa financiera sigue. Para fechas precisas del mes "
    "actual: BLS (bls.gov/schedule), BEA (bea.gov/news/schedule) "
    "y Federal Reserve."
)


# ============================================================
# Footer
# ============================================================
st.markdown("---")
st.caption(
    "Earnings + IPOs se cachean 30-60 min para no quemar cuota de "
    "Finnhub (visible en la página API Usage). El calendario FOMC y "
    "los patrones macro están hardcodeados — actualizarlos al cambiar "
    "de año o cuando la Fed publica un schedule nuevo."
)

"""
Calendar — earnings, FOMC, IPOs and economic events.

Layout:
- Header strip with 4 KPI cards (next event per kind).
- EARNINGS · upcoming 14d — card list with urgency colour.
- FOMC · next meetings — featured countdown card + table.
- IPOs · upcoming 30d — card list.
- ECONOMIC EVENTS · release cadence — 2-col grid.

Data sources: Finnhub for earnings + IPOs (cached 30-60 min);
hardcoded calendars for FOMC + macro release patterns (refresh
once a year).
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
# next year's FOMC schedule (federalreserve.gov/monetarypolicy/
# fomccalendars.htm).
# ============================================================
_FOMC_2026: list[tuple[date, str]] = [
    (date(2026,  1, 28), "Decisión + conferencia"),
    (date(2026,  3, 18), "Decisión + SEP + conferencia"),
    (date(2026,  4, 29), "Decisión + conferencia"),
    (date(2026,  6, 17), "Decisión + SEP + conferencia"),
    (date(2026,  7, 29), "Decisión + conferencia"),
    (date(2026,  9, 16), "Decisión + SEP + conferencia"),
    (date(2026, 11,  4), "Decisión + conferencia"),
    (date(2026, 12, 16), "Decisión + SEP + conferencia"),
]

_ECON_PATTERN: list[tuple[str, str, str, str]] = [
    # (label, cadence, when, descripción 1-línea)
    ("Nonfarm Payrolls (NFP)", "Mensual", "1er viernes",
     "Empleo + wages — el indicador más vigilado de actividad."),
    ("CPI",                    "Mensual", "Día 10-14",
     "Inflación headline — driver clave de expectativas de Fed."),
    ("PPI",                    "Mensual", "Día ~13",
     "Inflación al productor — leading indicator de CPI."),
    ("Retail Sales",           "Mensual", "Día ~15",
     "Consumo nominal — termómetro del consumer."),
    ("PCE",                    "Mensual", "Última semana",
     "Inflación preferida de la Fed."),
    ("GDP Advance",            "Trimestral", "Fines del mes posterior al trim.",
     "Primera lectura del crecimiento — alto error pero alto impacto."),
    ("Jobless Claims",         "Semanal", "Jueves 8:30am ET",
     "Salud laboral en tiempo real."),
]


def _upcoming_fomc(today: date, n: int = 4) -> list[tuple[date, str]]:
    return [(d, label) for d, label in _FOMC_2026 if d >= today][:n]


# ============================================================
# Page header
# ============================================================
st.markdown(
    """
<div style="margin-bottom:24px;">
  <div style="display:flex;align-items:baseline;gap:14px;">
    <h1 style="margin:0;font-size:26px;font-weight:700;color:#F3F4F6;">
      📅 Calendar
    </h1>
    <span style="color:#94A3B8;font-size:12px;letter-spacing:0.06em;
text-transform:uppercase;">próximos catalizadores</span>
  </div>
  <div style="color:#94A3B8;font-size:13px;margin-top:6px;">
    Earnings, FOMC, IPOs y macro releases. Datos vivos de Finnhub
    para earnings/IPOs · calendario FOMC y patrones macro hardcodeados.
  </div>
</div>
""",
    unsafe_allow_html=True,
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


def _days_to(d: date) -> tuple[int, str]:
    """Returns (delta_days, human_label)."""
    if d is None or not isinstance(d, date):
        return (10**9, "—")
    delta = (d - TODAY).days
    if delta < 0:
        return (delta, f"hace {abs(delta)}d")
    if delta == 0:
        return (0, "hoy")
    if delta == 1:
        return (1, "mañana")
    if delta < 7:
        return (delta, f"en {delta}d")
    if delta < 30:
        return (delta, f"en {delta // 7} sem")
    return (delta, f"en {delta // 30} mes")


def _urgency_color(days: int) -> tuple[str, str]:
    """(border_color, accent_color) by days-to-event."""
    if days < 0:
        return ("#475569", "#475569")            # past — muted
    if days <= 2:
        return ("#EF4444", "#F87171")            # red — imminent
    if days <= 7:
        return ("#F59E0B", "#FBBF24")            # amber — this week
    if days <= 30:
        return ("#10B981", "#10B981")            # green — soon
    return ("#3B82F6", "#60A5FA")                # blue — further out


# ============================================================
# Top KPI strip — 4 cards: next earnings, next FOMC, next IPO, today
# ============================================================
def _kpi_card(label: str, value: str, sub: str, accent: str) -> str:
    return (
        f'<div style="background:#0f172a;border:1px solid #334155;'
        f'border-top:3px solid {accent};border-radius:8px;'
        f'padding:14px 16px;">'
        f'<div style="font-size:10px;color:#94A3B8;letter-spacing:0.08em;'
        f'text-transform:uppercase;margin-bottom:6px;">{label}</div>'
        f'<div style="font-size:20px;font-weight:700;color:#F3F4F6;'
        f'line-height:1.1;font-variant-numeric:tabular-nums;">{value}</div>'
        f'<div style="font-size:11px;color:#94A3B8;margin-top:6px;'
        f'line-height:1.4;">{sub}</div>'
        f'</div>'
    )


# Compute KPIs (best-effort — each guarded so a missing source doesn't blank the strip)
kpi_earnings = ("—", "Sin datos", "#475569")
kpi_ipo = ("—", "Sin datos", "#475569")

try:
    from data.finnhub_provider import (
        is_available as _fh_ok_kpi,
        fetch_market_earnings_calendar,
        fetch_ipo_calendar,
    )
    if _fh_ok_kpi():
        @st.cache_data(ttl=1800, show_spinner=False)
        def _earnings_for_kpi(_k: str) -> pd.DataFrame:
            return fetch_market_earnings_calendar()

        @st.cache_data(ttl=3600, show_spinner=False)
        def _ipos_for_kpi(_k: str) -> pd.DataFrame:
            return fetch_ipo_calendar()

        _edf_kpi = _earnings_for_kpi(TODAY.isoformat())
        _idf_kpi = _ipos_for_kpi(TODAY.isoformat())
        if not _edf_kpi.empty and "date" in _edf_kpi.columns:
            n_e = len(_edf_kpi)
            sym = _edf_kpi.iloc[0].get("symbol") or "—"
            d0 = _edf_kpi.iloc[0]["date"]
            d0_d = d0.date() if pd.notna(d0) else None
            _, lab = _days_to(d0_d) if d0_d else (10**9, "—")
            border, accent = _urgency_color(_days_to(d0_d)[0] if d0_d else 99)
            kpi_earnings = (
                f"{n_e}",
                f"Próximo: {sym} ({lab})",
                accent,
            )
        if not _idf_kpi.empty and "date" in _idf_kpi.columns:
            n_i = len(_idf_kpi)
            d0 = _idf_kpi.iloc[0]["date"]
            d0_d = d0.date() if pd.notna(d0) else None
            sym = _idf_kpi.iloc[0].get("symbol") or "—"
            _, lab = _days_to(d0_d) if d0_d else (10**9, "—")
            _, accent = _urgency_color(_days_to(d0_d)[0] if d0_d else 99)
            kpi_ipo = (f"{n_i}", f"Próxima: {sym} ({lab})", accent)
except Exception:
    pass

# FOMC KPI from hardcoded list — always available
_next_fomc = _upcoming_fomc(TODAY, n=1)
if _next_fomc:
    nd, _ = _next_fomc[0]
    days_fomc = (nd - TODAY).days
    _, fomc_lab = _days_to(nd)
    _, fomc_accent = _urgency_color(days_fomc)
    kpi_fomc = (f"{days_fomc}d", f"{_fmt_date(nd)} · {fomc_lab}", fomc_accent)
else:
    kpi_fomc = ("—", "Sin reuniones programadas", "#475569")

# Today KPI — simple but anchors the eye
kpi_today = (_fmt_date(TODAY), TODAY.isoformat(), "#C9A961")

st.markdown(
    '<div style="display:grid;grid-template-columns:repeat(4,1fr);'
    'gap:12px;margin-bottom:24px;">'
    + _kpi_card("Hoy", kpi_today[0], kpi_today[1], kpi_today[2])
    + _kpi_card("Próximo FOMC", kpi_fomc[0], kpi_fomc[1], kpi_fomc[2])
    + _kpi_card("Earnings 14d", kpi_earnings[0], kpi_earnings[1], kpi_earnings[2])
    + _kpi_card("IPOs 30d", kpi_ipo[0], kpi_ipo[1], kpi_ipo[2])
    + '</div>',
    unsafe_allow_html=True,
)


# ============================================================
# Section header helper (reused)
# ============================================================
def _section_header(emoji: str, title: str, sub: str) -> None:
    st.markdown(
        f'<div style="margin-top:8px;margin-bottom:14px;">'
        f'<div style="display:flex;align-items:baseline;gap:10px;">'
        f'<span style="font-size:18px;">{emoji}</span>'
        f'<h2 style="margin:0;font-size:18px;font-weight:600;'
        f'color:#F3F4F6;letter-spacing:-0.01em;">{title}</h2>'
        f'</div>'
        f'<div style="color:#94A3B8;font-size:12px;margin-top:4px;'
        f'margin-left:28px;">{sub}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ============================================================
# Section 1 — Upcoming earnings (card list)
# ============================================================
_section_header("📊", "Earnings · próximos 14 días",
                "Cobertura S&P + ADRs principales · vía Finnhub")

try:
    from data.finnhub_provider import (
        is_available as _fh_ok, fetch_market_earnings_calendar,
    )
    if not _fh_ok():
        st.info("🔑 Configurá FINNHUB_API_KEY para ver el calendario.",
                icon="ℹ️")
    else:
        @st.cache_data(ttl=1800, show_spinner="Cargando earnings…")
        def _load_earnings(_cache_key: str) -> pd.DataFrame:
            return fetch_market_earnings_calendar()

        edf = _load_earnings(TODAY.isoformat())
        if edf.empty:
            st.caption("Sin earnings reportados en la ventana.")
        else:
            # Group by date — cleaner reading than a flat 60-row table.
            edf = edf.head(40).copy()
            _HOUR_LABEL = {"bmo": "🌅 Pre-market",
                           "amc": "🌙 After-close",
                           "dmh": "☀️ Intra-day"}
            cards: list[str] = []
            for _, row in edf.iterrows():
                d_ts = row.get("date")
                d_d = d_ts.date() if pd.notna(d_ts) else None
                days, lab = _days_to(d_d) if d_d else (10**9, "—")
                border, accent = _urgency_color(days)
                sym = str(row.get("symbol") or "—")
                eps_est = row.get("epsEstimate")
                rev_est = row.get("revenueEstimate")
                hour = str(row.get("hour") or "").lower()
                hour_lbl = _HOUR_LABEL.get(hour, "")
                eps_txt = (f"EPS est. <b>${eps_est:.2f}</b>"
                            if pd.notna(eps_est) else "EPS est. —")
                rev_txt = (f"Rev est. <b>${rev_est/1e9:.2f}B</b>"
                            if pd.notna(rev_est) and rev_est > 0
                            else "Rev est. —")
                cards.append(
                    f'<div style="background:#0f172a;border:1px solid #334155;'
                    f'border-left:3px solid {border};border-radius:6px;'
                    f'padding:10px 14px;">'
                    f'<div style="display:flex;justify-content:space-between;'
                    f'align-items:baseline;margin-bottom:4px;">'
                    f'<span style="font-size:14px;font-weight:700;'
                    f'color:#F3F4F6;letter-spacing:0.02em;">{sym}</span>'
                    f'<span style="font-size:11px;color:{accent};'
                    f'font-weight:600;">{lab}</span>'
                    f'</div>'
                    f'<div style="font-size:11px;color:#94A3B8;">'
                    f'{_fmt_date(d_d)} · {hour_lbl}'
                    f'</div>'
                    f'<div style="font-size:11px;color:#cbd5e1;margin-top:6px;">'
                    f'{eps_txt} · {rev_txt}'
                    f'</div>'
                    f'</div>'
                )
            st.markdown(
                '<div style="display:grid;'
                'grid-template-columns:repeat(auto-fill,minmax(220px,1fr));'
                'gap:10px;">'
                + "".join(cards) + '</div>',
                unsafe_allow_html=True,
            )
            st.caption(f"Mostrando {len(edf)} de {len(_load_earnings(TODAY.isoformat()))} "
                       "reportes en la ventana.")
except Exception as e:
    st.warning(f"Earnings no disponibles: {type(e).__name__} — {e}",
               icon="⚠️")


# ============================================================
# Section 2 — FOMC meetings (featured countdown + table)
# ============================================================
st.markdown("<br>", unsafe_allow_html=True)
_section_header("🏛️", "FOMC · reuniones de política monetaria",
                "Federal Reserve · días con statement + conferencia")

upcoming = _upcoming_fomc(TODAY, n=4)
if not upcoming:
    st.info("Sin reuniones FOMC programadas en lo que queda del año. "
            "Refrescá la lista cuando salga el calendario del próximo año.",
            icon="📅")
else:
    next_d, next_label = upcoming[0]
    days = (next_d - TODAY).days
    _, accent = _urgency_color(days)
    # Featured countdown card
    st.markdown(
        f'<div style="background:#0f172a;border:1px solid #334155;'
        f'border-left:4px solid {accent};border-radius:8px;'
        f'padding:18px 20px;margin-bottom:14px;'
        f'display:flex;justify-content:space-between;align-items:center;">'
        f'<div>'
        f'<div style="font-size:10px;color:#94A3B8;letter-spacing:0.08em;'
        f'text-transform:uppercase;margin-bottom:4px;">Próxima reunión</div>'
        f'<div style="font-size:18px;color:#F3F4F6;font-weight:600;">'
        f'{_fmt_date(next_d)}</div>'
        f'<div style="font-size:12px;color:#94A3B8;margin-top:2px;">'
        f'{next_label}</div>'
        f'</div>'
        f'<div style="text-align:right;">'
        f'<div style="font-size:34px;color:{accent};font-weight:700;'
        f'line-height:1;font-variant-numeric:tabular-nums;">{days}</div>'
        f'<div style="font-size:11px;color:#94A3B8;letter-spacing:0.08em;'
        f'text-transform:uppercase;margin-top:4px;">'
        f'{"día" if days == 1 else "días"}</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Table of the next 4 — clean dataframe is fine here
    rows = []
    for d, label in upcoming:
        days_d = (d - TODAY).days
        rows.append({
            "Fecha":  _fmt_date(d),
            "Cuándo": _days_to(d)[1],
            "Evento": label,
        })
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


# ============================================================
# Section 3 — IPO calendar (card list)
# ============================================================
st.markdown("<br>", unsafe_allow_html=True)
_section_header("🚀", "IPOs · próximos 30 días",
                "Calendario de salidas a bolsa · vía Finnhub")

try:
    from data.finnhub_provider import (
        is_available as _fh_ok2, fetch_ipo_calendar,
    )
    if not _fh_ok2():
        st.info("🔑 Configurá FINNHUB_API_KEY para ver IPOs.",
                icon="ℹ️")
    else:
        @st.cache_data(ttl=3600, show_spinner="Cargando IPOs…")
        def _load_ipos(_cache_key: str) -> pd.DataFrame:
            return fetch_ipo_calendar()

        idf = _load_ipos(TODAY.isoformat())
        if idf.empty:
            st.caption("Sin IPOs anunciadas en la ventana.")
        else:
            cards: list[str] = []
            for _, row in idf.head(20).iterrows():
                d_ts = row.get("date")
                d_d = d_ts.date() if pd.notna(d_ts) else None
                days, lab = _days_to(d_d) if d_d else (10**9, "—")
                border, accent = _urgency_color(days)
                sym = str(row.get("symbol") or "—")
                name = str(row.get("name") or "")[:38]
                exch = str(row.get("exchange") or "")
                price = str(row.get("price") or "—")
                size = row.get("totalSharesValue")
                size_txt = (f"${size/1e9:.2f}B" if pd.notna(size) and size >= 1e9
                            else f"${size/1e6:.0f}M" if pd.notna(size) and size > 0
                            else "—")
                status = str(row.get("status") or "")
                cards.append(
                    f'<div style="background:#0f172a;border:1px solid #334155;'
                    f'border-left:3px solid {border};border-radius:6px;'
                    f'padding:10px 14px;">'
                    f'<div style="display:flex;justify-content:space-between;'
                    f'align-items:baseline;margin-bottom:4px;">'
                    f'<span style="font-size:14px;font-weight:700;'
                    f'color:#F3F4F6;letter-spacing:0.02em;">{sym}</span>'
                    f'<span style="font-size:11px;color:{accent};'
                    f'font-weight:600;">{lab}</span>'
                    f'</div>'
                    f'<div style="font-size:12px;color:#cbd5e1;'
                    f'white-space:nowrap;overflow:hidden;'
                    f'text-overflow:ellipsis;margin-bottom:6px;">{name}</div>'
                    f'<div style="font-size:11px;color:#94A3B8;">'
                    f'{_fmt_date(d_d)} · {exch} · {status}'
                    f'</div>'
                    f'<div style="font-size:11px;color:#94A3B8;margin-top:4px;">'
                    f'Precio: <b style="color:#cbd5e1;">{price}</b> · '
                    f'Tamaño: <b style="color:#cbd5e1;">{size_txt}</b>'
                    f'</div>'
                    f'</div>'
                )
            st.markdown(
                '<div style="display:grid;'
                'grid-template-columns:repeat(auto-fill,minmax(240px,1fr));'
                'gap:10px;">'
                + "".join(cards) + '</div>',
                unsafe_allow_html=True,
            )
            st.caption(f"Mostrando {min(20, len(idf))} de {len(idf)} IPOs.")
except Exception as e:
    st.warning(f"IPOs no disponibles: {type(e).__name__} — {e}",
               icon="⚠️")


# ============================================================
# Section 4 — Economic events grid
# ============================================================
st.markdown("<br>", unsafe_allow_html=True)
_section_header("📈", "Eventos macro · cadencia de releases",
                "Releases de alto impacto sobre el equity market")

# 2-col grid of macro events with description
_FREQ_COLORS = {
    "Semanal":    ("#10B981", "Sem"),
    "Mensual":    ("#3B82F6", "Mes"),
    "Trimestral": ("#C9A961", "Trim"),
}
econ_cards: list[str] = []
for label, cadence, when, descr in _ECON_PATTERN:
    color, short = _FREQ_COLORS.get(cadence, ("#94A3B8", cadence))
    econ_cards.append(
        f'<div style="background:#0f172a;border:1px solid #334155;'
        f'border-radius:6px;padding:12px 14px;">'
        f'<div style="display:flex;justify-content:space-between;'
        f'align-items:baseline;margin-bottom:4px;">'
        f'<span style="font-size:13px;font-weight:600;color:#F3F4F6;">'
        f'{label}</span>'
        f'<span style="display:inline-block;padding:1px 7px;'
        f'border-radius:3px;background:{color}22;color:{color};'
        f'font-size:9px;font-weight:700;letter-spacing:0.06em;">'
        f'{short.upper()}</span>'
        f'</div>'
        f'<div style="font-size:11px;color:#cbd5e1;margin-bottom:4px;">'
        f'⏱ {when}</div>'
        f'<div style="font-size:11px;color:#94A3B8;line-height:1.4;">'
        f'{descr}</div>'
        f'</div>'
    )
st.markdown(
    '<div style="display:grid;'
    'grid-template-columns:repeat(auto-fill,minmax(280px,1fr));'
    'gap:10px;">'
    + "".join(econ_cards) + '</div>',
    unsafe_allow_html=True,
)
st.caption(
    "Patrones de release típicos, no fechas exactas del mes. Para "
    "fechas precisas: BLS (bls.gov/schedule), BEA (bea.gov/news/"
    "schedule), Federal Reserve."
)


# ============================================================
# Footer
# ============================================================
st.markdown("---")
st.caption(
    "Earnings + IPOs cacheados 30-60 min (visible en API Usage). "
    "FOMC y patrones macro hardcodeados — actualizar al cambiar "
    "de año o cuando la Fed publica un schedule nuevo."
)

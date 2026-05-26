"""
Informe de research de acciones en PDF (reportlab).

Ensambla un informe estilo research institucional a partir de los
artefactos que la página de Equity Analysis ya computa — no corre
análisis nuevo, este módulo es puro layout.

API pública
-----------
``build_research_pdf(bundle, results, ...) -> bytes``
    Devuelve el PDF como bytes, listo para ``st.download_button``.

El informe está en español. Estructura:
  Portada · Resumen de Inversión · Descripción del Negocio ·
  Desempeño Financiero (+ charts) · Rentabilidad y Retornos (+ charts) ·
  Estructura de Capital (+ charts) · Valuación · Comparables.

Los charts Plotly se rasterizan a PNG vía kaleido y se embeben sobre
una tarjeta oscura (los charts están diseñados para fondo oscuro).
Toda sección es defensiva: data faltante o un chart que no rinde
degradan a "—" / se omiten, nunca se levanta excepción.
"""
from __future__ import annotations
import logging
from datetime import datetime, timezone
from io import BytesIO
from typing import Any, Optional

import pandas as pd

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable, Image, KeepTogether, PageBreak, Paragraph,
    SimpleDocTemplate, Spacer, Table, TableStyle,
)

log = logging.getLogger(__name__)


# ============================================================
# Paleta — fondo claro (apto impresión), acento dorado
# ============================================================
GOLD   = colors.HexColor("#9A7B33")
NAVY   = colors.HexColor("#0B0E14")
INK    = colors.HexColor("#1F2937")
MUTED  = colors.HexColor("#6B7280")
RULE   = colors.HexColor("#D8DBE0")
PANEL  = colors.HexColor("#F4F2EC")
HIGHLIGHT = colors.HexColor("#F1E7C7")   # tinte dorado — filas destacadas
GAINS  = colors.HexColor("#0F7A4F")
LOSSES = colors.HexColor("#B4232B")

# Fondo oscuro para las tarjetas de charts (los charts del app usan
# texto claro + paleta pensada para fondo oscuro).
CHART_BG = "#0B0E14"

# El rating engine emite veredictos en inglés — se traducen al mostrar.
_VERDICT_ES = {
    "STRONG BUY":  "COMPRA FUERTE",
    "BUY":         "COMPRA",
    "HOLD":        "MANTENER",
    "SELL":        "VENTA",
    "STRONG SELL": "VENTA FUERTE",
    "N/A":         "N/A",
}
_VERDICT_COLOR = {
    "STRONG BUY":  GAINS,
    "BUY":         GAINS,
    "HOLD":        GOLD,
    "SELL":        LOSSES,
    "STRONG SELL": LOSSES,
    "N/A":         GOLD,
}
_CONFIDENCE_ES = {"high": "Alta", "medium": "Media", "low": "Baja"}

# Apéndice de estados financieros — core.account_labels emite las
# etiquetas en inglés; se traducen al mostrar (clave = label inglés).
_ES_SECTIONS = {"ASSETS": "ACTIVOS", "LIABILITIES": "PASIVOS",
                "EQUITY": "PATRIMONIO"}
_ES_LABELS: dict[str, str] = {
    "Revenue": "Ingresos",
    "Cost of Revenue": "Costo de ventas",
    "Gross Profit": "Resultado bruto",
    "SG&A": "Gastos de venta y administrativos",
    "R&D": "Investigación y desarrollo",
    "Operating Expenses": "Gastos operativos",
    "Operating Income": "Resultado operativo",
    "EBIT": "EBIT", "EBITDA": "EBITDA",
    "Interest Expense": "Gastos por intereses",
    "Interest Income": "Ingresos por intereses",
    "Income Before Tax": "Resultado antes de impuestos",
    "Tax Expense": "Impuesto a las ganancias",
    "Net Income": "Resultado neto",
    "EPS": "BPA (beneficio por acción)",
    "EPS (Diluted)": "BPA diluido",
    "Weighted Avg Shares": "Acciones promedio ponderadas",
    "Weighted Avg Shares (Diluted)": "Acciones promedio (diluidas)",
    "D&A": "Depreciación y amortización",
    "Total Assets": "Activos totales",
    "Current Assets": "Activos corrientes",
    "Non-Current Assets": "Activos no corrientes",
    "Cash & Equivalents": "Efectivo y equivalentes",
    "Cash & Short-Term Investments": "Efectivo e inversiones de corto plazo",
    "Short-Term Investments": "Inversiones de corto plazo",
    "Receivables": "Cuentas por cobrar",
    "Inventory": "Inventario",
    "PP&E (net)": "Propiedad, planta y equipo (neto)",
    "Goodwill": "Llave de negocio (goodwill)",
    "Intangible Assets": "Activos intangibles",
    "Goodwill & Intangibles": "Goodwill e intangibles",
    "Long-Term Investments": "Inversiones de largo plazo",
    "Other Assets": "Otros activos",
    "Total Liabilities": "Pasivos totales",
    "Current Liabilities": "Pasivos corrientes",
    "Non-Current Liabilities": "Pasivos no corrientes",
    "Accounts Payable": "Cuentas por pagar",
    "Short-Term Debt": "Deuda de corto plazo",
    "Long-Term Debt": "Deuda de largo plazo",
    "Total Debt": "Deuda total",
    "Deferred Revenue": "Ingresos diferidos",
    "Other Liabilities": "Otros pasivos",
    "Stockholders Equity": "Patrimonio neto",
    "Total Equity": "Patrimonio total",
    "Retained Earnings": "Resultados acumulados",
    "Common Stock": "Capital social",
    "Shares Outstanding": "Acciones en circulación",
    "Operating Cash Flow": "Flujo de caja operativo",
    "CapEx": "Inversiones de capital (CapEx)",
    "Free Cash Flow": "Flujo de caja libre",
    "Stock-Based Comp": "Compensación en acciones",
    "Dividends Paid": "Dividendos pagados",
    "Buybacks": "Recompras de acciones",
    "Acquisitions": "Adquisiciones",
    "Net Investing CF": "Flujo de inversión neto",
    "Net Financing CF": "Flujo de financiación neto",
    "Δ Working Capital": "Δ Capital de trabajo",
    "Debt Repayment": "Repago de deuda",
    "Common Stock Issued": "Emisión de acciones",
}
# Claves cuyo valor NO es un monto en dólares.
_PER_SHARE_KEYS = {"eps", "epsdiluted"}
_SHARE_COUNT_KEYS = {"weightedAverageShsOut", "weightedAverageShsOutDil",
                     "commonStockSharesOutstanding"}

# ---- Ratios financieros: agrupación, traducción y unidades ----
# Columnas de calculate_ratios que NO son ratios (montos en dólares) —
# se excluyen de la tabla de ratios; viven en Desempeño Financiero.
_RATIO_EXCLUDE = {"Revenue", "Net Income", "EBITDA", "FCF",
                  "FCF Adjusted (SBC)"}
# Grupos en orden de display; cada columna no listada cae en "Otros".
_RATIO_GROUPS: list[tuple[str, list[str]]] = [
    ("Crecimiento y márgenes",
     ["Revenue Growth %", "Gross Margin %", "Operating Margin %",
      "EBITDA Margin %", "Net Margin %", "FCF Margin %", "FCF Adj Margin %"]),
    ("Rentabilidad del capital",
     ["ROE %", "ROA %", "ROIC %", "ROIC - WACC (pp)", "Cash Conversion",
      "Asset Turnover"]),
    ("Liquidez y cobertura",
     ["Current Ratio", "Quick Ratio", "Interest Coverage"]),
    ("Apalancamiento", ["Debt/Equity", "Debt/EBITDA", "Net Debt/EBITDA"]),
]
_RATIO_ES: dict[str, str] = {
    "Revenue Growth %": "Crecimiento de ingresos",
    "Gross Margin %": "Margen bruto",
    "Operating Margin %": "Margen operativo",
    "EBITDA Margin %": "Margen EBITDA",
    "Net Margin %": "Margen neto", "FCF Margin %": "Margen de FCF",
    "FCF Adj Margin %": "Margen de FCF ajustado",
    "ROE %": "ROE — retorno sobre patrimonio",
    "ROA %": "ROA — retorno sobre activos",
    "ROIC %": "ROIC — retorno sobre capital invertido",
    "ROIC - WACC (pp)": "Spread ROIC − WACC",
    "Cash Conversion": "Conversión de caja (FCF/Resultado neto)",
    "Asset Turnover": "Rotación de activos",
    "Current Ratio": "Liquidez corriente", "Quick Ratio": "Prueba ácida",
    "Interest Coverage": "Cobertura de intereses",
    "Debt/Equity": "Deuda / Patrimonio",
    "Debt/EBITDA": "Deuda / EBITDA",
    "Net Debt/EBITDA": "Deuda neta / EBITDA",
}


def _fmt_ratio(col: str, v: Any) -> str:
    """Formatea una celda de la tabla de ratios según la unidad que
    implica el nombre de la columna: porcentaje, puntos o múltiplo."""
    f = _num(v)
    if f is None:
        return "—"
    if "(pp)" in col:
        return f"{f:+,.1f} pp"
    if col.endswith("%"):
        return f"{f:,.1f}%"
    return f"{f:,.2f}×"


# ============================================================
# Estilos de párrafo
# ============================================================
def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    s: dict[str, ParagraphStyle] = {}
    s["title"] = ParagraphStyle(
        "title", parent=base["Normal"], fontName="Helvetica-Bold",
        fontSize=25, leading=29, textColor=NAVY)
    s["subtitle"] = ParagraphStyle(
        "subtitle", parent=base["Normal"], fontName="Helvetica",
        fontSize=11, leading=15, textColor=MUTED)
    s["eyebrow"] = ParagraphStyle(
        "eyebrow", parent=base["Normal"], fontName="Helvetica-Bold",
        fontSize=9, leading=12, textColor=GOLD, spaceAfter=2)
    s["h2"] = ParagraphStyle(
        "h2", parent=base["Normal"], fontName="Helvetica-Bold",
        fontSize=13, leading=17, textColor=NAVY, spaceBefore=14, spaceAfter=6)
    s["h3"] = ParagraphStyle(
        "h3", parent=base["Normal"], fontName="Helvetica-Bold",
        fontSize=9.5, leading=13, textColor=GOLD, spaceBefore=8, spaceAfter=4)
    s["body"] = ParagraphStyle(
        "body", parent=base["Normal"], fontName="Helvetica",
        fontSize=9.5, leading=14, textColor=INK, spaceAfter=6)
    s["small"] = ParagraphStyle(
        "small", parent=base["Normal"], fontName="Helvetica",
        fontSize=8, leading=11, textColor=MUTED)
    s["cell"] = ParagraphStyle(
        "cell", parent=base["Normal"], fontName="Helvetica",
        fontSize=8.5, leading=11, textColor=INK)
    s["cell_r"] = ParagraphStyle("cell_r", parent=s["cell"], alignment=TA_RIGHT)
    s["verdict"] = ParagraphStyle(
        "verdict", parent=base["Normal"], fontName="Helvetica-Bold",
        fontSize=19, leading=22, alignment=TA_CENTER, textColor=NAVY)
    return s


# ============================================================
# Formato de números
# ============================================================
def _num(v: Any) -> Optional[float]:
    try:
        if v is None:
            return None
        f = float(v)
        return f if pd.notna(f) else None
    except (TypeError, ValueError):
        return None


def _money(v: Any) -> str:
    f = _num(v)
    if f is None:
        return "—"
    a = abs(f)
    if a >= 1e12:
        return f"US${f / 1e12:,.2f} B"          # billón = 1e12
    if a >= 1e9:
        return f"US${f / 1e9:,.2f} MM"          # mil millones
    if a >= 1e6:
        return f"US${f / 1e6:,.1f} M"
    return f"US${f:,.0f}"


def _price(v: Any) -> str:
    f = _num(v)
    return f"US${f:,.2f}" if f is not None else "—"


def _pct(v: Any, *, scale: float = 1.0) -> str:
    f = _num(v)
    return f"{f * scale:,.1f}%" if f is not None else "—"


def _fmt_int(v: Any) -> str:
    f = _num(v)
    return f"{int(f):,}".replace(",", ".") if f is not None else "—"


def _model_intrinsic(model: Any) -> Optional[float]:
    """Valor intrínseco por acción de cualquier resultado de modelo."""
    if model is None:
        return None
    for attr in ("intrinsic_value_per_share", "intrinsic_per_share",
                 "value_per_share", "implied_per_share_median"):
        v = _num(getattr(model, attr, None))
        if v is not None:
            return v
    return None


# ============================================================
# Charts — Plotly → PNG (kaleido) → flowable Image
# ============================================================
def _render_fig(fig: Any, *, w_in: float = 6.7, h_in: float = 2.7) -> Optional[Image]:
    """Rasteriza una figura Plotly a un Image de reportlab sobre fondo
    oscuro. Devuelve None si la figura es vacía o kaleido falla."""
    if fig is None:
        return None
    try:
        fig.update_layout(paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG)
        # 1100 px a ~6.7" ≈ 164 DPI — nítido para impresión. ``scale=1``
        # (antes 2) recorta a la mitad el tiempo de kaleido y el peso del
        # PDF sin pérdida visible de calidad: el cuello de botella de
        # rendimiento del informe es el rasterizado de ~14 gráficos.
        px_w = 1100
        px_h = int(px_w * h_in / w_in)
        png = fig.to_image(format="png", width=px_w, height=px_h, scale=1)
        return Image(BytesIO(png), width=w_in * inch, height=h_in * inch)
    except Exception as e:                       # kaleido / chart failure
        log.debug("PDF chart render failed: %s", e)
        return None


def _chart_block(title: str, img: Optional[Image], S: dict,
                 *, caption: Optional[str] = None) -> list:
    """Sub-título + (caption opcional) + chart, mantenidos juntos en la
    misma página vía KeepTogether — evita que el subtítulo quede
    huérfano al pie mientras el gráfico salta a la página siguiente."""
    inner: list = [Paragraph(title, S["h3"])]
    if caption:
        inner.append(Paragraph(caption, S["body"]))
    if img is not None:
        inner.append(img)
    else:
        inner.append(Paragraph("Gráfico no disponible para este ticker.",
                                S["small"]))
    inner.append(Spacer(1, 10))
    return [KeepTogether(inner)]


# ============================================================
# Narrativa de evolución — texto factual computado de los datos
# ============================================================
def _trend_verb(delta: float, *, up: str, down: str, flat: str,
                eps: float = 0.5) -> str:
    if delta > eps:
        return up
    if delta < -eps:
        return down
    return flat


def _evol_financiero(income: Any, cash: Any) -> Optional[str]:
    """Párrafo en español sobre la evolución de ingresos, márgenes y FCF."""
    try:
        from analysis.ratios import _get, cagr, free_cash_flow
    except Exception:
        return None
    rev = _get(income, "revenue")
    if rev is None or rev.dropna().empty:
        return None
    # Mismo horizonte que la tabla de Desempeño Financiero (5 ejercicios).
    s = rev.dropna().tail(5)
    n = max(len(s) - 1, 0)
    parts: list[str] = []
    if n >= 1:
        g = _num(cagr(s))
        if g is not None:
            verb = "crecieron" if g > 0 else "se contrajeron"
            parts.append(
                f"Los ingresos {verb} a un CAGR de {g * 100:,.1f}% en {n} "
                f"años — de {_money(s.iloc[0])} a {_money(s.iloc[-1])}.")
    oi = _get(income, "operating_income")
    if oi is not None:
        m = (oi / rev.where(rev != 0) * 100.0).dropna().tail(5)
        if len(m) >= 2:
            d = float(m.iloc[-1] - m.iloc[0])
            t = _trend_verb(d, up="se expandió", down="se contrajo",
                            flat="se mantuvo estable")
            parts.append(
                f"El margen operativo {t} de {m.iloc[0]:,.1f}% a "
                f"{m.iloc[-1]:,.1f}%.")
    fcf = (free_cash_flow(cash)
           if cash is not None and not cash.empty else None)
    if fcf is not None and not fcf.dropna().empty:
        fs = fcf.dropna().tail(5)
        if len(fs) >= 2:
            fg = _num(cagr(fs))
            if fg is not None:
                parts.append(
                    f"El flujo de caja libre evolucionó a {fg * 100:,.1f}% "
                    f"anual, cerrando en {_money(fs.iloc[-1])}.")
    return " ".join(parts) or None


def _evol_rentabilidad(results: Any, income: Any, balance: Any) -> Optional[str]:
    """Párrafo sobre ROIC vs WACC y creación/destrucción de valor."""
    try:
        from analysis.koller_reorg import reorganize
    except Exception:
        reorganize = None
    wacc = _num(getattr(getattr(results, "wacc", None), "wacc", None))
    parts: list[str] = []
    roic = None
    if reorganize is not None:
        try:
            reorg = reorganize(income, balance,
                               getattr(results, "_cash", None))
            r = getattr(reorg, "roic", None)
            roic = _num(r.dropna().iloc[-1]) if r is not None and hasattr(r, "dropna") and not r.dropna().empty else _num(r)
        except Exception:
            roic = None
    if roic is not None and wacc is not None:
        spread = roic - wacc
        if spread > 0.005:
            parts.append(
                f"El ROIC ({roic * 100:,.1f}%) supera al WACC "
                f"({wacc * 100:,.1f}%) por {spread * 100:,.1f} puntos — la "
                f"empresa crea valor con cada peso reinvertido.")
        elif spread < -0.005:
            parts.append(
                f"El ROIC ({roic * 100:,.1f}%) está por debajo del WACC "
                f"({wacc * 100:,.1f}%) — la reinversión destruye valor.")
        else:
            parts.append(
                f"El ROIC ({roic * 100:,.1f}%) está en línea con el WACC "
                f"({wacc * 100:,.1f}%): la empresa apenas cubre su costo "
                f"de capital.")
    parts.append(
        "Los gráficos muestran la trayectoria de ROIC/ROCE/ROA y la "
        "descomposición DuPont del ROE (margen × rotación × apalancamiento).")
    return " ".join(parts) or None


def _evol_valuacion(results: Any) -> Optional[str]:
    """Párrafo sobre el rango de modelos y el potencial vs precio."""
    agg = getattr(results, "aggregator", None)
    if agg is None:
        return None
    iv = _num(getattr(agg, "intrinsic_per_share", None))
    price = _num(getattr(results, "current_price", None))
    lo = _num(getattr(agg, "range_p25", None))
    hi = _num(getattr(agg, "range_p75", None))
    n = getattr(agg, "n_models_used", None)
    parts: list[str] = []
    if iv is not None and lo is not None and hi is not None and n:
        parts.append(
            f"Los {n} modelos aplicables arrojan un rango intercuartil de "
            f"{_price(lo)} a {_price(hi)}, con un valor intrínseco "
            f"combinado de {_price(iv)} por acción.")
    if iv is not None and price is not None and price > 0:
        up = (iv - price) / price * 100.0
        if up > 0:
            parts.append(
                f"Frente al precio actual de {_price(price)}, el modelo "
                f"implica un potencial alcista de {up:,.1f}%.")
        else:
            parts.append(
                f"Frente al precio actual de {_price(price)}, la acción "
                f"cotiza {abs(up):,.1f}% por encima del valor estimado.")
    cv = _num(getattr(agg, "dispersion_cv", None))
    if cv is not None:
        disp = _trend_verb(cv - 0.30, up="alta", down="baja",
                           flat="moderada", eps=0.0)
        parts.append(
            f"La dispersión entre modelos es {disp} (CV {cv * 100:,.0f}%), "
            f"lo que define el nivel de confianza del rango.")
    return " ".join(parts) or None


# ============================================================
# Helpers de tabla
# ============================================================
def _kv_table(rows: list[tuple[str, str]], S: dict) -> Table:
    data = [[Paragraph(k, S["cell"]), Paragraph(str(v), S["cell_r"])]
            for k, v in rows]
    tbl = Table(data, colWidths=[3.3 * inch, 3.3 * inch])
    tbl.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, -2), 0.3, RULE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
    ]))
    return tbl


# ============================================================
# Secciones — cada una devuelve una lista de flowables
# ============================================================
def _cover(bundle: Any, results: Any, S: dict, *, as_of: datetime) -> list:
    info = getattr(bundle, "info", {}) or {}
    profile = getattr(bundle, "fmp_profile", None) or {}
    name = (info.get("longName") or info.get("shortName")
            or profile.get("companyName") or bundle.ticker)
    sector = getattr(bundle, "sector", None) or "—"
    industry = info.get("industry") or profile.get("industry") or "—"

    rating = getattr(results, "rating", None)
    verdict_raw = str(getattr(rating, "verdict", None) or "—").upper()
    verdict_es = _VERDICT_ES.get(verdict_raw, verdict_raw)
    upside = getattr(rating, "upside", None)
    conf_raw = str(getattr(rating, "confidence", None) or "").lower()
    confidence = _CONFIDENCE_ES.get(conf_raw, conf_raw.title() or "—")

    price = _num(getattr(results, "current_price", None))
    agg = getattr(results, "aggregator", None)
    intrinsic = _num(getattr(agg, "intrinsic_per_share", None))

    out: list = [Spacer(1, 0.55 * inch),
                 Paragraph("INFORME DE RESEARCH", S["eyebrow"]),
                 Paragraph(str(name), S["title"]),
                 Paragraph(f"{bundle.ticker} &nbsp;·&nbsp; {sector} "
                           f"&nbsp;·&nbsp; {industry}", S["subtitle"]),
                 Spacer(1, 0.28 * inch),
                 HRFlowable(width="100%", thickness=1.2, color=GOLD),
                 Spacer(1, 0.28 * inch)]

    vcolor = _VERDICT_COLOR.get(verdict_raw, NAVY)
    vstyle = ParagraphStyle("v", parent=S["verdict"], textColor=vcolor)
    upside_txt = (f"{upside * 100:+,.1f}%" if _num(upside) is not None else "—")

    rec_tbl = Table([
        [Paragraph("RECOMENDACIÓN", S["eyebrow"]),
         Paragraph("PRECIO ACTUAL", S["eyebrow"]),
         Paragraph("VALOR INTRÍNSECO", S["eyebrow"]),
         Paragraph("POTENCIAL", S["eyebrow"])],
        [Paragraph(verdict_es, vstyle),
         Paragraph(_price(price), S["verdict"]),
         Paragraph(_price(intrinsic), S["verdict"]),
         Paragraph(upside_txt, vstyle)],
    ], colWidths=[1.66 * inch] * 4)
    rec_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PANEL),
        ("BOX", (0, 0), (-1, -1), 0.5, RULE),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, RULE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
    ]))
    out.append(rec_tbl)
    out.append(Spacer(1, 0.16 * inch))
    out.append(Paragraph(
        f"Confianza: {confidence} &nbsp;·&nbsp; "
        f"Perfil de valuación: {getattr(results, 'profile', '—')} "
        f"&nbsp;·&nbsp; Fecha del informe: {as_of:%d/%m/%Y}", S["small"]))
    return out


def _collect_facts(bundle: Any, results: Any) -> dict:
    """Hechos financieros para el narrador AI — números YA computados;
    el modelo sólo los redacta, nunca los inventa."""
    facts: dict = {}
    info = getattr(bundle, "info", {}) or {}
    facts["empresa"] = info.get("longName") or getattr(bundle, "ticker", "")
    facts["ticker"] = getattr(bundle, "ticker", "")
    facts["sector"] = getattr(bundle, "sector", None) or "—"
    facts["perfil_ciclo_vida"] = getattr(results, "profile", "—")
    rating = getattr(results, "rating", None)
    if rating is not None:
        v = str(getattr(rating, "verdict", "") or "").upper()
        facts["veredicto"] = _VERDICT_ES.get(v, v)
        up = _num(getattr(rating, "upside", None))
        if up is not None:
            facts["potencial_pct"] = round(up * 100.0, 1)

    income = getattr(bundle, "income", None)
    balance = getattr(bundle, "balance", None)
    cash = getattr(bundle, "cash", None)
    try:
        from analysis.ratios import _get, _resolve_total_debt, cagr, free_cash_flow
        rev = _get(income, "revenue")
        if rev is not None and not rev.dropna().empty:
            s = rev.dropna().tail(5)
            facts["ingresos_primero"] = _money(s.iloc[0])
            facts["ingresos_ultimo"] = _money(s.iloc[-1])
            g = _num(cagr(s))
            if g is not None:
                facts["ingresos_cagr_5y_pct"] = round(g * 100.0, 1)
        oi = _get(income, "operating_income")
        if oi is not None and rev is not None:
            m = (oi / rev.where(rev != 0) * 100.0).dropna().tail(5)
            if len(m) >= 2:
                facts["margen_operativo_primero_pct"] = round(float(m.iloc[0]), 1)
                facts["margen_operativo_ultimo_pct"] = round(float(m.iloc[-1]), 1)
        fcf = (free_cash_flow(cash)
               if cash is not None and not cash.empty else None)
        if fcf is not None and not fcf.dropna().empty:
            fg = _num(cagr(fcf.dropna().tail(5)))
            if fg is not None:
                facts["fcf_cagr_5y_pct"] = round(fg * 100.0, 1)
        debt = _resolve_total_debt(balance)
        if debt is not None and not debt.dropna().empty:
            d = debt.dropna().tail(5)
            facts["deuda_total_primero"] = _money(d.iloc[0])
            facts["deuda_total_ultimo"] = _money(d.iloc[-1])
        if cash is not None and not cash.empty:
            uses: dict[str, float] = {}
            for label, k in (("recompras", "buybacks"),
                             ("dividendos", "dividends_paid"),
                             ("inversión de capital", "capex")):
                s2 = _get(cash, k)
                if s2 is not None and not s2.dropna().empty:
                    uses[label] = abs(float(s2.dropna().tail(5).sum()))
            if uses:
                facts["asignacion_capital_principal"] = max(uses, key=uses.get)
    except Exception as e:
        log.debug("collect_facts financials block failed: %s", e)

    w = _num(getattr(getattr(results, "wacc", None), "wacc", None))
    if w is not None:
        facts["wacc_pct"] = round(w * 100.0, 1)
    agg = getattr(results, "aggregator", None)
    if agg is not None:
        iv = _num(getattr(agg, "intrinsic_per_share", None))
        if iv is not None:
            facts["valor_intrinseco"] = _price(iv)
        facts["n_modelos"] = getattr(agg, "n_models_used", None)
        cv = _num(getattr(agg, "dispersion_cv", None))
        if cv is not None:
            facts["dispersion_pct"] = round(cv * 100.0, 0)
        lo = _num(getattr(agg, "range_p25", None))
        hi = _num(getattr(agg, "range_p75", None))
        if lo is not None:
            facts["rango_intrinseco_p25"] = _price(lo)
        if hi is not None:
            facts["rango_intrinseco_p75"] = _price(hi)
    price = _num(getattr(results, "current_price", None))
    if price is not None:
        facts["precio_actual"] = _price(price)

    # ---- Management / dirección ----
    try:
        officers = info.get("companyOfficers") or []
        if isinstance(officers, list) and officers:
            named = []
            for o in officers[:5]:
                if not isinstance(o, dict):
                    continue
                nm = o.get("name")
                title = o.get("title") or ""
                if nm:
                    named.append(f"{nm} ({title})" if title else str(nm))
            if named:
                facts["directivos"] = named
            # CEO explícito — primer officer cuyo título menciona CEO.
            for o in officers:
                if not isinstance(o, dict):
                    continue
                title = str(o.get("title", "")).lower()
                if ("ceo" in title or "chief executive" in title) \
                        and o.get("name"):
                    facts["ceo"] = o["name"]
                    if o.get("title"):
                        facts["ceo_titulo"] = o["title"]
                    break
    except Exception as e:
        log.debug("collect_facts management block failed: %s", e)

    # ---- Contexto de mercado ----
    for k_src, k_dst in (("country", "pais"), ("fullTimeEmployees", "empleados"),
                         ("industry", "industria")):
        v = info.get(k_src)
        if v:
            facts[k_dst] = v
    beta = _num(info.get("beta"))
    if beta is not None:
        facts["beta"] = round(beta, 2)
    lo52 = _num(info.get("fiftyTwoWeekLow"))
    hi52 = _num(info.get("fiftyTwoWeekHigh"))
    if lo52 is not None and hi52 is not None:
        facts["rango_52s"] = f"{_price(lo52)} – {_price(hi52)}"

    # ---- Evolución de ingresos año por año ----
    try:
        from analysis.ratios import _get as _g2
        from core.formatters import format_period
        rev2 = _g2(income, "revenue")
        if rev2 is not None and not rev2.dropna().empty:
            s = rev2.dropna().tail(6)
            facts["ingresos_por_anio"] = {
                str(format_period(p)): _money(v) for p, v in s.items()}
    except Exception as e:
        log.debug("collect_facts revenue series failed: %s", e)

    # ---- Apalancamiento y solvencia ----
    try:
        from analysis.ratios import (
            debt_to_equity, debt_to_ebitda, interest_coverage,
            net_debt_to_ebitda, current_ratio,
        )

        def _last(fn, *a):
            try:
                s = fn(*a)
                if s is not None and hasattr(s, "dropna") and not s.dropna().empty:
                    return _num(s.dropna().iloc[-1])
            except Exception:
                return None
            return None

        de = _last(debt_to_equity, balance)
        if de is not None:
            facts["deuda_patrimonio"] = round(de, 2)
        dne = _last(net_debt_to_ebitda, income, balance)
        if dne is not None:
            facts["deuda_neta_ebitda"] = round(dne, 2)
        icov = _last(interest_coverage, income)
        if icov is not None:
            facts["cobertura_intereses"] = round(icov, 1)
        cr = _last(current_ratio, balance)
        if cr is not None:
            facts["liquidez_corriente"] = round(cr, 2)
    except Exception as e:
        log.debug("collect_facts leverage block failed: %s", e)

    # ---- Evolución de ratios financieros (para la sección 'ratios') ----
    try:
        from analysis.ratios import calculate_ratios
        from core.formatters import format_period
        rdf = calculate_ratios(income, balance, cash, wacc=w)
        if rdf is not None and not rdf.empty:
            cols = [c for c in rdf.columns if c not in _RATIO_EXCLUDE]
            evol: dict[str, dict] = {}
            for c in cols:
                s = rdf[c].dropna().tail(5)
                if len(s) >= 2:
                    evol[c] = {str(format_period(p)): round(float(v), 2)
                               for p, v in s.items()}
            if evol:
                facts["ratios_evolucion"] = evol
    except Exception as e:
        log.debug("collect_facts ratios block failed: %s", e)

    # ---- Comparables / competidores ----
    try:
        peers = getattr(bundle, "peers", None) or []
        peer_tickers = [getattr(p, "ticker", None) for p in peers]
        peer_tickers = [t for t in peer_tickers if t]
        if peer_tickers:
            facts["comparables"] = peer_tickers[:10]
    except Exception as e:
        log.debug("collect_facts peers block failed: %s", e)

    return facts


def _resumen_inversion(bundle: Any, results: Any, S: dict, ai: dict) -> list:
    out: list = [Paragraph("Resumen de Inversión", S["h2"]),
                 HRFlowable(width="100%", thickness=0.5, color=RULE),
                 Spacer(1, 6)]
    rating = getattr(results, "rating", None)
    reasoning = ai.get("resumen") or getattr(rating, "reasoning", None)
    if reasoning:
        out.append(Paragraph(str(reasoning), S["body"]))

    agg = getattr(results, "aggregator", None)
    rows = [
        ("Capitalización de mercado", _money(getattr(bundle, "market_cap", None))),
        ("Valor intrínseco combinado / acción",
         _price(getattr(agg, "intrinsic_per_share", None))),
        ("Rango intrínseco (P25–P75)",
         f"{_price(getattr(agg, 'range_p25', None))} – "
         f"{_price(getattr(agg, 'range_p75', None))}"),
        ("Modelos utilizados", str(getattr(agg, "n_models_used", "—"))),
        ("Dispersión (coef. de variación)",
         _pct(getattr(agg, "dispersion_cv", None), scale=100.0)),
        ("WACC", _pct(getattr(getattr(results, "wacc", None), "wacc", None),
                      scale=100.0)),
    ]
    out.append(Spacer(1, 6))
    out.append(_kv_table(rows, S))
    return out


def _descripcion_negocio(bundle: Any, results: Any, S: dict) -> list:
    info = getattr(bundle, "info", {}) or {}
    profile = getattr(bundle, "fmp_profile", None) or {}
    desc = (info.get("longBusinessSummary") or profile.get("description") or "")

    out: list = [Paragraph("Descripción del Negocio", S["h2"]),
                 HRFlowable(width="100%", thickness=0.5, color=RULE),
                 Spacer(1, 6)]
    if desc:
        txt = str(desc)
        if len(txt) > 1100:
            txt = txt[:1100].rsplit(" ", 1)[0] + " …"
        out.append(Paragraph(txt, S["body"]))

    rows = [
        ("Sector", getattr(bundle, "sector", None) or "—"),
        ("Industria", info.get("industry") or profile.get("industry") or "—"),
        ("País", info.get("country") or profile.get("country") or "—"),
        ("Empleados", _fmt_int(info.get("fullTimeEmployees")
                               or profile.get("fullTimeEmployees"))),
        ("Bolsa", info.get("exchange")
         or profile.get("exchangeShortName") or "—"),
        ("Perfil de ciclo de vida", getattr(results, "profile", "—")),
    ]
    out.append(Spacer(1, 6))
    out.append(_kv_table(rows, S))
    return out


def _negocio_y_gestion(bundle: Any, results: Any, S: dict, ai: dict) -> list:
    """Evolución del modelo de negocio, panorama hacia adelante y equipo
    directivo. La prosa la aporta el narrador AI; sin él, cae a una
    descripción factual de la trayectoria de ingresos."""
    out: list = [Paragraph("Evolución del Negocio y Gestión", S["h2"]),
                 HRFlowable(width="100%", thickness=0.5, color=RULE),
                 Spacer(1, 8)]
    income = getattr(bundle, "income", None)
    cash = getattr(bundle, "cash", None)
    info = getattr(bundle, "info", {}) or {}

    # ---- Evolución del negocio y panorama ----
    out.append(Paragraph("Trayectoria del negocio y panorama", S["h3"]))
    negocio = ai.get("negocio") or _evol_financiero(income, cash)
    if negocio:
        out.append(Paragraph(str(negocio), S["body"]))
    else:
        out.append(Paragraph(
            "Sin datos suficientes para describir la evolución del "
            "negocio.", S["small"]))

    # Mini-tabla con la evolución de ingresos año por año.
    try:
        from analysis.ratios import _get
        from core.formatters import format_period
        rev = _get(income, "revenue")
        if rev is not None and not rev.dropna().empty:
            s = rev.dropna().tail(6)
            yrs = [str(format_period(p)) for p in s.index]
            row_lbl = [Paragraph("<b>Ejercicio</b>", S["cell"])] + [
                Paragraph(f"<b>{y}</b>", S["cell_r"]) for y in yrs]
            row_val = [Paragraph("Ingresos", S["cell"])] + [
                Paragraph(_money(v), S["cell_r"]) for v in s]
            colw = (6.7 * inch - 1.4 * inch) / max(len(yrs), 1)
            rt = Table([row_lbl, row_val],
                       colWidths=[1.4 * inch] + [colw] * len(yrs))
            rt.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), PANEL),
                ("LINEBELOW", (0, 0), (-1, 0), 0.6, GOLD),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ]))
            out.append(Spacer(1, 6))
            out.append(rt)
    except Exception as e:
        log.debug("revenue mini-table skipped: %s", e)

    # ---- Equipo directivo ----
    out.append(Spacer(1, 10))
    out.append(Paragraph("Equipo directivo y asignación de capital",
                         S["h3"]))
    mgmt = ai.get("management")
    if mgmt:
        out.append(Paragraph(str(mgmt), S["body"]))

    officers = info.get("companyOfficers") or []
    rows: list[tuple[str, str]] = []
    if isinstance(officers, list):
        for o in officers[:6]:
            if not isinstance(o, dict):
                continue
            nm = o.get("name")
            title = o.get("title") or "—"
            if nm:
                rows.append((str(title), str(nm)))
    if rows:
        out.append(Spacer(1, 4))
        out.append(_kv_table(rows, S))
    elif not mgmt:
        out.append(Paragraph(
            "Sin información de directivos disponible para este ticker.",
            S["small"]))
    return out


def _desempeno_financiero(bundle: Any, S: dict, ai: dict) -> list:
    out: list = [Paragraph("Desempeño Financiero", S["h2"]),
                 HRFlowable(width="100%", thickness=0.5, color=RULE),
                 Spacer(1, 6)]
    income = getattr(bundle, "income", None)
    balance = getattr(bundle, "balance", None)
    cash = getattr(bundle, "cash", None)
    if income is None or income.empty:
        out.append(Paragraph("Sin estados financieros disponibles.",
                              S["small"]))
        return out

    try:
        from analysis.ratios import _get, free_cash_flow
        from core.formatters import format_period
    except Exception:
        out.append(Paragraph("Helpers financieros no disponibles.",
                              S["small"]))
        return out

    periods = list(income.index)[-5:]
    labels = [format_period(p) for p in periods]

    def _cell_row(label, series, *, fmt):
        cells = [Paragraph(label, S["cell"])]
        for p in periods:
            v = (series.loc[p] if series is not None and p in series.index
                 else None)
            cells.append(Paragraph(fmt(v), S["cell_r"]))
        return cells

    rev = _get(income, "revenue")
    gp = _get(income, "gross_profit")
    oi = _get(income, "operating_income")
    ni = _get(income, "net_income")
    fcf = free_cash_flow(cash) if cash is not None and not cash.empty else None

    def _margin(numer):
        if numer is None or rev is None:
            return None
        try:
            return numer / rev.where(rev != 0) * 100.0
        except Exception:
            return None

    header = [Paragraph("Concepto", S["cell"])] + [
        Paragraph(f"<b>{l}</b>", S["cell_r"]) for l in labels]
    data = [
        header,
        _cell_row("Ingresos", rev, fmt=_money),
        _cell_row("Resultado bruto", gp, fmt=_money),
        _cell_row("Resultado operativo", oi, fmt=_money),
        _cell_row("Resultado neto", ni, fmt=_money),
        _cell_row("Flujo de caja libre", fcf, fmt=_money),
        _cell_row("Margen operativo", _margin(oi), fmt=lambda v: _pct(v)),
        _cell_row("Margen neto", _margin(ni), fmt=lambda v: _pct(v)),
    ]
    col0 = 1.7 * inch
    colw = (6.7 * inch - col0) / max(len(periods), 1)
    tbl = Table(data, colWidths=[col0] + [colw] * len(periods))
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PANEL),
        ("LINEBELOW", (0, 0), (-1, 0), 0.6, GOLD),
        ("LINEBELOW", (0, 1), (-1, -3), 0.3, RULE),
        ("LINEABOVE", (0, -2), (-1, -2), 0.4, RULE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    out.append(tbl)
    out.append(Spacer(1, 10))

    narr = ai.get("financiero") or _evol_financiero(income, cash)
    if narr:
        out.append(Paragraph(narr, S["body"]))
    out.append(Spacer(1, 8))

    # ---- Charts ----
    try:
        from ui.charts.revenue_history import build_revenue_figure
        out += _chart_block(
            "Ingresos · Resultado neto · Flujo de caja libre",
            _render_fig(build_revenue_figure(income, cash=cash, height=360)),
            S)
    except Exception as e:
        log.debug("revenue chart skipped: %s", e)
    try:
        from ui.charts.margins_evolution import build_margins_figure
        out += _chart_block(
            "Evolución de márgenes",
            _render_fig(build_margins_figure(
                income, balance, cash, height=360,
                peers=getattr(bundle, "peers", None))),
            S)
    except Exception as e:
        log.debug("margins chart skipped: %s", e)
    return out


def _rentabilidad(bundle: Any, results: Any, S: dict, ai: dict) -> list:
    out: list = [Paragraph("Rentabilidad y Retornos", S["h2"]),
                 HRFlowable(width="100%", thickness=0.5, color=RULE),
                 Spacer(1, 8)]
    income = getattr(bundle, "income", None)
    balance = getattr(bundle, "balance", None)
    cash = getattr(bundle, "cash", None)
    if income is None or income.empty:
        out.append(Paragraph("Sin estados financieros disponibles.",
                              S["small"]))
        return out

    narr = ai.get("rentabilidad") or _evol_rentabilidad(results, income, balance)
    if narr:
        out.append(Paragraph(narr, S["body"]))
        out.append(Spacer(1, 8))

    wacc = getattr(getattr(results, "wacc", None), "wacc", None)
    try:
        from ui.charts.profitability_evolution import build_profitability_evolution
        out += _chart_block(
            "Evolución de rentabilidad · ROIC / ROCE / ROA (vs WACC)",
            _render_fig(build_profitability_evolution(
                income, balance, cash, height=380, wacc=wacc)),
            S)
    except Exception as e:
        log.debug("profitability chart skipped: %s", e)
    try:
        from ui.charts.dupont_decomposition import build_dupont
        out += _chart_block(
            "Descomposición DuPont · ROE = margen × rotación × apalancamiento",
            _render_fig(build_dupont(income, balance, height=380)),
            S)
    except Exception as e:
        log.debug("dupont chart skipped: %s", e)
    return out


def _evol_capital(income: Any, balance: Any, cash: Any) -> Optional[str]:
    """Párrafo sobre la evolución de deuda y la asignación de capital."""
    try:
        from analysis.ratios import _get, _resolve_total_debt
    except Exception:
        return None
    parts: list[str] = []
    try:
        debt = _resolve_total_debt(balance)
        if debt is not None and not debt.dropna().empty:
            d = debt.dropna().tail(5)
            if len(d) >= 2:
                t = _trend_verb(float(d.iloc[-1] - d.iloc[0]),
                                up="creció", down="se redujo",
                                flat="se mantuvo estable", eps=1.0)
                parts.append(
                    f"La deuda total {t} de {_money(d.iloc[0])} a "
                    f"{_money(d.iloc[-1])} en el período.")
    except Exception:
        pass
    if cash is not None and not getattr(cash, "empty", True):
        buyb = _get(cash, "buybacks")
        divs = _get(cash, "dividends_paid")
        capex = _get(cash, "capex")
        tot = {}
        for name, s in (("recompras", buyb), ("dividendos", divs),
                        ("inversión de capital", capex)):
            if s is not None and not s.dropna().empty:
                tot[name] = abs(float(s.dropna().tail(5).sum()))
        if tot:
            top = max(tot, key=tot.get)
            parts.append(
                f"En los últimos ejercicios la asignación de capital se "
                f"orientó principalmente a {top}.")
    return " ".join(parts) or None


def _estructura_capital(bundle: Any, S: dict, ai: dict) -> list:
    out: list = [Paragraph("Estructura de Capital", S["h2"]),
                 HRFlowable(width="100%", thickness=0.5, color=RULE),
                 Spacer(1, 8)]
    income = getattr(bundle, "income", None)
    balance = getattr(bundle, "balance", None)
    cash = getattr(bundle, "cash", None)
    if income is None or income.empty:
        out.append(Paragraph("Sin estados financieros disponibles.",
                              S["small"]))
        return out

    narr = ai.get("capital") or _evol_capital(income, balance, cash)
    if narr:
        out.append(Paragraph(narr, S["body"]))
        out.append(Spacer(1, 8))

    # ---- Tabla de apalancamiento y solvencia ----
    try:
        from analysis.ratios import (
            _get, _resolve_total_debt, current_ratio, debt_to_ebitda,
            debt_to_equity, interest_coverage, net_debt_to_ebitda,
            quick_ratio,
        )
        from core.formatters import format_period

        periods = list(balance.index)[-5:] if balance is not None else []
        if periods:
            labels = [format_period(p) for p in periods]

            def _x(v):
                f = _num(v)
                return f"{f:,.2f}×" if f is not None else "—"

            def _row(label, series, fmt):
                cells = [Paragraph(label, S["cell"])]
                for p in periods:
                    v = (series.loc[p]
                         if series is not None and hasattr(series, "index")
                         and p in series.index else None)
                    cells.append(Paragraph(fmt(v), S["cell_r"]))
                return cells

            debt = _resolve_total_debt(balance)
            cash_eq = _get(balance, "cash_eq")
            net_debt = None
            if debt is not None:
                net_debt = (debt - cash_eq) if cash_eq is not None else debt

            header = [Paragraph("Métrica", S["cell"])] + [
                Paragraph(f"<b>{l}</b>", S["cell_r"]) for l in labels]
            data = [
                header,
                _row("Deuda total", debt, _money),
                _row("Deuda neta", net_debt, _money),
                _row("Deuda / Patrimonio", debt_to_equity(balance), _x),
                _row("Deuda / EBITDA", debt_to_ebitda(income, balance), _x),
                _row("Deuda neta / EBITDA",
                     net_debt_to_ebitda(income, balance), _x),
                _row("Cobertura de intereses", interest_coverage(income), _x),
                _row("Liquidez corriente", current_ratio(balance), _x),
                _row("Prueba ácida", quick_ratio(balance), _x),
            ]
            col0 = 1.9 * inch
            colw = (6.7 * inch - col0) / max(len(periods), 1)
            lt = Table(data, colWidths=[col0] + [colw] * len(periods))
            lt.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), PANEL),
                ("LINEBELOW", (0, 0), (-1, 0), 0.6, GOLD),
                ("LINEBELOW", (0, 1), (-1, 2), 0.3, RULE),
                ("LINEABOVE", (0, 3), (-1, 3), 0.4, RULE),
                ("LINEBELOW", (0, 3), (-1, -2), 0.3, RULE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ]))
            out.append(lt)
            out.append(Spacer(1, 4))
            out.append(Paragraph(
                "Deuda neta = deuda total − efectivo e inversiones "
                "líquidas. Deuda neta/EBITDA &gt; 3× y cobertura de "
                "intereses &lt; 3× señalan un perfil de apalancamiento "
                "exigente; la prueba ácida excluye inventarios de la "
                "liquidez de corto plazo.", S["small"]))
            out.append(Spacer(1, 10))
    except Exception as e:
        log.debug("leverage table skipped: %s", e)

    try:
        from ui.charts.debt_evolution import build_debt_evolution
        out += _chart_block(
            "Evolución de la deuda financiera",
            _render_fig(build_debt_evolution(income, balance, cash, height=360)),
            S)
    except Exception as e:
        log.debug("debt chart skipped: %s", e)
    try:
        from ui.charts.capital_allocation_stacked import build_capital_allocation_chart
        out += _chart_block(
            "Asignación de capital",
            _render_fig(build_capital_allocation_chart(
                income, balance, cash, height=360)),
            S)
    except Exception as e:
        log.debug("capital allocation chart skipped: %s", e)
    return out


def _valuacion(results: Any, S: dict, ai: dict) -> list:
    out: list = [Paragraph("Valuación", S["h2"]),
                 HRFlowable(width="100%", thickness=0.5, color=RULE),
                 Spacer(1, 6)]
    agg = getattr(results, "aggregator", None)
    weights = getattr(agg, "weights_used", {}) or {}

    narr = ai.get("valuacion") or _evol_valuacion(results)
    if narr:
        out.append(Paragraph(narr, S["body"]))
        out.append(Spacer(1, 8))

    models = [
        ("Flujo de Caja Descontado (DCF)", getattr(results, "dcf", None), "dcf"),
        ("Earnings Power Value (EPV)", getattr(results, "epv", None), "epv"),
        ("Múltiplos intrínsecos", getattr(results, "multiples", None),
         "multiples"),
        ("Descuento de dividendos (DDM)", getattr(results, "ddm", None), "ddm"),
        ("Ingreso residual", getattr(results, "residual_income", None), "ri"),
    ]
    data = [[Paragraph("<b>Modelo</b>", S["cell"]),
             Paragraph("<b>Intrínseco / acción</b>", S["cell_r"]),
             Paragraph("<b>Ponderación</b>", S["cell_r"])]]
    for label, model, key in models:
        iv = _model_intrinsic(model)
        w = _num(weights.get(key))
        data.append([
            Paragraph(label, S["cell"]),
            Paragraph(_price(iv), S["cell_r"]),
            Paragraph(_pct(w, scale=100.0) if w is not None else "—",
                      S["cell_r"]),
        ])
    data.append([
        Paragraph("<b>Valor intrínseco combinado</b>", S["cell"]),
        Paragraph(f"<b>{_price(getattr(agg, 'intrinsic_per_share', None))}</b>",
                  S["cell_r"]),
        Paragraph("<b>100%</b>", S["cell_r"]),
    ])
    tbl = Table(data, colWidths=[3.0 * inch, 1.85 * inch, 1.85 * inch])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PANEL),
        ("LINEBELOW", (0, 0), (-1, 0), 0.6, GOLD),
        ("LINEBELOW", (0, 1), (-1, -2), 0.3, RULE),
        ("LINEABOVE", (0, -1), (-1, -1), 0.8, NAVY),
        ("BACKGROUND", (0, -1), (-1, -1), PANEL),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    out.append(tbl)

    clipped = getattr(agg, "clipped_models", None) or []
    if clipped:
        out.append(Spacer(1, 6))
        out.append(Paragraph(
            f"Modelos recortados como outliers y sub-ponderados: "
            f"{', '.join(clipped)}.", S["small"]))
    return out


def _comparables(bundle: Any, S: dict) -> list:
    out: list = [Paragraph("Comparables", S["h2"]),
                 HRFlowable(width="100%", thickness=0.5, color=RULE),
                 Spacer(1, 6)]
    peers = getattr(bundle, "peers", None) or []
    if not peers:
        out.append(Paragraph(
            "No se resolvió un grupo de comparables para este ticker.",
            S["small"]))
        return out

    headers = ["Ticker", "Cap. de mercado", "Ingresos", "EBITDA",
               "Resultado neto"]
    data = [[Paragraph(f"<b>{h}</b>", S["cell"] if i == 0 else S["cell_r"])
             for i, h in enumerate(headers)]]
    for p in peers[:8]:
        data.append([
            Paragraph(str(getattr(p, "ticker", "—")), S["cell"]),
            Paragraph(_money(getattr(p, "market_cap", None)), S["cell_r"]),
            Paragraph(_money(getattr(p, "revenue", None)), S["cell_r"]),
            Paragraph(_money(getattr(p, "ebitda", None)), S["cell_r"]),
            Paragraph(_money(getattr(p, "net_income", None)), S["cell_r"]),
        ])
    tbl = Table(data, colWidths=[1.0 * inch] + [1.42 * inch] * 4)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PANEL),
        ("LINEBELOW", (0, 0), (-1, 0), 0.6, GOLD),
        ("LINEBELOW", (0, 1), (-1, -1), 0.3, RULE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    out.append(tbl)
    return out


def _statement_table(df: Any, order: list, S: dict, *, title: str) -> list:
    """Una tabla de estado financiero completo (todas las líneas del
    ``order`` canónico), con filas de sección y subtotales destacados."""
    out: list = [Paragraph(title, S["h3"])]
    if df is None or getattr(df, "empty", True):
        out.append(Paragraph("Sin datos disponibles.", S["small"]))
        out.append(Spacer(1, 8))
        return out

    from core.account_labels import SECTION_LABELS, get_label
    from core.formatters import format_period

    df = df.sort_index()
    periods = list(df.index)[-5:]
    labels = [format_period(p) for p in periods]

    def _fmt(key, v):
        if key in _SHARE_COUNT_KEYS:
            f = _num(v)
            return _fmt_int(f) if f is not None else "—"
        if key in _PER_SHARE_KEYS:
            return _price(v)
        return _money(v)

    header = [Paragraph("Concepto", S["cell"])] + [
        Paragraph(f"<b>{l}</b>", S["cell_r"]) for l in labels]
    data: list = [header]
    section_idx: list[int] = []
    subtotal_idx: list[int] = []

    for key, kind in order:
        if kind == "section":
            sec_en = SECTION_LABELS.get(key, key)
            sec = _ES_SECTIONS.get(sec_en, sec_en)
            section_idx.append(len(data))
            data.append([Paragraph(f"<b>{sec}</b>", S["cell"])]
                        + [Paragraph("", S["cell"]) for _ in periods])
            continue
        if key not in df.columns:
            continue
        eng = get_label(key)
        es = _ES_LABELS.get(eng, eng)
        is_sub = (kind == "subtotal")
        cells = [Paragraph(f"<b>{es}</b>" if is_sub else es, S["cell"])]
        for p in periods:
            v = df.loc[p, key] if p in df.index else None
            cells.append(Paragraph(_fmt(key, v), S["cell_r"]))
        if is_sub:
            subtotal_idx.append(len(data))
        data.append(cells)

    col0 = 2.3 * inch
    colw = (6.7 * inch - col0) / max(len(periods), 1)
    tbl = Table(data, colWidths=[col0] + [colw] * len(periods))
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), PANEL),
        ("LINEBELOW", (0, 0), (-1, 0), 0.6, GOLD),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]
    for i in section_idx:
        style.append(("BACKGROUND", (0, i), (-1, i), PANEL))
        style.append(("SPAN", (0, i), (-1, i)))
    for i in subtotal_idx:
        style.append(("LINEABOVE", (0, i), (-1, i), 0.4, RULE))
    tbl.setStyle(TableStyle(style))
    out.append(tbl)
    out.append(Spacer(1, 12))
    return out


def _apendice(bundle: Any, S: dict) -> list:
    out: list = [Paragraph("Apéndice · Estados Financieros", S["h2"]),
                 HRFlowable(width="100%", thickness=0.5, color=RULE),
                 Spacer(1, 4),
                 Paragraph("Estados completos según reportados (últimos "
                           "ejercicios disponibles).", S["small"]),
                 Spacer(1, 8)]
    try:
        from core.account_labels import (
            BALANCE_SHEET_ORDER, CASH_FLOW_ORDER, INCOME_STATEMENT_ORDER,
        )
    except Exception:
        out.append(Paragraph("Taxonomía de estados no disponible.",
                              S["small"]))
        return out

    out += _statement_table(getattr(bundle, "income", None),
                            INCOME_STATEMENT_ORDER, S,
                            title="Estado de Resultados")
    out += _statement_table(getattr(bundle, "balance", None),
                            BALANCE_SHEET_ORDER, S,
                            title="Estado de Situación Patrimonial")
    out += _statement_table(getattr(bundle, "cash", None),
                            CASH_FLOW_ORDER, S,
                            title="Estado de Flujo de Efectivo")
    return out


def _notable_ratios(df: Any) -> list[tuple[str, float, float, float]]:
    """Ratios cuya evolución primer→último ejercicio fue más pronunciada.
    Devuelve ``(columna, primero, último, cambio_relativo)`` — top 5 con
    |Δ| ≥ 12%, garantizando al menos 3 si hay datos."""
    movers: list[tuple[str, float, float, float]] = []
    for c in getattr(df, "columns", []):
        if c in _RATIO_EXCLUDE:
            continue
        s = df[c].dropna()
        if len(s) < 2:
            continue
        first, last = float(s.iloc[0]), float(s.iloc[-1])
        if abs(first) < 1e-9:
            continue
        movers.append((c, first, last, (last - first) / abs(first)))
    movers.sort(key=lambda r: abs(r[3]), reverse=True)
    strong = [m for m in movers if abs(m[3]) >= 0.12][:5]
    return strong if len(strong) >= 3 else movers[:3]


def _evol_ratios(notable: list[tuple[str, float, float, float]]) -> str:
    """Narrativa rule-based de respaldo — qué ratios se movieron y cuánto
    (sin causalidad; eso lo aporta el narrador AI)."""
    if not notable:
        return ""
    frases = []
    for c, first, last, rel in notable:
        lbl = _RATIO_ES.get(c, c)
        verbo = "se expandió" if rel > 0 else "se contrajo"
        frases.append(f"{lbl} {verbo} de {_fmt_ratio(c, first)} a "
                       f"{_fmt_ratio(c, last)} ({rel * 100:+,.0f}%)")
    return ("Los movimientos más pronunciados del período: "
            + "; ".join(frases) + ".")


def _ratios_completos(bundle: Any, results: Any, S: dict, ai: dict) -> list:
    """Sección de ratios financieros — en hoja propia. Sólo ratios (sin
    ingresos/EBITDA); destaca los 3-5 de evolución más llamativa con su
    explicación causal, y lista la grilla completa agrupada."""
    out: list = [PageBreak(),
                 Paragraph("Ratios Financieros", S["h2"]),
                 HRFlowable(width="100%", thickness=0.5, color=RULE),
                 Spacer(1, 6)]
    income = getattr(bundle, "income", None)
    balance = getattr(bundle, "balance", None)
    cash = getattr(bundle, "cash", None)
    if income is None or getattr(income, "empty", True):
        out.append(Paragraph("Sin estados financieros disponibles.",
                              S["small"]))
        return out
    try:
        from analysis.ratios import calculate_ratios
        from core.formatters import format_period
        wacc = _num(getattr(getattr(results, "wacc", None), "wacc", None))
        df = calculate_ratios(income, balance, cash, wacc=wacc)
    except Exception as e:
        log.debug("calculate_ratios failed: %s", e)
        out.append(Paragraph("Ratios no disponibles.", S["small"]))
        return out
    if df is None or df.empty:
        out.append(Paragraph("Ratios no disponibles.", S["small"]))
        return out

    out.append(Paragraph(
        "Los ratios se agrupan por dimensión de análisis — crecimiento "
        "y márgenes, rentabilidad del capital, liquidez y apalancamiento. "
        "Las columnas son los últimos ejercicios; cada celda lleva su "
        "unidad (%, puntos o ×). El spread ROIC − WACC es el test "
        "directo de creación de valor: positivo, la empresa rinde por "
        "encima de su costo de capital.", S["body"]))
    out.append(Spacer(1, 8))

    # ---- Ratios destacados — evolución y causa ----
    notable = _notable_ratios(df)
    notable_cols = {c for c, *_ in notable}
    destacados: list = [
        Paragraph("Ratios destacados — evolución y causa", S["h3"])]
    narr = ai.get("ratios") or _evol_ratios(notable)
    if narr:
        destacados.append(Paragraph(str(narr), S["body"]))
    if notable:
        d_head = [Paragraph("<b>Ratio</b>", S["cell"]),
                  Paragraph("<b>Primer ej.</b>", S["cell_r"]),
                  Paragraph("<b>Último ej.</b>", S["cell_r"]),
                  Paragraph("<b>Variación</b>", S["cell_r"])]
        d_data = [d_head]
        for c, first, last, rel in notable:
            arrow = "▲" if rel > 0 else "▼"
            d_data.append([
                Paragraph(_RATIO_ES.get(c, c), S["cell"]),
                Paragraph(_fmt_ratio(c, first), S["cell_r"]),
                Paragraph(_fmt_ratio(c, last), S["cell_r"]),
                Paragraph(f"{arrow} {rel * 100:+,.0f}%", S["cell_r"]),
            ])
        dt = Table(d_data, colWidths=[2.6 * inch, 1.45 * inch,
                                      1.45 * inch, 1.2 * inch])
        dt.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PANEL),
            ("LINEBELOW", (0, 0), (-1, 0), 0.6, GOLD),
            ("LINEBELOW", (0, 1), (-1, -1), 0.3, RULE),
            ("BACKGROUND", (0, 1), (-1, -1), HIGHLIGHT),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        destacados.append(Spacer(1, 4))
        destacados.append(dt)
    out += [KeepTogether(destacados), Spacer(1, 12)]

    # ---- Grilla completa de ratios, agrupada ----
    out.append(Paragraph("Grilla completa de ratios", S["h3"]))
    periods = list(df.index)[-5:]
    labels = [format_period(p) for p in periods]
    header = [Paragraph("Ratio", S["cell"])] + [
        Paragraph(f"<b>{l}</b>", S["cell_r"]) for l in labels]
    data: list = [header]
    section_idx: list[int] = []
    highlight_idx: list[int] = []

    classified = {c for _, cols in _RATIO_GROUPS for c in cols}
    groups = list(_RATIO_GROUPS)
    extra = [c for c in df.columns
             if c not in classified and c not in _RATIO_EXCLUDE]
    if extra:
        groups.append(("Otros indicadores", extra))

    for gname, cols in groups:
        present = [c for c in cols
                   if c in df.columns and c not in _RATIO_EXCLUDE]
        if not present:
            continue
        section_idx.append(len(data))
        data.append([Paragraph(f"<b>{gname}</b>", S["cell"])]
                    + [Paragraph("", S["cell"]) for _ in periods])
        for ratio in present:
            label = _RATIO_ES.get(ratio, ratio)
            mark = " ●" if ratio in notable_cols else ""
            cells = [Paragraph(f"{label}{mark}", S["cell"])]
            for p in periods:
                v = df.loc[p, ratio] if p in df.index else None
                cells.append(Paragraph(_fmt_ratio(ratio, v), S["cell_r"]))
            if ratio in notable_cols:
                highlight_idx.append(len(data))
            data.append(cells)

    col0 = 2.5 * inch
    colw = (6.7 * inch - col0) / max(len(periods), 1)
    tbl = Table(data, colWidths=[col0] + [colw] * len(periods))
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), PANEL),
        ("LINEBELOW", (0, 0), (-1, 0), 0.6, GOLD),
        ("LINEBELOW", (0, 1), (-1, -1), 0.3, RULE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]
    for i in highlight_idx:
        style.append(("BACKGROUND", (0, i), (-1, i), HIGHLIGHT))
    for i in section_idx:
        style.append(("BACKGROUND", (0, i), (-1, i), PANEL))
        style.append(("SPAN", (0, i), (-1, i)))
        style.append(("TEXTCOLOR", (0, i), (-1, i), GOLD))
    tbl.setStyle(TableStyle(style))
    out.append(tbl)
    out.append(Spacer(1, 4))
    out.append(Paragraph(
        "● ratios destacados por su variación en el período.", S["small"]))
    return out


def _football_field(results: Any, S: dict) -> list:
    """Football field — rango de valor por modelo vs precio."""
    out: list = [Paragraph("Football Field · Rango de Valuación", S["h2"]),
                 HRFlowable(width="100%", thickness=0.5, color=RULE),
                 Spacer(1, 6),
                 Paragraph(
                     "Cada barra es el rango de valor de un modelo; la línea "
                     "vertical marca el precio de mercado. La dispersión "
                     "entre modelos ES la información — un rango ancho "
                     "señala incertidumbre estructural en la valuación.",
                     S["body"])]
    try:
        from ui.components.football_field import build_football_field_figure
        out += _chart_block(
            "Valor intrínseco por modelo vs precio de mercado",
            _render_fig(build_football_field_figure(results, height=320)),
            S)
    except Exception as e:
        log.debug("football field skipped: %s", e)
        out.append(Paragraph("Football field no disponible.", S["small"]))
    return out


def _sensibilidad(bundle: Any, results: Any, S: dict) -> list:
    """Heatmap de sensibilidad del valor intrínseco a WACC × g terminal."""
    out: list = [Paragraph("Análisis de Sensibilidad", S["h2"]),
                 HRFlowable(width="100%", thickness=0.5, color=RULE),
                 Spacer(1, 6),
                 Paragraph(
                     "El valor intrínseco del DCF es muy sensible a dos "
                     "supuestos: el costo de capital (WACC) y el crecimiento "
                     "terminal (g). La grilla muestra el valor por acción "
                     "para combinaciones alrededor del caso base.", S["body"])]
    income = getattr(bundle, "income", None)
    balance = getattr(bundle, "balance", None)
    cash = getattr(bundle, "cash", None)
    wacc = _num(getattr(getattr(results, "wacc", None), "wacc", None))
    if income is None or getattr(income, "empty", True) or wacc is None:
        out.append(Paragraph("Sensibilidad no disponible.", S["small"]))
        return out
    try:
        from valuation.dcf_three_stage import sensitivity_table
        from ui.charts.sensitivity_heatmap import build_sensitivity_heatmap
        from core.constants import DCF_DEFAULTS
        g0 = float(DCF_DEFAULTS["terminal_growth"])
        wacc_grid = [round(wacc + d, 4) for d in (-0.02, -0.01, 0, 0.01, 0.02)]
        g_grid = [round(g0 + d, 4) for d in (-0.01, -0.005, 0, 0.005, 0.01)]
        sens = sensitivity_table(income=income, balance=balance, cash=cash,
                                 wacc_grid=wacc_grid, g_grid=g_grid)
        out += _chart_block(
            "Valor intrínseco $/acción · WACC × crecimiento terminal",
            _render_fig(build_sensitivity_heatmap(
                sens, current_price=_num(getattr(results, "current_price", None)),
                current_wacc=wacc, current_g=g0, height=340)),
            S)
    except Exception as e:
        log.debug("sensitivity skipped: %s", e)
        out.append(Paragraph("Sensibilidad no disponible.", S["small"]))
    return out


def _analistas(bundle: Any, results: Any, S: dict) -> list:
    """Consenso de analistas (Finnhub) frente a la valuación propia."""
    out: list = [Paragraph("Opinión de Analistas", S["h2"]),
                 HRFlowable(width="100%", thickness=0.5, color=RULE),
                 Spacer(1, 6)]
    ticker = getattr(bundle, "ticker", "")
    target = {}
    recs = None
    try:
        from data.finnhub_provider import (
            is_available, fetch_price_target, fetch_recommendation_trends,
        )
        if is_available():
            target = fetch_price_target(ticker) or {}
            recs = fetch_recommendation_trends(ticker)
    except Exception as e:
        log.debug("analyst data fetch failed: %s", e)

    agg = getattr(results, "aggregator", None)
    own_iv = _num(getattr(agg, "intrinsic_per_share", None))
    rating = getattr(results, "rating", None)
    own_verdict = str(getattr(rating, "verdict", None) or "—").upper()
    own_verdict_es = _VERDICT_ES.get(own_verdict, own_verdict)

    wall_mean = _num(target.get("targetMean") or target.get("targetMedian"))
    rows = [
        ("Precio objetivo medio (Wall Street)", _price(wall_mean)),
        ("Rango analistas (bajo – alto)",
         f"{_price(_num(target.get('targetLow')))} – "
         f"{_price(_num(target.get('targetHigh')))}"),
        ("Valor intrínseco (este informe)", _price(own_iv)),
        ("Recomendación (este informe)", own_verdict_es),
    ]
    out.append(_kv_table(rows, S))

    # Narrativa de contraste
    parts: list[str] = []
    if wall_mean is not None and own_iv is not None:
        if own_iv < wall_mean * 0.9:
            parts.append(
                f"La valuación de este informe ({_price(own_iv)}) es más "
                f"conservadora que el objetivo medio de Wall Street "
                f"({_price(wall_mean)}).")
        elif own_iv > wall_mean * 1.1:
            parts.append(
                f"Este informe estima un valor ({_price(own_iv)}) por encima "
                f"del consenso de Wall Street ({_price(wall_mean)}).")
        else:
            parts.append(
                f"La valuación propia ({_price(own_iv)}) está en línea con "
                f"el consenso de Wall Street ({_price(wall_mean)}).")
    if recs is None or getattr(recs, "empty", True):
        parts.append(
            "El detalle de recomendaciones de analistas requiere una "
            "FINNHUB_API_KEY configurada; sin ella sólo se muestra la "
            "valuación propia.")
    out.append(Spacer(1, 6))
    if parts:
        out.append(Paragraph(" ".join(parts), S["body"]))
    return out


def _competitive(bundle: Any, results: Any, S: dict, ai: dict) -> list:
    """Panorama competitivo — narrativa + revenue share + market cap."""
    out: list = [Paragraph("Panorama Competitivo", S["h2"]),
                 HRFlowable(width="100%", thickness=0.5, color=RULE),
                 Spacer(1, 6)]
    narr = ai.get("competencia")
    if narr:
        out.append(Paragraph(str(narr), S["body"]))
        out.append(Spacer(1, 8))
    peers = getattr(bundle, "peers", None) or []
    ticker = getattr(bundle, "ticker", "")
    if not peers:
        out.append(Paragraph(
            "Sin grupo de comparables cuantitativo resuelto para este "
            "ticker; el análisis competitivo se apoya en la narrativa "
            "anterior.", S["small"]))
        return out

    # Revenue + market cap del target
    tgt_rev = None
    try:
        from analysis.ratios import _get
        rev = _get(getattr(bundle, "income", None), "revenue")
        if rev is not None and not rev.dropna().empty:
            tgt_rev = float(rev.dropna().iloc[-1])
    except Exception:
        tgt_rev = None
    tgt_mcap = _num(getattr(bundle, "market_cap", None))

    revenues: dict[str, float] = {}
    mcaps: dict[str, float] = {}
    if tgt_rev:
        revenues[ticker] = tgt_rev
    if tgt_mcap:
        mcaps[ticker] = tgt_mcap
    for p in peers:
        r, m = _num(getattr(p, "revenue", None)), _num(getattr(p, "market_cap", None))
        if r:
            revenues[getattr(p, "ticker", "?")] = r
        if m:
            mcaps[getattr(p, "ticker", "?")] = m

    try:
        from ui.components.competitive_landscape import (
            _build_revenue_share_donut, _build_market_cap_bar,
        )
        if len(revenues) >= 2:
            out += _chart_block(
                "Participación en ingresos del grupo",
                _render_fig(_build_revenue_share_donut(ticker, revenues),
                            w_in=5.0, h_in=2.6),
                S)
        if len(mcaps) >= 2:
            out += _chart_block(
                "Capitalización de mercado del grupo",
                _render_fig(_build_market_cap_bar(ticker, mcaps),
                            w_in=6.2, h_in=2.6),
                S)
    except Exception as e:
        log.debug("competitive landscape skipped: %s", e)
        out.append(Paragraph("Panorama competitivo no disponible.",
                              S["small"]))
    return out


def _footer(canvas, doc, *, ticker: str) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(MUTED)
    canvas.drawString(
        0.9 * inch, 0.55 * inch,
        f"{ticker} — Informe de Research  ·  Generado por Equity Research App"
        f"  ·  No constituye asesoramiento de inversión.")
    canvas.drawRightString(7.6 * inch, 0.55 * inch, f"Página {doc.page}")
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.5)
    canvas.line(0.9 * inch, 0.72 * inch, 7.6 * inch, 0.72 * inch)
    canvas.restoreState()


# ============================================================
# API pública
# ============================================================
def build_research_pdf(
    *,
    bundle: Any,
    results: Any,
    as_of: Optional[datetime] = None,
) -> bytes:
    """Construye el informe de research y devuelve los bytes del PDF.

    ``bundle``  — analysis.parallel_loader.HydratedBundle
    ``results`` — core.valuation_pipeline.ValuationResults
    Ambos se toman ya computados; esta función sólo hace layout.
    """
    as_of = as_of or datetime.now(timezone.utc)
    S = _styles()
    ticker = getattr(bundle, "ticker", "TICKER")

    # Estados financieros en orden cronológico — algunos proveedores
    # devuelven un ejercicio fuera de lugar (p. ej. el FY más viejo al
    # final), lo que dibuja los charts en zigzag. Ordenar el índice una
    # sola vez acá lo corrige para todas las secciones y gráficos.
    for _attr in ("income", "balance", "cash"):
        try:
            _df = getattr(bundle, _attr, None)
            if (_df is not None and hasattr(_df, "sort_index")
                    and not _df.empty):
                setattr(bundle, _attr, _df.sort_index())
        except Exception as e:
            log.debug("sort %s failed: %s", _attr, e)

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=letter,
        leftMargin=0.9 * inch, rightMargin=0.9 * inch,
        topMargin=0.8 * inch, bottomMargin=0.9 * inch,
        title=f"{ticker} — Informe de Research",
        author="Equity Research App",
    )

    # Narrador AI (Gemini) — UNA llamada, en paralelo con el resto.
    # Antes bloqueaba ~5-10s antes de empezar a armar el PDF; ahora se
    # dispara en un thread y mientras corre se construye la portada y
    # las secciones que NO usan AI (rentabilidad sin AI, sensibilidad,
    # football field, analistas, comparables, apéndice). Las secciones
    # AI-dependientes se construyen recién cuando el future resuelve.
    # ``ai`` es un dict que se mutará in-place tras el await — los
    # builders lo capturan por referencia, así no hace falta recompilar
    # las lambdas.
    ai: dict = {}
    from concurrent.futures import ThreadPoolExecutor
    _ai_pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="pdf-ai")
    try:
        from analysis.ai_narrative import generate_pdf_narrative
        _ai_future = _ai_pool.submit(
            generate_pdf_narrative, ticker, _collect_facts(bundle, results))
    except Exception as exc:                     # AI module unavailable
        log.debug("AI narrative not launchable: %s", exc)
        _ai_future = None

    # ---- Slots de secciones — orden FINAL en el PDF ----
    # (builder, keep_together, needs_ai). Los builders capturan el
    # dict ``ai``; los que no lo leen son seguros de ejecutar antes
    # de que Gemini termine.
    section_specs = [
        (lambda: _resumen_inversion(bundle, results, S, ai), True,  True),
        (lambda: _descripcion_negocio(bundle, results, S),  True,  False),
        (lambda: _negocio_y_gestion(bundle, results, S, ai), False, True),
        (lambda: _desempeno_financiero(bundle, S, ai),       False, True),
        (lambda: _rentabilidad(bundle, results, S, ai),      False, True),
        (lambda: _estructura_capital(bundle, S, ai),         False, True),
        (lambda: _ratios_completos(bundle, results, S, ai),  False, True),
        (lambda: _valuacion(results, S, ai),                 True,  True),
        (lambda: _football_field(results, S),                False, False),
        (lambda: _sensibilidad(bundle, results, S),          False, False),
        (lambda: _analistas(bundle, results, S),             True,  False),
        (lambda: _comparables(bundle, S),                    True,  False),
        (lambda: _competitive(bundle, results, S, ai),       False, True),
    ]

    def _build_slot(builder, keep):
        try:
            flowables = builder()
            return KeepTogether(flowables) if keep else flowables
        except Exception as exc:
            return Paragraph(
                f"<i>Section unavailable: {type(exc).__name__}</i>",
                S["small"])

    # Cover (no AI) — corre mientras Gemini está pensando.
    cover_flow: list = list(_cover(bundle, results, S, as_of=as_of))

    # Pre-renderizar las secciones AI-FREE (los charts pesados de éstas
    # rasterizan mientras Gemini sigue corriendo).
    slot_outputs: list = [None] * len(section_specs)
    for i, (builder, keep, needs_ai) in enumerate(section_specs):
        if not needs_ai:
            slot_outputs[i] = _build_slot(builder, keep)

    # Ahora sí — esperar a Gemini y poblar ``ai`` antes de las secciones
    # que lo leen. Tope generoso: si Gemini tarda más, las secciones
    # AI caen a su narrativa rule-based con ai={}.
    if _ai_future is not None:
        try:
            ai_payload = _ai_future.result(timeout=60) or {}
            ai.update(ai_payload)
        except Exception as exc:
            log.debug("AI narrative skipped: %s", exc)
            # Cancel the future so the worker can exit cleanly
            # instead of finishing the Gemini call into the void.
            _ai_future.cancel()
    # wait=True ensures the worker thread is joined before this
    # function returns. Previously wait=False leaked one thread per
    # PDF generation when Gemini overran the 60s timeout.
    _ai_pool.shutdown(wait=True)

    # Secciones AI-dependientes — con ``ai`` ya poblado.
    for i, (builder, keep, needs_ai) in enumerate(section_specs):
        if needs_ai and slot_outputs[i] is None:
            slot_outputs[i] = _build_slot(builder, keep)

    # Ensamblar el story en orden definitivo.
    story: list = list(cover_flow)
    story.append(PageBreak())
    for out in slot_outputs:
        story.append(out)
        story.append(Spacer(1, 10))

    # ---- Apéndice (estados completos) — arranca en página nueva ----
    try:
        story.append(PageBreak())
        story.append(_apendice(bundle, S))
    except Exception as exc:                      # nunca tumbar el informe
        story.append(Paragraph(
            f"<i>Apéndice no disponible: {type(exc).__name__}</i>",
            S["small"]))

    def _on_page(canvas, doc_):
        _footer(canvas, doc_, ticker=ticker)

    # `story` puede contener listas (secciones no-KeepTogether) — aplanar.
    flat: list = []
    for item in story:
        if isinstance(item, list):
            flat.extend(item)
        else:
            flat.append(item)

    doc.build(flat, onFirstPage=_on_page, onLaterPages=_on_page)
    return buf.getvalue()

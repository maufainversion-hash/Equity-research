"""
Academy — generación de lecciones educativas vía Gemini.

Catálogo curado de temas agrupados por categoría (empresas, valuación,
sectores, macro, mercado) + una función ``generate_lesson(topic)``
que pide a Gemini la masterclass siguiendo una estructura fija de 10
secciones.

Diseño:
- Una llamada Gemini por (tema, modelo) — cacheada 24h vía
  ``@st.cache_data``. Re-consultas dentro del día no queman cuota.
- Sin ``GOOGLE_API_KEY`` o ante un 429: devuelve un mensaje
  explicativo en lugar de la lección. La página lo renderiza tal cual.
- El prompt es deliberadamente largo y específico: cuanto más
  contexto, menos lección genérica. Si quieren editar el tono o la
  estructura, se toca ``_SYSTEM`` / ``_USER_TEMPLATE`` y listo.
"""
from __future__ import annotations
import logging
from typing import Optional

import streamlit as st

log = logging.getLogger(__name__)

_GEMINI_MODEL = "gemini-2.5-flash"
_GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"{_GEMINI_MODEL}:generateContent"
)


# ============================================================
# Topic catalog — categoría → [(slug, label, descripción corta)]
# ============================================================
# Las descripciones son hooks de 1 línea para que el usuario sepa qué
# va a aprender antes de gastar la llamada. El slug se usa como key
# de cache + en el prompt enviado a Gemini.
CATALOG: dict[str, list[tuple[str, str, str]]] = {
    "📊 Empresas": [
        ("revenue_growth",       "Revenue growth",         "Calidad del crecimiento: orgánico, M&A, FX, mix"),
        ("margins",              "Márgenes",               "Gross / operating / net — qué dicen sobre el moat"),
        ("operating_leverage",   "Operating leverage",     "Por qué pequeños cambios en revenue mueven mucho la utilidad"),
        ("free_cash_flow",       "Free Cash Flow",         "El número que más mira un buy-side senior"),
        ("roic",                 "ROIC",                   "Retorno sobre capital invertido vs WACC — value creation"),
        ("roe",                  "ROE · DuPont",           "Descomposición y trampas (apalancamiento que disfraza)"),
        ("debt_analysis",        "Análisis de deuda",      "Coverage, maturity walls, refinancing risk"),
        ("dilution",             "Dilución (SBC + raises)", "Cómo erosiona retornos sin que se note"),
        ("moats",                "Moats económicos",       "Network effects, switching costs, scale, brand"),
        ("unit_economics",       "Unit economics",         "CAC, LTV, payback — para entender modelos SaaS / consumer"),
        ("pricing_power",        "Pricing power",          "Cómo detectarlo antes de que aparezca en el P&L"),
        ("earnings_quality",     "Calidad de earnings",    "Accruals, working capital, non-recurring"),
        ("capital_allocation",   "Capital allocation",     "Buybacks vs dividendos vs capex vs M&A"),
        ("guidance",             "Guidance de management", "Cómo leer entre líneas en earnings calls"),
        ("cyclicality",          "Ciclicidad",             "Normalizar earnings para no comprar peaks"),
        ("competitive_advantages", "Ventajas competitivas", "Por qué duran las que duran"),
        ("saas_metrics",         "SaaS metrics",           "ARR, NRR, magic number, rule of 40"),
        ("banking_metrics",      "Bancos · métricas",      "NIM, efficiency, NPL, CET1, ROTE"),
        ("insurance_metrics",    "Aseguradoras · métricas", "Combined ratio, float, reserves"),
        ("semis_metrics",        "Semis · métricas",       "Inventory days, design wins, capex intensity"),
        ("consumer_brands",      "Consumer brands",        "Brand equity, market share, pricing premium"),
        ("network_effects",      "Network effects",        "Por qué hay winner-takes-most en algunos modelos"),
    ],
    "💰 Valuación": [
        ("dcf",                  "DCF",                    "El framework, sus assumptions críticas y cuándo NO usarlo"),
        ("multiples_overview",   "Múltiplos · overview",   "Cuándo cada múltiplo y por qué"),
        ("ev_ebitda",            "EV/EBITDA",              "Por qué prefieren EV vs P/E en industriales / leverage"),
        ("pe_ratio",             "P/E",                    "El más usado y el más mal usado"),
        ("peg",                  "PEG",                    "Growth-adjusted — cuándo es trampa"),
        ("sotp",                 "Sum-of-the-parts",       "Conglomerados, hidden value, holding discount"),
        ("terminal_value",       "Terminal value",         "El 70% del DCF — qué assumptions importan"),
        ("sensitivity_analysis", "Sensitivity analysis",   "WACC × g terminal — leer la matriz como pro"),
        ("scenario_analysis",    "Scenario analysis",      "Bull / base / bear — no es promediar es discriminar"),
        ("intrinsic_value",      "Intrinsic value",        "El concepto Damodaranista — value vs price"),
        ("margin_of_safety",     "Margin of safety",       "Graham, Buffett, Marks — la única defensa real"),
    ],
    "🏛️ Sectores": [
        ("sector_banks",         "Bancos",                 "P/TBV, ROTE, sensibilidad a curva, credit losses"),
        ("sector_tech",          "Tecnológicas",           "Growth-at-scale, rule of 40, valuation por etapa"),
        ("sector_utilities",     "Utilities",              "Regulated returns, rate base, allowed ROE"),
        ("sector_energy",        "Energía",                "Reservas, breakeven price, capital intensity"),
        ("sector_consumer",      "Consumo masivo",         "Pricing, volumes, brand equity, EM exposure"),
        ("sector_industrials",   "Industriales",           "Backlog, book-to-bill, ciclo capex"),
        ("sector_healthcare",    "Healthcare",             "Pipeline, patent cliff, payer mix"),
        ("sector_semis",         "Semiconductores",        "Ciclo, lead times, capex intensity, geopolitical"),
    ],
    "🌐 Macro & economía": [
        ("inflation",            "Inflación",              "Headline vs core, expectativas, base effects"),
        ("interest_rates",       "Tasas de interés",       "Real vs nominal, curva, impacto en activos"),
        ("yield_curve",          "Yield curve",            "Forma, inversión, predictivo de recesión"),
        ("credit_spreads",       "Credit spreads",         "IG vs HY, leading indicator de stress"),
        ("gdp",                  "GDP",                    "Composición, growth vs nivel, nowcasting"),
        ("unemployment",         "Desempleo",              "U-3, U-6, participation rate, wage growth"),
        ("monetary_policy",      "Política monetaria",     "Fed, ECB, BoJ — herramientas y reaction function"),
        ("fiscal_policy",        "Política fiscal",        "Deficit, debt-to-GDP, fiscal multiplier"),
        ("liquidity",            "Liquidez",               "M2, reverse repo, RRP, financial conditions"),
        ("business_cycles",      "Ciclos económicos",      "Expansión, peak, contracción, trough — y cómo posicionarse"),
        ("recession_indicators", "Recession indicators",   "Curva, claims, ISM, Sahm rule"),
        ("dollar_strength",      "Dólar (DXY)",            "Driver de EM, commodities, earnings multinacionales"),
        ("commodity_cycles",     "Commodity cycles",       "Super-ciclos, supply response, financialization"),
    ],
    "📈 Mercado": [
        ("risk_on_off",          "Risk-on vs risk-off",    "Cómo se lee el cambio de régimen"),
        ("positioning",          "Positioning",            "CFTC, dealer gamma, fund flows — lo que mueve a corto"),
        ("sentiment",            "Sentiment",              "VIX, put/call, AAII — contrarian vs trend"),
        ("volatility",           "Volatilidad",            "Term structure, vol-of-vol, ATM vs skew"),
        ("earnings_season",      "Earnings season",        "Beats/misses, guidance, reacción del precio"),
        ("institutional_flows",  "Flows institucionales",  "ETFs, mutual funds, hedge funds, retail"),
        ("market_regimes",       "Market regimes",         "Bull, bear, range-bound — y cómo cambia la estrategia"),
        ("factor_investing",     "Factor investing",       "Value, momentum, quality, size, low-vol"),
        ("momentum",             "Momentum",               "El factor con mejor evidencia empírica"),
        ("growth_vs_value",      "Growth vs value",        "Por qué rotan y cuándo"),
    ],
}


def all_topics() -> list[tuple[str, str, str, str]]:
    """Flat list of (category, slug, label, descr) for search."""
    out: list[tuple[str, str, str, str]] = []
    for cat, topics in CATALOG.items():
        for slug, label, descr in topics:
            out.append((cat, slug, label, descr))
    return out


def find_topic(slug: str) -> Optional[tuple[str, str, str, str]]:
    """Lookup (category, slug, label, descr) by slug."""
    for cat, topics in CATALOG.items():
        for s, label, descr in topics:
            if s == slug:
                return (cat, s, label, descr)
    return None


# ============================================================
# Prompt — masterclass de 10 secciones
# ============================================================
_SYSTEM = (
    "Sos un analista senior de equity research, profesor de finanzas "
    "y estratega macroeconómico. Tu objetivo es crear contenido "
    "educativo de nivel profesional pero fácil de entender para "
    "inversores retail avanzados y estudiantes de finanzas.\n\n"
    "La explicación debe ser clara, estructurada, práctica y enfocada "
    "en desarrollar pensamiento analítico real, no solo teoría. "
    "Evitá respuestas genéricas. Enseñá cómo piensa un analista "
    "buy-side/sell-side profesional.\n\n"
    "REGLAS:\n"
    "- Explicá el 'por qué' detrás de cada métrica.\n"
    "- Relacioná empresa → industria → economía → mercado.\n"
    "- Mostrá cómo interpretar datos, no solo definirlos.\n"
    "- Incluí ejemplos reales (empresas, eventos históricos).\n"
    "- Priorizá contenido accionable.\n"
    "- Mencioná errores comunes de principiantes.\n"
    "- Lenguaje simple pero sofisticado — como un mix entre Howard "
    "Marks, Damodaran, McKinsey valuation y sell-side reports.\n"
    "- Usá analogías inteligentes cuando ayuden.\n"
    "- Conectá narrativa + números siempre.\n\n"
    "ESTRUCTURA OBLIGATORIA — exactamente estas 10 secciones, en "
    "este orden, con estos títulos markdown:\n\n"
    "# {Título del módulo}\n\n"
    "## 1. Concepto principal\n"
    "Explicación profunda y clara del tema.\n\n"
    "## 2. Por qué importa\n"
    "Impacto en valuación, crecimiento, riesgo o retorno esperado.\n\n"
    "## 3. Cómo lo analiza un profesional\n"
    "Frameworks mentales, preguntas clave y lógica que usa un "
    "analista buy-side / sell-side.\n\n"
    "## 4. Métricas clave\n"
    "Lista de KPIs con: qué significan · cómo interpretarlos · "
    "rangos buenos/malos · cuándo pueden engañar.\n\n"
    "## 5. Señales positivas vs señales de alerta\n"
    "Tabla markdown comparativa con columnas | Bullish | Bearish |.\n\n"
    "## 6. Impacto en la valuación\n"
    "Cómo afecta múltiplos, discount rates, márgenes, growth "
    "assumptions, FCF, market sentiment.\n\n"
    "## 7. Caso práctico\n"
    "Empresa real o ejemplo hipotético: qué mirar, qué preguntas "
    "hacerse, qué conclusiones sacar.\n\n"
    "## 8. Errores comunes\n"
    "Errores típicos de inversores principiantes.\n\n"
    "## 9. Mentalidad de analista\n"
    "Cómo pensar correctamente sobre el tema.\n\n"
    "## 10. Resumen rápido\n"
    "Bullet points simples y memorables (máx. 8).\n\n"
    "Escribí en español financiero profesional. Densidad analítica, "
    "no relleno. El resultado debe sentirse como una masterclass "
    "profesional integrada en una plataforma premium."
)


def _user_prompt(topic_label: str, topic_descr: str,
                 category: str) -> str:
    return (
        f"Tema de la masterclass: **{topic_label}**\n"
        f"Categoría: {category}\n"
        f"Hook: {topic_descr}\n\n"
        f"Escribí la lección completa siguiendo la estructura "
        f"obligatoria de 10 secciones. Adaptá los ejemplos al tipo "
        f"de tema (si es macro, ejemplos macro; si es sector, "
        f"empresas de ese sector; si es valuación, casos clásicos "
        f"como Damodaran usa)."
    )


# ============================================================
# Generation — Gemini call with cache + API usage tracking
# ============================================================
@st.cache_data(ttl=86400, show_spinner=False)
def generate_lesson(slug: str) -> str:
    """Returns the markdown lesson for the topic, or an error string
    starting with '⚠️' when generation fails.

    Cached 24h per slug — re-visits within the day are free."""
    topic = find_topic(slug)
    if topic is None:
        return f"⚠️ Tema desconocido: `{slug}`"
    category, _, label, descr = topic

    try:
        from core.config import read_secret
        key = read_secret("GOOGLE_API_KEY", "")
    except Exception:
        key = ""
    if not key:
        return (
            "⚠️ **GOOGLE_API_KEY no configurada.** Para generar "
            "lecciones agregá la key en `.streamlit/secrets.toml` "
            "(local) o en App settings → Secrets (Streamlit Cloud)."
        )

    try:
        import requests
    except ImportError:
        return "⚠️ Falta la librería `requests`."

    body = {
        "systemInstruction": {"parts": [{"text": _SYSTEM}]},
        "contents": [{
            "parts": [{"text": _user_prompt(label, descr, category)}]
        }],
        "generationConfig": {
            "temperature": 0.5,
            "maxOutputTokens": 8192,
            # Disable "thinking" budget — for prose it just steals
            # output tokens and risks truncating the lesson.
            "thinkingConfig": {"thinkingBudget": 0},
        },
    }

    try:
        r = requests.post(f"{_GEMINI_URL}?key={key}", json=body, timeout=45)
    except Exception as e:
        try:
            from core.api_usage import record as _track
            _track("gemini")
        except Exception:
            pass
        log.warning("Gemini lesson request failed: %s", e)
        return f"⚠️ Falló la conexión con Gemini: {type(e).__name__}"

    try:
        from core.api_usage import record as _track
        _track("gemini")
    except Exception:
        pass

    if r.status_code == 429:
        return ("⚠️ **Cuota de Gemini agotada por hoy.** El free tier "
                "tiene un techo diario (~250 req). Probá mañana o "
                "configurá un plan pago.")
    if r.status_code != 200:
        log.warning("Gemini lesson HTTP %s", r.status_code)
        return (f"⚠️ Gemini devolvió HTTP {r.status_code}. Reintentá "
                f"en unos minutos.")
    try:
        payload = r.json()
        text = payload["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        log.warning("Gemini lesson unparseable: %s", e)
        return "⚠️ Respuesta de Gemini no parseable."
    return text.strip()

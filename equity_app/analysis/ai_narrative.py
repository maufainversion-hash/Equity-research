"""
Narrador AI del informe de research — Google Gemini.

USO EXCLUSIVO del informe PDF (``exports/pdf_report.py``). Ningún otro
módulo debe llamar acá.

Diseño:
- **Una sola llamada** por PDF: recibe todos los hechos financieros ya
  computados y devuelve la prosa de todas las secciones de una vez.
- La llamada está cacheada (``@st.cache_data``) — regenerar el mismo
  informe no vuelve a consumir cuota.
- Sin ``GOOGLE_API_KEY``, ante un 429/cuota, o ante cualquier fallo de
  red: devuelve ``{}``. El PDF entonces cae a su narrativa rule-based
  (determinística, sin API). El narrador AI es un *upgrade* opcional,
  nunca un requisito.

Regla del prompt: el modelo NO inventa ni altera números — sólo redacta
sobre los hechos provistos, en español financiero profesional.
"""
from __future__ import annotations
import json
import logging
from typing import Any

import streamlit as st

log = logging.getLogger(__name__)

_GEMINI_MODEL = "gemini-2.5-flash"
_GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"{_GEMINI_MODEL}:generateContent"
)

# Secciones que el modelo redacta. Claves estables — el PDF las consume.
_SECTIONS = ("resumen", "negocio", "management", "financiero",
             "rentabilidad", "capital", "ratios", "valuacion",
             "competencia")

_SYSTEM = (
    "Sos analista senior de equity research en un banco de inversión "
    "top-tier (Goldman Sachs / Morgan Stanley / JP Morgan / Bloomberg "
    "Intelligence). Escribís research institucional en español "
    "financiero preciso para portfolio managers, asesores e "
    "inversores sofisticados.\n\n"
    "MARCO ANALÍTICO OBLIGATORIO — cada sección debe contener, en "
    "este orden y entrelazadas (no como bullets):\n"
    "  1) OBSERVACIÓN — el dato o tendencia relevante.\n"
    "  2) INTERPRETACIÓN — el PORQUÉ detrás del movimiento, "
    "conectando con otras métricas.\n"
    "  3) IMPLICANCIA DE NEGOCIO — qué significa para la tesis, "
    "el modelo, la creación de valor o el riesgo.\n\n"
    "REGLAS DE ESTILO:\n"
    "- Tono institucional, analítico y confiado — ni promocional ni "
    "alarmista.\n"
    "- Léxico financiero natural: CAGR, operating leverage, "
    "compounding, pricing power, escalabilidad, calidad de earnings, "
    "FCF conversion, capital allocation, ROIC vs WACC, creación de "
    "valor económico (EVA), foso económico, flexibilidad financiera.\n"
    "- Variá la estructura de las oraciones. Evitá fórmulas robóticas "
    "y la repetición de \"la empresa\" o \"la compañía\".\n"
    "- Priorizá INTERPRETACIÓN por sobre descripción. Nunca te "
    "limites a repetir los números — interpretalos.\n"
    "- Cada oración debe aportar una idea nueva; densidad analítica, "
    "no relleno.\n"
    "- Conectá métricas entre sí (un margen no vive solo: explicá "
    "qué dice sobre escalabilidad, pricing power, mix o eficiencia).\n"
    "- Detectá fundamentals que mejoran o que se deterioran y "
    "señalalo explícitamente.\n\n"
    "REGLAS DE ANÁLISIS AVANZADO (aplicalas cuando los datos las "
    "disparen — y si las disparan, MENCIONALAS por nombre):\n"
    "- Ingresos crecen más rápido que opex → operating leverage.\n"
    "- ROIC > WACC → creación de valor económico (decilo explícito).\n"
    "- EPS crece más rápido que ingresos → margin expansion, "
    "recompras o ganancias de eficiencia (identificá cuál).\n"
    "- Márgenes en expansión consistente → escalabilidad y pricing "
    "power.\n"
    "- FCF consistentemente positivo → flexibilidad financiera y "
    "capacidad de autofinanciar crecimiento.\n"
    "- Deuda baja + cash flow robusto → resiliencia del balance.\n"
    "- Ingresos desacelerando + márgenes mejorando → fase de "
    "madurez y optimización.\n"
    "- Utilidad neta sube pero FCF se debilita → advertir sobre la "
    "calidad de los earnings.\n\n"
    "REGLAS ABSOLUTAS:\n"
    "(1) NO inventes ni modifiques ningún número — usá exclusivamente "
    "los datos provistos. Nombres de competidores, productos y "
    "ejecutivos sí podés citarlos de tu conocimiento general, pero "
    "NUNCA cifras.\n"
    "(2) Si un dato cuantitativo falta, simplemente no lo menciones — "
    "no especules.\n"
    "(3) Prosa densa: 4 a 7 oraciones por sección, sin frases vacías "
    "ni cierres genéricos.\n"
    "(4) No describas los datos sin interpretarlos. \"Los ingresos "
    "crecieron 12%\" no alcanza — explicá por qué, qué refleja sobre "
    "el negocio y qué implica."
)


def _build_prompt(facts: dict[str, Any]) -> str:
    lines = [
        "Datos cuantitativos de la empresa (estos son los ÚNICOS "
        "números que podés usar — no inventes nada fuera de este "
        "bloque):",
        json.dumps(facts, ensure_ascii=False, indent=2, default=str),
        "",
        "Redactá un párrafo de research institucional para cada "
        "sección, aplicando el marco Observación → Interpretación → "
        "Implicancia. Devolvé EXCLUSIVAMENTE un objeto JSON con estas "
        "claves exactas:",
        "",
        "- resumen: Executive Summary institucional. Sintetizá la "
        "performance, la trayectoria de ingresos y earnings, la "
        "evolución de márgenes, la eficiencia del capital, la salud "
        "financiera y la calidad del crecimiento. Identificá 2-3 "
        "fortalezas centrales y el principal riesgo. Cerrá con una "
        "oración-tesis estilo institucional (veredicto + nivel de "
        "convicción + horizonte).",
        "",
        "- negocio: Revenue & Business Evolution. Analizá el CAGR de "
        "ingresos, el crecimiento YoY, aceleración o desaceleración, "
        "escalabilidad del modelo, ciclicidad y consistencia. "
        "Interpretá si el crecimiento es estructuralmente sostenible, "
        "si la empresa entra en fase de madurez o expansión, y si "
        "está impulsado por precios, volumen, M&A o expansión "
        "operativa. Conectá con el panorama estructural hacia "
        "adelante.",
        "",
        "- management: Equipo directivo y calidad de la asignación de "
        "capital. Citá al CEO por nombre si lo conocés, su "
        "trayectoria, cambios relevantes de liderazgo. Evaluá la "
        "calidad de capital allocation observada en los datos "
        "(recompras vs dividendos vs reinversión vs M&A) y qué dice "
        "sobre la disciplina y el track record del management.",
        "",
        "- financiero: Profitability Analysis + Cash Flow Quality. "
        "Analizá gross margin, operating margin, EBITDA margin y net "
        "margin: ¿expansión o compresión? ¿operating leverage? "
        "¿pricing power? ¿mejoras estructurales o temporales? Cruzá "
        "con la evolución de OCF y FCF: si los earnings contables se "
        "traducen en caja (FCF conversion), CapEx intensity, y si "
        "puede autofinanciar el crecimiento. Si net income mejora "
        "mientras FCF se debilita, advertí sobre calidad de "
        "earnings.",
        "",
        "- rentabilidad: Capital Efficiency. Analizá ROE, ROA y ROIC "
        "y compará explícitamente ROIC contra WACC. Si ROIC > WACC, "
        "afirmá creación de valor económico; si ROIC < WACC, "
        "destrucción de valor. Interpretá qué dicen estos retornos "
        "sobre la calidad del capital allocation del management y "
        "sobre la existencia de ventajas competitivas estructurales "
        "(foso económico, pricing power, eficiencia operativa).",
        "",
        "- capital: Financial Health & Risk. Analizá deuda/patrimonio, "
        "deuda neta/EBITDA, cobertura de intereses, liquidez "
        "corriente y posición de caja. Evaluá fortaleza del balance, "
        "riesgo de refinanciación, perfil de liquidez y flexibilidad "
        "financiera. Conectá con la asignación de capital observada "
        "(recompras, dividendos, CapEx) y qué dice sobre la "
        "disciplina financiera y el espacio para retornar capital a "
        "accionistas.",
        "",
        "- ratios: mirá 'ratios_evolucion' y elegí los 3 a 5 ratios "
        "cuya trayectoria sea MÁS llamativa (mayor magnitud de "
        "movimiento, mayor relevancia para la tesis). Para cada uno "
        "explicá la cadena causal del movimiento, descomponiéndolo "
        "en sus drivers — márgenes, rotación de activos, "
        "apalancamiento, costo de la deuda, conversión de caja. NO "
        "es una lista de cambios: es un análisis de causas "
        "encadenadas. Cerrá interpretando qué dice el conjunto sobre "
        "la evolución de fundamentals.",
        "",
        "- valuacion: Valuation Perspective. Comentá el rango de los "
        "modelos de valuación, el potencial vs precio de mercado y "
        "qué implica la dispersión entre modelos (¿alta convicción o "
        "alta incertidumbre?). Si hay múltiplos en los datos (P/E, "
        "EV/EBITDA, P/S, P/B, PEG) analizá si la valuación implica "
        "optimismo o cautela y si los múltiplos premium están "
        "justificados por la calidad del crecimiento y la "
        "rentabilidad. Conectá valuación con fundamentals.",
        "",
        "- competencia: Panorama competitivo + Final Investment View. "
        "Caracterizá el panorama competitivo, citá a los principales "
        "competidores por nombre, evaluá la posición relativa y la "
        "solidez del foso económico. Cerrá con el Investment View: "
        "bull case (qué tiene que pasar para outperformance), bear "
        "case (qué puede salir mal), principales catalizadores y "
        "riesgos. La conclusión debe parecer una tesis de inversión "
        "institucional real.",
    ]
    return "\n".join(lines)


@st.cache_data(ttl=3600, show_spinner=False)
def generate_pdf_narrative(ticker: str, facts: dict[str, Any]) -> dict[str, str]:
    """Prosa de research para el PDF, vía Gemini — UNA llamada.

    Devuelve ``{seccion: parrafo}`` o ``{}`` ante key ausente / cuota /
    fallo. El caller (pdf_report) cae a la narrativa rule-based cuando
    el dict viene vacío."""
    try:
        from core.config import read_secret
        key = read_secret("GOOGLE_API_KEY", "")
    except Exception:
        key = ""
    if not key:
        log.debug("GOOGLE_API_KEY no configurada — narrativa AI omitida")
        return {}

    try:
        import requests
    except ImportError:
        return {}

    body = {
        "systemInstruction": {"parts": [{"text": _SYSTEM}]},
        "contents": [{"parts": [{"text": _build_prompt(facts)}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.4,
            # 9 secciones de prosa densa — techo holgado para que el
            # JSON nunca se trunque a mitad de una sección.
            "maxOutputTokens": 8192,
            # gemini-2.5-flash gasta budget en "thinking"; para prosa
            # no hace falta — desactivarlo evita que el JSON se trunque.
            "thinkingConfig": {"thinkingBudget": 0},
        },
    }
    try:
        r = requests.post(f"{_GEMINI_URL}?key={key}", json=body, timeout=30)
    except Exception as e:
        log.warning("Gemini request failed: %s", e)
        try:
            from core.api_usage import record as _track
            _track("gemini")            # cuenta el intento — gastó cuota igual
        except Exception:
            pass
        return {}
    try:
        from core.api_usage import record as _track
        _track("gemini")
    except Exception:
        pass
    if r.status_code != 200:
        # 429 = cuota; cualquier no-200 → fallback silencioso.
        log.warning("Gemini returned HTTP %s — falling back to rule-based",
                    r.status_code)
        return {}
    try:
        payload = r.json()
        text = payload["candidates"][0]["content"]["parts"][0]["text"]
        parsed = json.loads(text)
    except Exception as e:
        log.warning("Gemini response unparseable: %s", e)
        return {}
    if not isinstance(parsed, dict):
        return {}

    # Quedarse sólo con las secciones esperadas, como strings limpios.
    out: dict[str, str] = {}
    for sec in _SECTIONS:
        v = parsed.get(sec)
        if isinstance(v, str) and v.strip():
            out[sec] = v.strip()
    return out

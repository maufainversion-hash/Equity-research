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
    "Sos un analista senior de equity research de un banco de inversión. "
    "Escribís en español profesional con lenguaje financiero preciso "
    "(CAGR, márgenes, ROIC vs WACC, apalancamiento, múltiplos, creación "
    "de valor, ventaja competitiva, foso económico). Tu trabajo es "
    "explicar la EVOLUCIÓN del negocio y de las métricas, el panorama "
    "competitivo y qué implican para la tesis de inversión. "
    "Reglas absolutas: (1) NO inventes ni modifiques ningún número — "
    "usá exclusivamente los datos provistos; los nombres de "
    "competidores, productos y ejecutivos sí podés citarlos de tu "
    "conocimiento general de la empresa, pero NO inventes cifras; "
    "(2) si un dato cuantitativo falta, no lo menciones; (3) prosa "
    "densa y analítica — 4 a 6 oraciones por sección, sin relleno ni "
    "frases vacías; (4) tono objetivo de research institucional, ni "
    "promocional ni alarmista; (5) cada oración debe aportar una idea "
    "nueva — desarrollo, no enumeración."
)


def _build_prompt(facts: dict[str, Any]) -> str:
    lines = [
        "Datos de la empresa a analizar (las CIFRAS son las únicas que "
        "podés usar — no inventes números fuera de esto):",
        json.dumps(facts, ensure_ascii=False, indent=2, default=str),
        "",
        "Redactá un párrafo de research denso y analítico para cada "
        "sección. Devolvé SÓLO un objeto JSON con estas claves exactas:",
        "- resumen: tesis de inversión de alto nivel — recomendación, "
        "los 2-3 drivers centrales y el principal riesgo.",
        "- negocio: evolución del modelo de negocio y de los ingresos, "
        "cómo gana plata la empresa hoy vs su historia, y el panorama "
        "y desafíos estructurales que enfrenta hacia adelante.",
        "- management: el equipo directivo y el CEO (citá el nombre si "
        "lo conocés), su trayectoria, cambios de liderazgo relevantes y "
        "la calidad de la asignación de capital de la gestión.",
        "- financiero: evolución de ingresos, márgenes y flujo de caja, "
        "interpretando la calidad y sostenibilidad de las tendencias.",
        "- rentabilidad: ROIC frente al WACC, retorno sobre el capital "
        "y creación o destrucción de valor económico.",
        "- capital: estructura de deuda, apalancamiento, solvencia y "
        "asignación de capital (recompras, dividendos, inversión).",
        "- ratios: mirá 'ratios_evolucion' y elegí los 3 a 5 ratios "
        "cuya trayectoria sea MÁS llamativa (los que más se movieron). "
        "Para cada uno explicá la relación causal de por qué subió o "
        "bajó, descomponiéndolo en sus drivers — márgenes, rotación de "
        "activos, apalancamiento, costo de la deuda, conversión de "
        "caja. No es una lista: es un análisis de causas encadenadas.",
        "- valuacion: rango de los modelos, potencial vs precio de "
        "mercado y qué implica la dispersión entre modelos.",
        "- competencia: el panorama competitivo, los principales "
        "competidores nombrados, la posición relativa de la empresa y "
        "la solidez de su ventaja competitiva (foso económico).",
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
        return {}
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

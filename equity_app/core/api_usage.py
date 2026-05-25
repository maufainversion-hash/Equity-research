"""
API-call tracker — per-session, in-memory.

Cada vez que el proyecto hace una llamada a un proveedor externo
(Gemini, FMP, Finnhub, FRED, Marketaux, Alpha Vantage), incrementa
acá un contador. La página ``API Usage`` lee ``get_usage()`` y
muestra cuánta cuota queda contra el límite free-tier conocido del
proveedor.

Diseño:
- Almacenamiento per-sesión vía ``st.session_state`` cuando hay
  contexto de Streamlit (browser tab).
- Fallback a un dict process-global cuando se llama desde threads
  (el worker del PDF report) o desde tests sin Streamlit. En ese
  caso, contribuye al mismo total que verá la sesión que dispara
  el work — basta porque Streamlit re-lee state al volver al main
  thread.
- No persistencia a disco: el contador vive sólo lo que dura la
  sesión / el proceso.

Decisiones explícitas:
- Sin reset automático por fecha — el usuario eligió "per session".
- Sin bloqueo cuando se acerca al límite — sólo informativo.
- Los límites son los free-tier públicos conocidos y son una
  *referencia* (planes pagos cambian el techo). Editables en
  ``PROVIDER_LIMITS`` sin tocar nada más.
"""
from __future__ import annotations
import logging
import threading
from typing import Optional

log = logging.getLogger(__name__)


# ============================================================
# Free-tier limits (daily, salvo aclaración)
# ============================================================
# Fuente: documentación pública de cada proveedor a la fecha del
# release. Si tu plan es pago, ajustá el techo correspondiente.
PROVIDER_LIMITS: dict[str, dict] = {
    "gemini": {
        "label": "Google Gemini (gemini-2.5-flash)",
        "limit": 250,
        "period": "día",
        "note": "Free tier; narrativa del PDF.",
    },
    "fmp": {
        "label": "Financial Modeling Prep",
        "limit": 250,
        "period": "día",
        "note": "Free tier; fundamentals + comparables.",
    },
    "finnhub": {
        "label": "Finnhub",
        "limit": 3600,                 # 60/min × 60 min → referencia
        "period": "día (60/min)",
        "note": "Rate por minuto; el techo diario es conservador.",
    },
    "fred": {
        "label": "FRED (St. Louis Fed)",
        "limit": 10000,                # holgado; FRED no publica daily cap estricto
        "period": "día",
        "note": "Sin tope diario duro; 120 req/min.",
    },
    "marketaux": {
        "label": "Marketaux (news + sentiment)",
        "limit": 100,
        "period": "día",
        "note": "Free tier estricto.",
    },
    "alpha_vantage": {
        "label": "Alpha Vantage (fallback)",
        "limit": 25,
        "period": "día",
        "note": "Free tier reducido recientemente.",
    },
}


# ============================================================
# Storage backend
# ============================================================
# Process-global fallback. Sólo se usa desde threads / tests sin
# contexto de Streamlit. Protegido por lock para evitar carreras.
_FALLBACK_LOCK = threading.Lock()
_FALLBACK_COUNTS: dict[str, int] = {}

_SESSION_KEY = "_api_usage_counts"


def _has_streamlit_ctx() -> bool:
    """True sólo si estamos dentro de un script-run de Streamlit.

    Necesario porque ``st.session_state`` emite warnings molestos
    si lo tocás sin ScriptRunContext (threads, tests). Detectarlo
    primero evita esos warnings."""
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        # suppress_warning evita el "missing ScriptRunContext" en stderr
        # cuando corremos desde threads/tests — esperado, no es un error.
        return get_script_run_ctx(suppress_warning=True) is not None
    except Exception:
        return False


def _get_store() -> tuple[dict, bool]:
    """Devuelve ``(dict_de_contadores, is_session_scoped)``.

    Si estamos dentro de una sesión Streamlit, usa
    ``st.session_state``. Si no (thread, test), usa el fallback
    process-global. El segundo elemento del tuple indica cuál se
    usó — útil para la UI que avisa al usuario."""
    if not _has_streamlit_ctx():
        return _FALLBACK_COUNTS, False
    try:
        import streamlit as st  # type: ignore
        store = st.session_state.setdefault(_SESSION_KEY, {})
        return store, True
    except Exception:
        return _FALLBACK_COUNTS, False


# ============================================================
# Public API
# ============================================================
def record(provider: str, n: int = 1) -> None:
    """Incrementa el contador del proveedor. Silencioso ante fallo.

    Llamar JUSTO DESPUÉS de la request HTTP (con o sin éxito —
    cuenta el consumo de cuota, no el éxito del response). Idempotente
    en el sentido de que un fallo de storage nunca rompe el call site."""
    if not provider:
        return
    key = provider.lower()
    try:
        store, scoped = _get_store()
        if scoped:
            store[key] = int(store.get(key, 0)) + n
        else:
            with _FALLBACK_LOCK:
                _FALLBACK_COUNTS[key] = int(_FALLBACK_COUNTS.get(key, 0)) + n
    except Exception as e:
        log.debug("api_usage.record(%s) failed: %s", provider, e)


def get_usage() -> dict[str, dict]:
    """Snapshot por proveedor, listo para renderizar.

    Devuelve un dict ``provider → {label, calls, limit, remaining,
    pct_used, period, note}`` para TODOS los proveedores listados en
    ``PROVIDER_LIMITS``, incluso los que tienen 0 llamadas — así la
    UI puede mostrar el cuadro completo siempre."""
    store, scoped = _get_store()
    counts: dict[str, int] = {}
    for k, v in store.items():
        counts[k.lower()] = int(v)
    # Mezclá fallback sólo si el store de la sesión NO es el fallback
    # mismo — si lo es (sin contexto Streamlit), ya lo contamos arriba
    # y volver a sumarlo duplicaría todo.
    if scoped:
        with _FALLBACK_LOCK:
            for k, v in _FALLBACK_COUNTS.items():
                counts[k.lower()] = counts.get(k.lower(), 0) + int(v)

    out: dict[str, dict] = {}
    for prov, meta in PROVIDER_LIMITS.items():
        calls = int(counts.get(prov, 0))
        limit = int(meta["limit"])
        remaining = max(0, limit - calls)
        pct = (calls / limit * 100.0) if limit > 0 else 0.0
        out[prov] = {
            "label": meta["label"],
            "calls": calls,
            "limit": limit,
            "remaining": remaining,
            "pct_used": round(pct, 1),
            "period": meta.get("period", "día"),
            "note": meta.get("note", ""),
        }
    return out


def reset(provider: Optional[str] = None) -> None:
    """Resetea contadores. Sin argumento → todos los proveedores."""
    store, _ = _get_store()
    with _FALLBACK_LOCK:
        if provider is None:
            store.clear()
            _FALLBACK_COUNTS.clear()
        else:
            k = provider.lower()
            store.pop(k, None)
            _FALLBACK_COUNTS.pop(k, None)

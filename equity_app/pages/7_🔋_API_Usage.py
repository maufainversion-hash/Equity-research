"""
API Usage — cuota restante por proveedor (per-sesión).

Cuenta las llamadas que esta sesión hizo a cada API externa
(Gemini, FMP, Finnhub, FRED, Marketaux, Alpha Vantage) y las
muestra contra el techo free-tier conocido del proveedor. Sirve
como tablero rápido para saber "cuántas llamadas me quedan hoy"
antes de regenerar un PDF o cargar otro ticker.

Es per-sesión a propósito (decisión del usuario): no persiste
entre reinicios del proceso ni se sincroniza entre tabs distintos
del browser. Si abrís dos tabs vas a ver dos contadores separados.
"""
from __future__ import annotations
import streamlit as st

from core.api_usage import get_usage, reset, PROVIDER_LIMITS


# ============================================================
# Header
# ============================================================
st.markdown(
    "<div style='text-align:center;color:#94a3b8;"
    "font-size:12px;letter-spacing:0.1em;margin:8px 0;'>API USAGE</div>",
    unsafe_allow_html=True,
)
st.markdown(
    "<h1 style='text-align:center;margin-bottom:8px;'>"
    "Consumo de API por sesión</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align:center;color:#94a3b8;margin-bottom:24px;'>"
    "Cuántas llamadas hiciste a cada proveedor en esta sesión, "
    "contra el límite free-tier conocido. Si tu plan es pago, los "
    "techos reales son más altos que los mostrados acá.</p>",
    unsafe_allow_html=True,
)


# ============================================================
# Toolbar
# ============================================================
col_refresh, col_reset, _ = st.columns([1, 1, 5])
with col_refresh:
    if st.button("Actualizar", use_container_width=True):
        st.rerun()
with col_reset:
    if st.button("Resetear contadores", use_container_width=True):
        reset()
        st.success("Contadores reseteados.")
        st.rerun()


# ============================================================
# Per-provider cards
# ============================================================
usage = get_usage()

# Color por nivel de uso — verde <60%, amarillo 60-80%, rojo >80%.
def _bar_color(pct: float) -> str:
    if pct >= 80:
        return "#ef4444"               # rojo
    if pct >= 60:
        return "#f59e0b"               # amarillo
    return "#10b981"                   # verde


def _badge(text: str, color: str) -> str:
    return (
        f"<span style='display:inline-block;padding:2px 8px;"
        f"border-radius:4px;background:{color}22;color:{color};"
        f"font-size:11px;font-weight:600;'>{text}</span>"
    )


# Layout: dos columnas para aprovechar el wide layout.
providers = list(PROVIDER_LIMITS.keys())
for i in range(0, len(providers), 2):
    row = providers[i:i + 2]
    cols = st.columns(2)
    for col, prov in zip(cols, row):
        u = usage[prov]
        color = _bar_color(u["pct_used"])
        # Badge de estado: OK / Atención / Crítico
        if u["pct_used"] >= 80:
            badge = _badge("CRÍTICO", "#ef4444")
        elif u["pct_used"] >= 60:
            badge = _badge("ATENCIÓN", "#f59e0b")
        else:
            badge = _badge("OK", "#10b981")

        bar_pct = min(100.0, u["pct_used"])
        with col:
            st.markdown(
                f"""
<div style="border:1px solid #334155;border-radius:8px;
padding:16px;margin-bottom:12px;background:#0f172a;">
  <div style="display:flex;justify-content:space-between;
align-items:center;margin-bottom:6px;">
    <div style="font-weight:600;color:#e2e8f0;">{u["label"]}</div>
    {badge}
  </div>
  <div style="display:flex;justify-content:space-between;
font-size:13px;color:#94a3b8;margin-bottom:8px;">
    <span>{u["calls"]} / {u["limit"]} llamadas</span>
    <span>{u["remaining"]} restantes</span>
  </div>
  <div style="background:#1e293b;border-radius:4px;height:8px;
overflow:hidden;">
    <div style="width:{bar_pct:.1f}%;height:100%;background:{color};
transition:width 0.3s ease;"></div>
  </div>
  <div style="margin-top:8px;font-size:11px;color:#64748b;">
    Período: {u["period"]} · {u["note"]}
  </div>
</div>
""",
                unsafe_allow_html=True,
            )

        # Warning explícito por debajo cuando queda <20%.
        if u["pct_used"] >= 80 and u["limit"] > 0:
            with col:
                st.warning(
                    f"Quedan {u['remaining']} llamadas en {u['label']}. "
                    "Considerá esperar al próximo período o reducir el "
                    "uso para evitar respuestas vacías.",
                    icon="⚠️",
                )


# ============================================================
# Footer / disclaimer
# ============================================================
st.markdown("---")
st.caption(
    "Los contadores son **per-sesión** — se cuentan sólo las "
    "llamadas que esta sesión disparó, no las de otros usuarios o "
    "tabs. Los límites mostrados corresponden al **free tier público** "
    "de cada proveedor a la fecha del release; tu plan real puede "
    "tener techos distintos. Los providers consultados desde threads "
    "(p.ej. la narrativa AI del PDF que corre en background) también "
    "se suman acá."
)

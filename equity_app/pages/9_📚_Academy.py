"""
Academy — masterclass financiera generada con Gemini on-demand.

Catálogo curado de ~60 temas agrupados por categoría. Click en un
tema → la lección se genera con Gemini siguiendo una estructura
fija de 10 secciones (Concepto, Por qué importa, Cómo lo analiza
un pro, Métricas, Señales bull/bear, Impacto en valuación, Caso
práctico, Errores comunes, Mentalidad, Resumen).

Cada lección queda cacheada 24h por slug, así re-visitar el mismo
tema dentro del día no quema cuota Gemini.
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from analysis.learn_content import (
    CATALOG, all_topics, find_topic, generate_lesson,
)


# ============================================================
# Page header
# ============================================================
st.markdown(
    """
<div style="margin-bottom:18px;">
  <div style="display:flex;align-items:baseline;gap:14px;">
    <h1 style="margin:0;font-size:26px;font-weight:700;color:#F3F4F6;">
      📚 Academy
    </h1>
    <span style="color:#94A3B8;font-size:12px;letter-spacing:0.06em;
text-transform:uppercase;">masterclass financiera · AI-powered</span>
  </div>
  <div style="color:#94A3B8;font-size:13px;margin-top:6px;">
    Lecciones nivel research institucional generadas con Gemini —
    cada tema en 10 secciones: concepto, métricas, señales,
    impacto en valuación, caso práctico, errores comunes y mentalidad.
  </div>
</div>
""",
    unsafe_allow_html=True,
)


# ============================================================
# Layout: sidebar de búsqueda/catalog + área de contenido
# ============================================================
# Estado: tema seleccionado vive en session_state para sobrevivir reruns.
if "academy_selected" not in st.session_state:
    st.session_state["academy_selected"] = None

col_nav, col_main = st.columns([1.0, 2.4], gap="medium")


# ---- Left column: catálogo ----
with col_nav:
    st.markdown(
        '<div class="eq-section-label">CATÁLOGO</div>',
        unsafe_allow_html=True,
    )

    # Búsqueda por texto — filtra el catálogo
    query = st.text_input(
        "Buscar tema",
        value="",
        placeholder="Ej.: DCF, ROIC, semis, inflación…",
        label_visibility="collapsed",
    ).strip().lower()

    if query:
        # Vista plana filtrada
        matches = [
            (cat, slug, label, descr)
            for cat, slug, label, descr in all_topics()
            if query in label.lower() or query in descr.lower()
            or query in cat.lower()
        ]
        if not matches:
            st.caption(f"Sin coincidencias para «{query}».")
        else:
            st.caption(f"{len(matches)} coincidencia(s):")
            for cat, slug, label, descr in matches[:30]:
                if st.button(
                    f"{label}",
                    key=f"academy_pick_{slug}",
                    width="stretch",
                    help=f"{cat} · {descr}",
                ):
                    st.session_state["academy_selected"] = slug
                    st.rerun()
    else:
        # Vista jerárquica por categoría
        for category, topics in CATALOG.items():
            with st.expander(f"{category}  ({len(topics)})", expanded=False):
                for slug, label, descr in topics:
                    is_active = (
                        st.session_state["academy_selected"] == slug
                    )
                    btn_label = ("▶ " + label) if is_active else label
                    if st.button(
                        btn_label,
                        key=f"academy_pick_{slug}",
                        width="stretch",
                        help=descr,
                    ):
                        st.session_state["academy_selected"] = slug
                        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.caption(
        f"**{len(all_topics())} temas** · cada lección se cachea 24h "
        "para no quemar cuota de Gemini."
    )


# ---- Right column: lección renderizada ----
with col_main:
    selected = st.session_state["academy_selected"]
    if selected is None:
        # Landing — explicación + featured suggestions
        st.markdown(
            """
<div style="background:#0f172a;border:1px solid #334155;
border-radius:8px;padding:20px 24px;margin-top:4px;">
<h2 style="margin:0 0 10px 0;font-size:18px;color:#F3F4F6;">
Cómo usar la Academy
</h2>
<div style="color:#cbd5e1;font-size:13px;line-height:1.6;">
Elegí un tema del catálogo a la izquierda y la lección se genera al
instante. El estilo combina equity research institucional con
explicaciones prácticas — pensado para inversores retail avanzados y
estudiantes que quieren <b>aprender a pensar como un analista</b>, no
solo memorizar fórmulas.
<br><br>
Cada masterclass cubre:<br>
&nbsp;&nbsp;1. Concepto principal · 2. Por qué importa<br>
&nbsp;&nbsp;3. Cómo lo analiza un pro · 4. Métricas clave<br>
&nbsp;&nbsp;5. Señales bullish / bearish · 6. Impacto en valuación<br>
&nbsp;&nbsp;7. Caso práctico · 8. Errores comunes<br>
&nbsp;&nbsp;9. Mentalidad de analista · 10. Resumen rápido
</div>
</div>
""",
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        # Picks recomendados para empezar — atajos rápidos
        st.markdown(
            '<div class="eq-section-label">SUGERIDOS PARA EMPEZAR</div>',
            unsafe_allow_html=True,
        )
        featured = [
            ("free_cash_flow",  "💵", "Free Cash Flow"),
            ("roic",            "📐", "ROIC"),
            ("dcf",             "🧮", "DCF"),
            ("margin_of_safety", "🛡️", "Margin of safety"),
            ("yield_curve",     "📈", "Yield curve"),
            ("market_regimes",  "🌐", "Market regimes"),
        ]
        cols = st.columns(3, gap="small")
        for (slug, emoji, label), col in zip(featured, cols * 2):
            with col:
                if st.button(
                    f"{emoji}  {label}",
                    key=f"academy_feat_{slug}",
                    width="stretch",
                ):
                    st.session_state["academy_selected"] = slug
                    st.rerun()
    else:
        # Render lesson
        topic = find_topic(selected)
        if topic is None:
            st.error(f"Tema desconocido: `{selected}`")
        else:
            cat, _, label, descr = topic
            # Header de la lección
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;'
                f'align-items:center;margin-bottom:10px;">'
                f'<div>'
                f'<span style="color:#94A3B8;font-size:11px;letter-spacing:'
                f'0.08em;text-transform:uppercase;">{cat}</span>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

            # Botón de regenerar (clear cache y vuelve a llamar Gemini)
            col_r1, col_r2 = st.columns([5, 1])
            with col_r2:
                if st.button("🔁 Regenerar", key=f"regen_{selected}",
                              width="stretch",
                              help="Borra el cache de esta lección y "
                                   "vuelve a llamar a Gemini"):
                    generate_lesson.clear()
                    st.rerun()

            with st.spinner("Generando masterclass…"):
                lesson_md = generate_lesson(selected)

            if lesson_md.startswith("⚠️"):
                st.warning(lesson_md, icon="⚠️")
            else:
                st.markdown(lesson_md, unsafe_allow_html=False)

            st.markdown("---")
            st.caption(
                f"Tema: **{label}** · Generado por Gemini · "
                f"Cacheado 24h. Si querés otra perspectiva o más "
                f"profundidad, usá 🔁 Regenerar."
            )

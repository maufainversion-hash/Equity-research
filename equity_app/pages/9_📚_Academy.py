"""
Academy — masterclass financiera con contenido curado.

Navegación: 100% via st.session_state (sin URLs, sin reloads).
Estado:
  - academy_cat: str | None — categoría seleccionada
  - academy_topic: str | None — tema seleccionado

Tres vistas:
  1. Landing (cat=None, topic=None): grid de categorías + featured.
  2. Categoría (cat set, topic=None): grid de topics de esa categoría.
  3. Lección (topic set): contenido completo del topic.
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from analysis.learn_content import (
    CATALOG, all_topics, find_topic, get_lesson,
    n_complete, n_total, Lesson,
)


# ============================================================
# Theme + state init
# ============================================================
_CAT_THEME: dict[str, dict[str, str]] = {
    "📊 Empresas":         {"accent": "#10B981", "tint": "rgba(16,185,129,0.10)"},
    "💰 Valuación":        {"accent": "#C9A961", "tint": "rgba(201,169,97,0.10)"},
    "🏛️ Sectores":         {"accent": "#3B82F6", "tint": "rgba(59,130,246,0.10)"},
    "🌐 Macro & economía": {"accent": "#A78BFA", "tint": "rgba(167,139,250,0.10)"},
    "📈 Mercado":          {"accent": "#F59E0B", "tint": "rgba(245,158,11,0.10)"},
}


def _theme(cat: str) -> dict[str, str]:
    return _CAT_THEME.get(cat, {"accent": "#94A3B8",
                                 "tint": "rgba(148,163,184,0.10)"})


# Initialise navigation state. session_state survives reruns but NOT
# page reloads — that's the trade-off vs query params.
if "academy_cat" not in st.session_state:
    st.session_state["academy_cat"] = None
if "academy_topic" not in st.session_state:
    st.session_state["academy_topic"] = None


def _go_landing() -> None:
    st.session_state["academy_cat"] = None
    st.session_state["academy_topic"] = None


def _go_cat(cat: str) -> None:
    st.session_state["academy_cat"] = cat
    st.session_state["academy_topic"] = None


def _go_topic(slug: str) -> None:
    # Resolve the topic's category so the breadcrumb shows it correctly.
    t = find_topic(slug)
    if t is not None:
        st.session_state["academy_cat"] = t[0]
    st.session_state["academy_topic"] = slug


# ============================================================
# CSS — clickable wrapper trick:
# A native st.button is overlaid (position:absolute) on top of an
# HTML card. The button text is invisible (white-on-same-bg with
# opacity 0) but it still receives the click event. Result: pretty
# cards that act as one big button each, no full-page reload, no
# URL change.
# ============================================================
st.markdown(
    """
<style>
/* Card visual — same look we had with the <a href> version */
.aca-card-wrapper {
  position:relative;
  margin-bottom:12px;
}
.aca-card {
  background:#0f172a;
  border:1px solid #334155;
  border-radius:10px;
  padding:18px 20px;
  transition:transform 0.15s ease, border-color 0.15s ease,
             background 0.15s ease;
  pointer-events:none;             /* the overlay button handles clicks */
}
.aca-card-wrapper:hover .aca-card {
  border-color:#475569;
  background:#0b1220;
  transform:translateY(-2px);
}
.aca-cat-card { position:relative; overflow:hidden; }
.aca-cat-card .aca-glow {
  position:absolute; top:-30%; right:-20%;
  width:160px; height:160px;
  border-radius:50%;
  filter:blur(40px);
  opacity:0.35;
  pointer-events:none;
}
.aca-pill {
  display:inline-block;
  padding:2px 8px;
  border-radius:4px;
  font-size:10px;
  font-weight:700;
  letter-spacing:0.06em;
  text-transform:uppercase;
}
.aca-topic-card-inner {
  background:#0f172a;
  border:1px solid #334155;
  border-left:3px solid var(--accent, #94A3B8);
  border-radius:8px;
  padding:14px 16px;
  position:relative;
  transition:transform 0.12s ease, border-color 0.15s ease;
  pointer-events:none;
}
.aca-card-wrapper:hover .aca-topic-card-inner {
  border-color:#64748B;
  transform:translateX(2px);
}
.aca-complete-dot {
  position:absolute;
  top:10px;
  right:12px;
  width:8px;
  height:8px;
  border-radius:50%;
  background:#10B981;
}

/* Overlay button: invisible (transparent) but covers the whole
   card. Click anywhere on the card → click on this button. */
.aca-card-wrapper div[data-testid="stButton"] {
  position:absolute;
  top:0; left:0; right:0; bottom:0;
  margin:0 !important;
}
.aca-card-wrapper div[data-testid="stButton"] > button {
  width:100% !important;
  height:100% !important;
  background:transparent !important;
  border:none !important;
  color:transparent !important;
  cursor:pointer;
  padding:0 !important;
  margin:0 !important;
  border-radius:10px !important;
}
.aca-card-wrapper div[data-testid="stButton"] > button:hover,
.aca-card-wrapper div[data-testid="stButton"] > button:focus {
  background:transparent !important;
  border:none !important;
  box-shadow:none !important;
  outline:none !important;
}
/* Hide the (transparent) button label / p children */
.aca-card-wrapper div[data-testid="stButton"] > button > * {
  opacity:0 !important;
}

/* Default button look across the whole Academy page: a compact CTA
   that visually attaches to the card above it (no border-top,
   rounded only on the bottom). */
div[data-testid="stButton"] > button {
  background:#131826 !important;
  border:1px solid #334155 !important;
  border-top:none !important;
  color:#cbd5e1 !important;
  border-radius:0 0 10px 10px !important;
  padding:10px 14px !important;
  text-align:center !important;
  font-weight:600 !important;
  font-size:12px !important;
  white-space:normal !important;
  height:auto !important;
  letter-spacing:0.04em !important;
  text-transform:uppercase !important;
  width:100% !important;
  margin-top:-12px !important;
  transition:background 0.15s ease, color 0.15s ease,
             border-color 0.15s ease;
}
div[data-testid="stButton"] > button:hover {
  background:#0b1220 !important;
  border-color:#64748B !important;
  color:#F3F4F6 !important;
}
div[data-testid="stButton"] > button:focus {
  outline:none !important;
  box-shadow:none !important;
}

/* Cards without a CTA button below (eg. inside breadcrumb / search
   summary) keep all four corners rounded. */
.aca-card-standalone .aca-card,
.aca-card-standalone .aca-topic-card-inner {
  border-radius:10px;
}

/* Breadcrumb buttons are independent — un-pin them from the generic
   card-CTA style (which assumes there's a card right above). */
.bc-row div[data-testid="stButton"] > button {
  border:1px solid #334155 !important;
  border-radius:8px !important;
  margin-top:0 !important;
  text-transform:none !important;
  letter-spacing:0 !important;
  font-size:13px !important;
  text-align:left !important;
}

.lesson-section {
  background:#0f172a;
  border:1px solid #1F2937;
  border-radius:8px;
  padding:18px 22px;
  margin-bottom:14px;
}
.lesson-section h3 {
  margin:0 0 12px 0;
  font-size:14px;
  font-weight:700;
  color:#C9A961;
  letter-spacing:0.04em;
  text-transform:uppercase;
}
.lesson-section .lesson-body {
  color:#cbd5e1;
  font-size:14px;
  line-height:1.65;
}
.lesson-section .lesson-body strong { color:#F3F4F6; }
.book-card {
  background:#0b1220;
  border:1px solid #1F2937;
  border-left:3px solid #C9A961;
  border-radius:6px;
  padding:12px 14px;
  margin-bottom:8px;
}
.video-card {
  background:#0b1220;
  border:1px solid #1F2937;
  border-left:3px solid #3B82F6;
  border-radius:6px;
  padding:12px 14px;
  margin-bottom:8px;
}
.quote-card {
  background:#0b1220;
  border-left:3px solid #A78BFA;
  border-radius:0 6px 6px 0;
  padding:14px 18px;
  margin-bottom:10px;
  font-style:italic;
  color:#E8EAED;
}
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# Hero header
# ============================================================
done = n_complete()
total = n_total()
st.markdown(
    f"""
<div style="background:linear-gradient(135deg,#0b1220 0%,#131826 100%);
border:1px solid #334155;border-radius:12px;padding:24px 28px;
margin-bottom:24px;position:relative;overflow:hidden;">
  <div style="position:absolute;top:-40px;right:-40px;width:200px;
height:200px;border-radius:50%;background:radial-gradient(circle,
rgba(201,169,97,0.18) 0%,transparent 70%);"></div>
  <div style="display:flex;align-items:baseline;gap:14px;margin-bottom:8px;">
    <h1 style="margin:0;font-size:30px;font-weight:700;color:#F3F4F6;
letter-spacing:-0.02em;">Academy</h1>
    <span style="color:#C9A961;font-size:11px;letter-spacing:0.1em;
text-transform:uppercase;font-weight:600;">
      masterclass financiera · contenido curado
    </span>
  </div>
  <div style="color:#cbd5e1;font-size:14px;line-height:1.55;max-width:780px;">
    Lecciones escritas a mano con fuentes verificables — Graham, Buffett,
    Damodaran, Marks, Klarman, McKinsey, CFA. Cada tema viene con
    definición, métricas, señales, libros canónicos, charlas en video y
    citas atribuidas. <b style="color:#F3F4F6;">Sin AI · sin esperas</b>.
  </div>
  <div style="display:flex;gap:28px;margin-top:16px;
border-top:1px solid #1F2937;padding-top:14px;">
    <div>
      <div style="font-size:22px;font-weight:700;color:#10B981;
font-variant-numeric:tabular-nums;">{done}</div>
      <div style="font-size:10px;color:#94A3B8;letter-spacing:0.08em;
text-transform:uppercase;">lecciones completas</div>
    </div>
    <div>
      <div style="font-size:22px;font-weight:700;color:#F3F4F6;
font-variant-numeric:tabular-nums;">{total}</div>
      <div style="font-size:10px;color:#94A3B8;letter-spacing:0.08em;
text-transform:uppercase;">temas totales</div>
    </div>
    <div>
      <div style="font-size:22px;font-weight:700;color:#F3F4F6;
font-variant-numeric:tabular-nums;">{len(CATALOG)}</div>
      <div style="font-size:10px;color:#94A3B8;letter-spacing:0.08em;
text-transform:uppercase;">categorías</div>
    </div>
    <div>
      <div style="font-size:22px;font-weight:700;color:#F3F4F6;
font-variant-numeric:tabular-nums;">0ms</div>
      <div style="font-size:10px;color:#94A3B8;letter-spacing:0.08em;
text-transform:uppercase;">cero API calls</div>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)


# ============================================================
# Breadcrumb (always rendered when not on landing)
# ============================================================
def _breadcrumb() -> None:
    """Sticky navigation row: home / category / topic links.

    Wrapped in a `.bc-row` div so we can override the generic
    Academy button style (which would otherwise eat the
    margin-top: -12px and clip these buttons up into the hero)."""
    cat = st.session_state["academy_cat"]
    topic_slug = st.session_state["academy_topic"]
    topic_label = ""
    if topic_slug:
        t = find_topic(topic_slug)
        if t is not None:
            topic_label = t[2]

    st.markdown('<div class="bc-row">', unsafe_allow_html=True)
    cols = st.columns([1, 1, 1, 4])
    with cols[0]:
        if st.button("🏠 Inicio", key="bc_home"):
            _go_landing()
            st.rerun()
    if cat:
        with cols[1]:
            if st.button(f"← {cat}", key="bc_cat"):
                st.session_state["academy_topic"] = None
                st.rerun()
    if topic_label:
        with cols[2]:
            st.markdown(
                f'<div style="padding:10px 14px;color:#F3F4F6;'
                f'font-size:13px;font-weight:500;">📖 {topic_label}</div>',
                unsafe_allow_html=True,
            )
    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# Lesson render
# ============================================================
def _md_to_html(text: str) -> str:
    """Minimal markdown → HTML (bold + line breaks + lists)."""
    import re
    if not text:
        return ""
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    paragraphs = out.split("\n\n")
    rendered: list[str] = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        lines = p.split("\n")
        is_list = all(
            line.lstrip().startswith(("·", "-", "*")) or
            (line.lstrip()[:2] in {f"{i}." for i in range(1, 10)})
            for line in lines if line.strip()
        )
        if is_list and len(lines) > 1:
            items = "".join(
                f"<li style='margin-bottom:4px;'>"
                f"{line.lstrip('-·*0123456789. ').strip()}</li>"
                for line in lines if line.strip()
            )
            rendered.append(
                f"<ol style='padding-left:20px;margin:6px 0;'>{items}</ol>"
            )
        else:
            rendered.append("<p style='margin:0 0 10px 0;'>"
                             + p.replace("\n", "<br>") + "</p>")
    return "".join(rendered)


def _render_lesson(lesson: Lesson, theme: dict[str, str]) -> None:
    accent = theme["accent"]
    completeness = ("Contenido completo" if lesson.is_complete
                    else "Contenido en desarrollo · ver fuentes recomendadas")
    completeness_color = "#10B981" if lesson.is_complete else "#F59E0B"

    st.markdown(
        f"""
<div style="background:#0f172a;border:1px solid #334155;
border-left:4px solid {accent};border-radius:8px;
padding:16px 20px;margin-bottom:18px;">
  <div style="font-size:11px;color:{accent};letter-spacing:0.08em;
text-transform:uppercase;font-weight:700;margin-bottom:4px;">
    {lesson.category}</div>
  <h2 style="margin:0;font-size:22px;color:#F3F4F6;font-weight:600;">
    {lesson.label}</h2>
  <div style="font-size:12px;color:#94A3B8;margin-top:4px;">{lesson.hook}</div>
  <div style="font-size:11px;color:{completeness_color};margin-top:8px;
font-weight:600;">● {completeness}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    if not lesson.is_complete:
        st.info(
            "Esta lección todavía está en redacción. Mientras tanto, "
            "los libros, charlas y citas de abajo son el material "
            "recomendado para empezar a profundizar en este tema.",
            icon="📖",
        )
    else:
        # 1. Concepto
        st.markdown(
            f'<div class="lesson-section"><h3>1 · Concepto principal</h3>'
            f'<div class="lesson-body">{_md_to_html(lesson.definition)}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        # 2. Por qué importa
        if lesson.why_matters:
            st.markdown(
                f'<div class="lesson-section"><h3>2 · Por qué importa</h3>'
                f'<div class="lesson-body">{_md_to_html(lesson.why_matters)}'
                f'</div></div>',
                unsafe_allow_html=True,
            )
        # 3. Cómo lo analiza un pro
        if lesson.how_pros_analyze:
            st.markdown(
                f'<div class="lesson-section">'
                f'<h3>3 · Cómo lo analiza un profesional</h3>'
                f'<div class="lesson-body">'
                f'{_md_to_html(lesson.how_pros_analyze)}</div></div>',
                unsafe_allow_html=True,
            )
        # 4. Métricas clave
        if lesson.key_metrics:
            rows = "".join(
                f'<tr><td style="padding:8px 12px;color:#F3F4F6;'
                f'font-weight:600;width:38%;border-bottom:1px solid #1F2937;">'
                f'{n}</td>'
                f'<td style="padding:8px 12px;color:#cbd5e1;'
                f'border-bottom:1px solid #1F2937;">{v}</td></tr>'
                for n, v in lesson.key_metrics
            )
            st.markdown(
                f'<div class="lesson-section"><h3>4 · Métricas clave</h3>'
                f'<table style="width:100%;border-collapse:collapse;'
                f'font-size:13px;">{rows}</table></div>',
                unsafe_allow_html=True,
            )
        # 5. Bull vs Bear
        if lesson.bullish_vs_bearish:
            rows = "".join(
                f'<tr><td style="padding:8px 12px;color:#10B981;width:50%;'
                f'border-bottom:1px solid #1F2937;">✓ {b}</td>'
                f'<td style="padding:8px 12px;color:#F87171;'
                f'border-bottom:1px solid #1F2937;">✕ {br}</td></tr>'
                for b, br in lesson.bullish_vs_bearish
            )
            st.markdown(
                f'<div class="lesson-section">'
                f'<h3>5 · Señales bullish vs bearish</h3>'
                f'<table style="width:100%;border-collapse:collapse;'
                f'font-size:13px;">'
                f'<thead><tr>'
                f'<th style="text-align:left;padding:8px 12px;'
                f'color:#10B981;font-size:11px;letter-spacing:0.06em;'
                f'text-transform:uppercase;">Bullish</th>'
                f'<th style="text-align:left;padding:8px 12px;'
                f'color:#F87171;font-size:11px;letter-spacing:0.06em;'
                f'text-transform:uppercase;">Bearish</th>'
                f'</tr></thead><tbody>{rows}</tbody></table></div>',
                unsafe_allow_html=True,
            )
        # 6. Impacto valuación
        if lesson.valuation_impact:
            st.markdown(
                f'<div class="lesson-section">'
                f'<h3>6 · Impacto en la valuación</h3>'
                f'<div class="lesson-body">'
                f'{_md_to_html(lesson.valuation_impact)}</div></div>',
                unsafe_allow_html=True,
            )
        # 7. Caso práctico
        if lesson.case_study:
            st.markdown(
                f'<div class="lesson-section"><h3>7 · Caso práctico</h3>'
                f'<div class="lesson-body">'
                f'{_md_to_html(lesson.case_study)}</div></div>',
                unsafe_allow_html=True,
            )
        # 8. Errores comunes
        if lesson.common_mistakes:
            items = "".join(f'<li style="margin-bottom:6px;">{m}</li>'
                            for m in lesson.common_mistakes)
            st.markdown(
                f'<div class="lesson-section">'
                f'<h3>8 · Errores comunes</h3>'
                f'<ul class="lesson-body" style="padding-left:20px;'
                f'margin:0;">{items}</ul></div>',
                unsafe_allow_html=True,
            )
        # 9. Mentalidad
        if lesson.mental_model:
            st.markdown(
                f'<div class="lesson-section">'
                f'<h3>9 · Mentalidad de analista</h3>'
                f'<div class="lesson-body">'
                f'{_md_to_html(lesson.mental_model)}</div></div>',
                unsafe_allow_html=True,
            )

    # 10. Fuentes
    if lesson.books or lesson.videos or lesson.quotes:
        st.markdown(
            '<div class="lesson-section"><h3>10 · Fuentes recomendadas</h3>',
            unsafe_allow_html=True,
        )
        if lesson.books:
            st.markdown(
                '<div style="color:#94A3B8;font-size:11px;'
                'letter-spacing:0.06em;text-transform:uppercase;'
                'margin-bottom:8px;font-weight:600;">📚 Libros</div>',
                unsafe_allow_html=True,
            )
            for b in lesson.books:
                year = f" ({b.year})" if b.year else ""
                chapter = (f'<div style="font-size:11px;color:#C9A961;'
                            f'margin-top:4px;">→ {b.chapter_hint}</div>'
                            if b.chapter_hint else "")
                why = (f'<div style="font-size:12px;color:#94A3B8;'
                        f'margin-top:6px;font-style:italic;'
                        f'line-height:1.5;">{b.why}</div>' if b.why else "")
                st.markdown(
                    f'<div class="book-card">'
                    f'<div style="font-size:14px;font-weight:600;'
                    f'color:#F3F4F6;">{b.title}</div>'
                    f'<div style="font-size:12px;color:#cbd5e1;'
                    f'margin-top:2px;">{b.author}{year}</div>'
                    f'{chapter}{why}</div>',
                    unsafe_allow_html=True,
                )

        if lesson.videos:
            st.markdown(
                '<div style="color:#94A3B8;font-size:11px;'
                'letter-spacing:0.06em;text-transform:uppercase;'
                'margin-top:14px;margin-bottom:8px;font-weight:600;">'
                '🎥 Videos / charlas</div>',
                unsafe_allow_html=True,
            )
            for v in lesson.videos:
                minutes = f" · ~{v.minutes} min" if v.minutes else ""
                url_link = (
                    f' · <a href="{v.url}" target="_blank" '
                    f'style="color:#3B82F6;">abrir →</a>'
                    if v.url else ""
                )
                why = (f'<div style="font-size:12px;color:#94A3B8;'
                        f'margin-top:6px;font-style:italic;'
                        f'line-height:1.5;">{v.why}</div>' if v.why else "")
                st.markdown(
                    f'<div class="video-card">'
                    f'<div style="font-size:14px;font-weight:600;'
                    f'color:#F3F4F6;">{v.title}</div>'
                    f'<div style="font-size:12px;color:#cbd5e1;'
                    f'margin-top:2px;">{v.channel}{minutes}{url_link}</div>'
                    f'{why}</div>',
                    unsafe_allow_html=True,
                )

        if lesson.quotes:
            st.markdown(
                '<div style="color:#94A3B8;font-size:11px;'
                'letter-spacing:0.06em;text-transform:uppercase;'
                'margin-top:14px;margin-bottom:8px;font-weight:600;">'
                '💬 Citas</div>',
                unsafe_allow_html=True,
            )
            for q in lesson.quotes:
                source = (f' <span style="color:#64748B;font-size:11px;">— '
                            f'{q.source}</span>' if q.source else "")
                st.markdown(
                    f'<div class="quote-card">"{q.text}"<br>'
                    f'<span style="color:#C9A961;font-size:12px;'
                    f'font-style:normal;font-weight:600;">— {q.author}</span>'
                    f'{source}</div>',
                    unsafe_allow_html=True,
                )
        st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# Routing (session-state driven)
# ============================================================
selected_topic = st.session_state["academy_topic"]
selected_cat = st.session_state["academy_cat"]


# ---------- State 3: lesson view ----------
if selected_topic:
    topic = find_topic(selected_topic)
    if topic is None:
        st.error(f"Tema desconocido: `{selected_topic}`")
        if st.button("← Volver al inicio", key="err_back"):
            _go_landing()
            st.rerun()
    else:
        cat, _, label, _ = topic
        _breadcrumb()
        st.markdown("<br>", unsafe_allow_html=True)
        lesson = get_lesson(selected_topic)
        if lesson is None:
            st.warning("Esta lección todavía no tiene contenido.")
        else:
            _render_lesson(lesson, _theme(cat))

# ---------- State 2: category view ----------
elif selected_cat and selected_cat in CATALOG:
    theme = _theme(selected_cat)
    _breadcrumb()
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        f"""
<div class="aca-card-standalone">
<div style="background:#0f172a;border:1px solid #334155;
border-left:4px solid {theme['accent']};border-radius:10px;
padding:16px 20px;margin-bottom:18px;">
  <h2 style="margin:0;font-size:20px;color:#F3F4F6;font-weight:600;">
    {selected_cat}</h2>
  <div style="font-size:12px;color:#94A3B8;margin-top:4px;">
    {len(CATALOG[selected_cat])} lecciones · ● verde = contenido
    completo · sin marca = stub con materiales recomendados
  </div>
</div>
</div>
""",
        unsafe_allow_html=True,
    )

    # Topic cards grid (3 columns, repeated rows)
    topics = CATALOG[selected_cat]
    n_cols = 3
    accent = theme["accent"]
    for row_start in range(0, len(topics), n_cols):
        cols = st.columns(n_cols, gap="small")
        for col, (slug, label, descr) in zip(
            cols, topics[row_start:row_start + n_cols]
        ):
            with col:
                lesson = get_lesson(slug)
                dot = ('<div class="aca-complete-dot"></div>'
                       if (lesson and lesson.is_complete) else "")
                st.markdown(
                    f'<div class="aca-topic-card-inner" '
                    f'style="--accent:{accent};">'
                    f'{dot}'
                    f'<div style="font-size:14px;font-weight:600;'
                    f'color:#F3F4F6;margin-bottom:6px;padding-right:18px;">'
                    f'{label}</div>'
                    f'<div style="font-size:11px;color:#94A3B8;'
                    f'line-height:1.4;min-height:32px;">{descr}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                if st.button("Ver lección →",
                              key=f"topic_btn_{slug}"):
                    _go_topic(slug)
                    st.rerun()

# ---------- State 1: landing ----------
else:
    # Search
    query = st.text_input(
        "Buscar tema",
        value="",
        placeholder="🔍 DCF, ROIC, semis, inflación…",
        label_visibility="collapsed",
    ).strip().lower()

    if query:
        matches = [
            (cat, slug, label, descr)
            for cat, slug, label, descr in all_topics()
            if query in label.lower() or query in descr.lower()
            or query in cat.lower()
        ]
        if not matches:
            st.caption(f"Sin coincidencias para «{query}».")
        else:
            st.caption(f"{len(matches)} resultado(s):")
            n_cols = 3
            shown = matches[:30]
            for row_start in range(0, len(shown), n_cols):
                cols = st.columns(n_cols, gap="small")
                for col, (cat, slug, label, descr) in zip(
                    cols, shown[row_start:row_start + n_cols]
                ):
                    with col:
                        lesson = get_lesson(slug)
                        theme = _theme(cat)
                        dot = ('<div class="aca-complete-dot"></div>'
                               if (lesson and lesson.is_complete) else "")
                        st.markdown(
                            f'<div class="aca-topic-card-inner" '
                            f'style="--accent:{theme["accent"]};">'
                            f'{dot}'
                            f'<div style="font-size:10px;'
                            f'color:{theme["accent"]};letter-spacing:0.06em;'
                            f'text-transform:uppercase;font-weight:700;'
                            f'margin-bottom:4px;">{cat}</div>'
                            f'<div style="font-size:14px;font-weight:600;'
                            f'color:#F3F4F6;margin-bottom:4px;'
                            f'padding-right:18px;">{label}</div>'
                            f'<div style="font-size:11px;color:#94A3B8;'
                            f'line-height:1.4;min-height:32px;">{descr}</div>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )
                        if st.button("Ver lección →",
                                      key=f"search_btn_{slug}"):
                            _go_topic(slug)
                            st.rerun()
    else:
        # Category grid — 3 columns of beautiful HTML cards
        st.markdown(
            '<div class="eq-section-label" style="margin-top:6px;">'
            'EXPLORÁ POR CATEGORÍA</div>',
            unsafe_allow_html=True,
        )

        cats_list = list(CATALOG.items())
        n_cols = 3
        for row_start in range(0, len(cats_list), n_cols):
            cols = st.columns(n_cols, gap="small")
            for col, (cat, topics) in zip(
                cols, cats_list[row_start:row_start + n_cols]
            ):
                with col:
                    theme = _theme(cat)
                    sample = ", ".join(t[1] for t in topics[:3])
                    if len(topics) > 3:
                        sample += "…"
                    complete_in_cat = sum(
                        1 for slug, _, _ in topics
                        if get_lesson(slug) and get_lesson(slug).is_complete
                    )
                    st.markdown(
                        f'<div class="aca-card aca-cat-card">'
                        f'<div class="aca-glow" '
                        f'style="background:{theme["accent"]};"></div>'
                        f'<div style="display:flex;justify-content:'
                        f'space-between;align-items:baseline;'
                        f'margin-bottom:8px;position:relative;">'
                        f'<div style="font-size:18px;font-weight:700;'
                        f'color:#F3F4F6;letter-spacing:-0.01em;">{cat}</div>'
                        f'<span class="aca-pill" '
                        f'style="background:{theme["tint"]};'
                        f'color:{theme["accent"]};">{len(topics)} temas</span>'
                        f'</div>'
                        f'<div style="font-size:12px;color:#94A3B8;'
                        f'line-height:1.5;position:relative;'
                        f'margin-bottom:6px;min-height:36px;">{sample}</div>'
                        f'<div style="font-size:10px;color:#10B981;'
                        f'position:relative;font-weight:600;">'
                        f'● {complete_in_cat} lección(es) completa(s)</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    if st.button("Explorar →", key=f"cat_btn_{cat}"):
                        _go_cat(cat)
                        st.rerun()

        # Featured complete lessons
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            '<div class="eq-section-label">⭐ LECCIONES COMPLETAS · '
            'EMPEZÁ POR ACÁ</div>',
            unsafe_allow_html=True,
        )
        featured = [
            ("free_cash_flow",   "💵", "Free Cash Flow"),
            ("roic",             "📐", "ROIC vs WACC"),
            ("dcf",              "🧮", "DCF"),
            ("margin_of_safety", "🛡️", "Margin of safety"),
            ("moats",            "🏰", "Moats económicos"),
            ("earnings_quality", "🔬", "Earnings quality"),
            ("yield_curve",      "📈", "Yield curve"),
            ("inflation",        "🔥", "Inflación"),
            ("capital_allocation", "🎯", "Capital allocation"),
            ("business_cycles",  "🔄", "Business cycles"),
        ]
        n_cols = 5
        for row_start in range(0, len(featured), n_cols):
            cols = st.columns(n_cols, gap="small")
            for col, (slug, emoji, label) in zip(
                cols, featured[row_start:row_start + n_cols]
            ):
                with col:
                    t = find_topic(slug)
                    if t is None:
                        continue
                    cat = t[0]
                    descr = t[3]
                    theme = _theme(cat)
                    st.markdown(
                        f'<div class="aca-topic-card-inner" '
                        f'style="--accent:{theme["accent"]};">'
                        f'<div class="aca-complete-dot"></div>'
                        f'<div style="display:flex;align-items:baseline;'
                        f'gap:8px;margin-bottom:6px;padding-right:18px;">'
                        f'<span style="font-size:18px;">{emoji}</span>'
                        f'<span style="font-size:14px;font-weight:600;'
                        f'color:#F3F4F6;">{label}</span>'
                        f'</div>'
                        f'<div style="font-size:11px;color:#94A3B8;'
                        f'line-height:1.4;min-height:32px;">{descr}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    if st.button("Abrir →", key=f"feat_btn_{slug}"):
                        _go_topic(slug)
                        st.rerun()


# Footer
st.markdown("<br>", unsafe_allow_html=True)
st.caption(
    "Contenido escrito a mano con fuentes verificables. Las lecciones "
    "marcadas ● verde tienen las 10 secciones completas; las otras tienen "
    "stub + materiales recomendados. Sin llamadas a APIs externas — "
    "todo el contenido vive en el código."
)

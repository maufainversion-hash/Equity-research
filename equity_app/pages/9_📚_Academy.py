"""
Academy — masterclass financiera con contenido curado (sin AI).

Catálogo de 64 temas. Cada lección tiene:
- Definición escrita a mano (no generada).
- Métricas clave, señales bullish/bearish, impacto en valuación.
- Caso real / contraejemplo histórico.
- Errores comunes + mentalidad de analista.
- Libros canónicos (Graham, Damodaran, Buffett, Marks, McKinsey…).
- Videos / charlas recomendadas.
- Citas atribuidas y verificables.

Navegación: query params (?cat= · ?topic=) — sin llamadas a Gemini,
sin esperas, sin 503.
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
# Colour theme per category
# ============================================================
_CAT_THEME: dict[str, dict[str, str]] = {
    "📊 Empresas":         {"accent": "#10B981", "tint": "rgba(16,185,129,0.10)"},
    "💰 Valuación":        {"accent": "#C9A961", "tint": "rgba(201,169,97,0.10)"},
    "🏛️ Sectores":         {"accent": "#3B82F6", "tint": "rgba(59,130,246,0.10)"},
    "🌐 Macro & economía": {"accent": "#A78BFA", "tint": "rgba(167,139,250,0.10)"},
    "📈 Mercado":          {"accent": "#F59E0B", "tint": "rgba(245,158,11,0.10)"},
}

# ASCII slugs for categories — used in URLs so query params don't
# break on emoji/space URL-encoding round-trip.
_CAT_SLUGS: dict[str, str] = {
    "📊 Empresas":         "empresas",
    "💰 Valuación":        "valuacion",
    "🏛️ Sectores":         "sectores",
    "🌐 Macro & economía": "macro",
    "📈 Mercado":          "mercado",
}
_CAT_FROM_SLUG: dict[str, str] = {v: k for k, v in _CAT_SLUGS.items()}


def _theme(cat: str) -> dict[str, str]:
    return _CAT_THEME.get(cat, {"accent": "#94A3B8",
                                 "tint": "rgba(148,163,184,0.10)"})


def _cat_slug(cat: str) -> str:
    return _CAT_SLUGS.get(cat, cat)


def _cat_from_slug(slug: str) -> str | None:
    return _CAT_FROM_SLUG.get(slug)


# ============================================================
# CSS — clickable cards + lesson sections
# ============================================================
st.markdown(
    """
<style>
.aca-card {
  background:#0f172a;
  border:1px solid #334155;
  border-radius:10px;
  padding:18px 20px;
  text-decoration:none !important;
  display:block;
  transition:transform 0.15s ease, border-color 0.15s ease,
             background 0.15s ease;
}
.aca-card:hover {
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
.aca-topic-card {
  background:#0f172a;
  border:1px solid #334155;
  border-left:3px solid var(--accent, #94A3B8);
  border-radius:8px;
  padding:14px 16px;
  text-decoration:none !important;
  display:block;
  transition:transform 0.12s ease, border-color 0.15s ease;
  position:relative;
}
.aca-topic-card:hover {
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
# Query params
# ============================================================
qp = st.query_params
selected_topic = qp.get("topic")
# Category in URL is an ASCII slug; resolve to its full display name.
_cat_qp = qp.get("cat")
selected_cat = _cat_from_slug(_cat_qp) if _cat_qp else None


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


def _breadcrumb(cat: str | None, topic_label: str | None = None) -> None:
    parts = ['<a href="?" style="color:#94A3B8;text-decoration:none;">📚 Academy</a>']
    if cat:
        parts.append(
            f'<span style="color:#475569;">›</span>'
            f'<a href="?cat={_cat_slug(cat)}" style="color:#94A3B8;'
            f'text-decoration:none;">{cat}</a>'
        )
    if topic_label:
        parts.append(
            f'<span style="color:#475569;">›</span>'
            f'<span style="color:#F3F4F6;font-weight:500;">{topic_label}</span>'
        )
    st.markdown(
        '<div style="font-size:12px;margin-bottom:18px;'
        'display:flex;gap:8px;align-items:center;">'
        + " ".join(parts) + '</div>',
        unsafe_allow_html=True,
    )


# ============================================================
# Lesson render — given a complete Lesson, render all 10 sections
# ============================================================
def _render_lesson(lesson: Lesson, theme: dict[str, str]) -> None:
    accent = theme["accent"]

    # Lesson header
    completeness = ("Contenido completo" if lesson.is_complete
                    else "Contenido en desarrollo · ver fuentes recomendadas")
    completeness_color = "#10B981" if lesson.is_complete else "#F59E0B"
    st.markdown(
        f"""
<div style="background:#0f172a;border:1px solid #334155;
border-left:4px solid {accent};border-radius:8px;
padding:16px 20px;margin-bottom:18px;">
  <div style="font-size:11px;color:{accent};
letter-spacing:0.08em;text-transform:uppercase;font-weight:700;
margin-bottom:4px;">{lesson.category}</div>
  <h2 style="margin:0;font-size:22px;color:#F3F4F6;
font-weight:600;">{lesson.label}</h2>
  <div style="font-size:12px;color:#94A3B8;margin-top:4px;">{lesson.hook}</div>
  <div style="font-size:11px;color:{completeness_color};margin-top:8px;
font-weight:600;">● {completeness}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    # If the lesson is a stub, only render the resources block.
    if not lesson.is_complete:
        st.info(
            "Esta lección todavía está en redacción. Mientras tanto, "
            "los libros, charlas y citas de abajo son el material "
            "recomendado para empezar a profundizar en este tema.",
            icon="📖",
        )
    else:
        # 1. Concepto principal
        st.markdown(
            f'<div class="lesson-section">'
            f'<h3>1 · Concepto principal</h3>'
            f'<div class="lesson-body">{_md_to_html(lesson.definition)}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # 2. Por qué importa
        if lesson.why_matters:
            st.markdown(
                f'<div class="lesson-section">'
                f'<h3>2 · Por qué importa</h3>'
                f'<div class="lesson-body">{_md_to_html(lesson.why_matters)}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # 3. Cómo lo analiza un profesional
        if lesson.how_pros_analyze:
            st.markdown(
                f'<div class="lesson-section">'
                f'<h3>3 · Cómo lo analiza un profesional</h3>'
                f'<div class="lesson-body">{_md_to_html(lesson.how_pros_analyze)}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # 4. Métricas clave (tabla)
        if lesson.key_metrics:
            rows = "".join(
                f'<tr><td style="padding:8px 12px;color:#F3F4F6;'
                f'font-weight:600;width:38%;border-bottom:1px solid #1F2937;">{n}</td>'
                f'<td style="padding:8px 12px;color:#cbd5e1;'
                f'border-bottom:1px solid #1F2937;">{v}</td></tr>'
                for n, v in lesson.key_metrics
            )
            st.markdown(
                f'<div class="lesson-section">'
                f'<h3>4 · Métricas clave</h3>'
                f'<table style="width:100%;border-collapse:collapse;'
                f'font-size:13px;">{rows}</table>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # 5. Bullish vs bearish
        if lesson.bullish_vs_bearish:
            rows = "".join(
                f'<tr>'
                f'<td style="padding:8px 12px;color:#10B981;width:50%;'
                f'border-bottom:1px solid #1F2937;">✓ {b}</td>'
                f'<td style="padding:8px 12px;color:#F87171;'
                f'border-bottom:1px solid #1F2937;">✕ {br}</td>'
                f'</tr>'
                for b, br in lesson.bullish_vs_bearish
            )
            st.markdown(
                f'<div class="lesson-section">'
                f'<h3>5 · Señales bullish vs bearish</h3>'
                f'<table style="width:100%;border-collapse:collapse;'
                f'font-size:13px;">'
                f'<thead><tr>'
                f'<th style="text-align:left;padding:8px 12px;color:#10B981;'
                f'font-size:11px;letter-spacing:0.06em;text-transform:uppercase;">'
                f'Bullish</th>'
                f'<th style="text-align:left;padding:8px 12px;color:#F87171;'
                f'font-size:11px;letter-spacing:0.06em;text-transform:uppercase;">'
                f'Bearish</th>'
                f'</tr></thead>'
                f'<tbody>{rows}</tbody>'
                f'</table>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # 6. Impacto en valuación
        if lesson.valuation_impact:
            st.markdown(
                f'<div class="lesson-section">'
                f'<h3>6 · Impacto en la valuación</h3>'
                f'<div class="lesson-body">{_md_to_html(lesson.valuation_impact)}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # 7. Caso práctico
        if lesson.case_study:
            st.markdown(
                f'<div class="lesson-section">'
                f'<h3>7 · Caso práctico</h3>'
                f'<div class="lesson-body">{_md_to_html(lesson.case_study)}</div>'
                f'</div>',
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
                f'margin:0;">{items}</ul>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # 9. Mentalidad de analista
        if lesson.mental_model:
            st.markdown(
                f'<div class="lesson-section">'
                f'<h3>9 · Mentalidad de analista</h3>'
                f'<div class="lesson-body">{_md_to_html(lesson.mental_model)}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # 10. Fuentes recomendadas (libros + videos + quotes)
    if lesson.books or lesson.videos or lesson.quotes:
        st.markdown(
            '<div class="lesson-section">'
            '<h3>10 · Fuentes recomendadas</h3>',
            unsafe_allow_html=True,
        )

        if lesson.books:
            st.markdown(
                '<div style="color:#94A3B8;font-size:11px;letter-spacing:0.06em;'
                'text-transform:uppercase;margin-bottom:8px;font-weight:600;">'
                '📚 Libros</div>',
                unsafe_allow_html=True,
            )
            for b in lesson.books:
                year = f" ({b.year})" if b.year else ""
                chapter = (f'<div style="font-size:11px;color:#C9A961;'
                            f'margin-top:4px;">→ {b.chapter_hint}</div>'
                            if b.chapter_hint else "")
                why = (f'<div style="font-size:12px;color:#94A3B8;'
                        f'margin-top:6px;font-style:italic;line-height:1.5;">'
                        f'{b.why}</div>' if b.why else "")
                st.markdown(
                    f'<div class="book-card">'
                    f'<div style="font-size:14px;font-weight:600;'
                    f'color:#F3F4F6;">{b.title}</div>'
                    f'<div style="font-size:12px;color:#cbd5e1;'
                    f'margin-top:2px;">{b.author}{year}</div>'
                    f'{chapter}{why}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        if lesson.videos:
            st.markdown(
                '<div style="color:#94A3B8;font-size:11px;letter-spacing:0.06em;'
                'text-transform:uppercase;margin-top:14px;margin-bottom:8px;'
                'font-weight:600;">🎥 Videos / charlas</div>',
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
                        f'margin-top:6px;font-style:italic;line-height:1.5;">'
                        f'{v.why}</div>' if v.why else "")
                st.markdown(
                    f'<div class="video-card">'
                    f'<div style="font-size:14px;font-weight:600;'
                    f'color:#F3F4F6;">{v.title}</div>'
                    f'<div style="font-size:12px;color:#cbd5e1;'
                    f'margin-top:2px;">{v.channel}{minutes}{url_link}</div>'
                    f'{why}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        if lesson.quotes:
            st.markdown(
                '<div style="color:#94A3B8;font-size:11px;letter-spacing:0.06em;'
                'text-transform:uppercase;margin-top:14px;margin-bottom:8px;'
                'font-weight:600;">💬 Citas</div>',
                unsafe_allow_html=True,
            )
            for q in lesson.quotes:
                source = (f' <span style="color:#64748B;font-size:11px;">— '
                            f'{q.source}</span>' if q.source else "")
                st.markdown(
                    f'<div class="quote-card">'
                    f'"{q.text}"<br>'
                    f'<span style="color:#C9A961;font-size:12px;'
                    f'font-style:normal;font-weight:600;">— {q.author}</span>'
                    f'{source}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        st.markdown('</div>', unsafe_allow_html=True)


def _md_to_html(text: str) -> str:
    """Minimal markdown → HTML converter (bold + line breaks + lists)
    so the lesson sections render nicely inside our custom <div>s
    without st.markdown's own wrapping."""
    import re
    if not text:
        return ""
    # **bold** → <strong>
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Line breaks: keep paragraphs (double newline) + simple <br> for single.
    paragraphs = out.split("\n\n")
    rendered: list[str] = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        # Lists: lines starting with digit+dot or "-"
        lines = p.split("\n")
        if all(line.lstrip().startswith(("·", "-", "*")) or
               (line.lstrip()[:2] in {f"{i}." for i in range(1, 10)})
               for line in lines if line.strip()):
            items = "".join(
                f"<li style='margin-bottom:4px;'>{line.lstrip('-·*0123456789. ').strip()}</li>"
                for line in lines if line.strip()
            )
            rendered.append(
                f"<ol style='padding-left:20px;margin:6px 0;'>{items}</ol>"
            )
        else:
            rendered.append("<p style='margin:0 0 10px 0;'>"
                             + p.replace("\n", "<br>") + "</p>")
    return "".join(rendered)


# ============================================================
# State 3 — topic selected
# ============================================================
if selected_topic:
    topic = find_topic(selected_topic)
    if topic is None:
        st.error(f"Tema desconocido: `{selected_topic}`")
        st.markdown('<a href="?" style="color:#3B82F6;">← Volver</a>',
                    unsafe_allow_html=True)
    else:
        cat, _, label, descr = topic
        _breadcrumb(cat, label)
        lesson = get_lesson(selected_topic)
        if lesson is None:
            # Shouldn't happen — every catalog slug should have a Lesson.
            st.warning("Esta lección todavía no tiene contenido.")
        else:
            _render_lesson(lesson, _theme(cat))

# ============================================================
# State 2 — category selected
# ============================================================
elif selected_cat and selected_cat in CATALOG:
    theme = _theme(selected_cat)
    _breadcrumb(selected_cat)

    st.markdown(
        f"""
<div style="background:#0f172a;border:1px solid #334155;
border-left:4px solid {theme['accent']};border-radius:8px;
padding:16px 20px;margin-bottom:18px;">
  <h2 style="margin:0;font-size:20px;color:#F3F4F6;font-weight:600;">
    {selected_cat}</h2>
  <div style="font-size:12px;color:#94A3B8;margin-top:4px;">
    {len(CATALOG[selected_cat])} lecciones · ● verde = contenido
    completo · sin marca = stub con materiales recomendados
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    cards: list[str] = []
    for slug, label, descr in CATALOG[selected_cat]:
        lesson = get_lesson(slug)
        dot = '<div class="aca-complete-dot"></div>' if (
            lesson and lesson.is_complete) else ""
        cards.append(
            f'<a class="aca-topic-card" href="?topic={slug}" '
            f'style="--accent:{theme["accent"]};">{dot}'
            f'<div style="font-size:14px;font-weight:600;color:#F3F4F6;'
            f'margin-bottom:6px;padding-right:18px;">{label}</div>'
            f'<div style="font-size:11px;color:#94A3B8;line-height:1.4;">'
            f'{descr}</div>'
            f'</a>'
        )
    st.markdown(
        '<div style="display:grid;grid-template-columns:repeat('
        'auto-fill,minmax(260px,1fr));gap:12px;">'
        + "".join(cards) + '</div>',
        unsafe_allow_html=True,
    )

# ============================================================
# State 1 — landing
# ============================================================
else:
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
            cards = []
            for cat, slug, label, descr in matches[:40]:
                theme = _theme(cat)
                lesson = get_lesson(slug)
                dot = '<div class="aca-complete-dot"></div>' if (
                    lesson and lesson.is_complete) else ""
                cards.append(
                    f'<a class="aca-topic-card" href="?topic={slug}" '
                    f'style="--accent:{theme["accent"]};">{dot}'
                    f'<div style="font-size:10px;color:{theme["accent"]};'
                    f'letter-spacing:0.06em;text-transform:uppercase;'
                    f'font-weight:700;margin-bottom:4px;">{cat}</div>'
                    f'<div style="font-size:14px;font-weight:600;'
                    f'color:#F3F4F6;margin-bottom:4px;padding-right:18px;">'
                    f'{label}</div>'
                    f'<div style="font-size:11px;color:#94A3B8;'
                    f'line-height:1.4;">{descr}</div>'
                    f'</a>'
                )
            st.markdown(
                '<div style="display:grid;grid-template-columns:repeat('
                'auto-fill,minmax(260px,1fr));gap:12px;margin-top:8px;">'
                + "".join(cards) + '</div>',
                unsafe_allow_html=True,
            )
    else:
        # Category grid
        st.markdown(
            '<div class="eq-section-label" style="margin-top:6px;">'
            'EXPLORÁ POR CATEGORÍA</div>',
            unsafe_allow_html=True,
        )

        cat_cards: list[str] = []
        for cat, topics in CATALOG.items():
            theme = _theme(cat)
            sample = ", ".join(t[1] for t in topics[:3])
            if len(topics) > 3:
                sample += "…"
            complete_in_cat = sum(
                1 for slug, _, _ in topics
                if get_lesson(slug) and get_lesson(slug).is_complete
            )
            cat_cards.append(
                f'<a class="aca-card aca-cat-card" href="?cat={_cat_slug(cat)}">'
                f'<div class="aca-glow" style="background:{theme["accent"]};"></div>'
                f'<div style="display:flex;justify-content:space-between;'
                f'align-items:baseline;margin-bottom:8px;position:relative;">'
                f'<div style="font-size:18px;font-weight:700;color:#F3F4F6;'
                f'letter-spacing:-0.01em;">{cat}</div>'
                f'<span class="aca-pill" style="background:{theme["tint"]};'
                f'color:{theme["accent"]};">{len(topics)} temas</span>'
                f'</div>'
                f'<div style="font-size:12px;color:#94A3B8;line-height:1.5;'
                f'position:relative;margin-bottom:6px;">{sample}</div>'
                f'<div style="font-size:10px;color:#10B981;'
                f'position:relative;font-weight:600;">'
                f'● {complete_in_cat} lección(es) completa(s)</div>'
                f'</a>'
            )
        st.markdown(
            '<div style="display:grid;grid-template-columns:repeat('
            'auto-fill,minmax(280px,1fr));gap:14px;margin-top:8px;'
            'margin-bottom:28px;">'
            + "".join(cat_cards) + '</div>',
            unsafe_allow_html=True,
        )

        # Featured complete topics
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
        feat_cards: list[str] = []
        for slug, emoji, label in featured:
            t = find_topic(slug)
            if t is None:
                continue
            cat, _, _, descr = t
            theme = _theme(cat)
            feat_cards.append(
                f'<a class="aca-topic-card" href="?topic={slug}" '
                f'style="--accent:{theme["accent"]};">'
                f'<div class="aca-complete-dot"></div>'
                f'<div style="display:flex;align-items:baseline;gap:8px;'
                f'margin-bottom:6px;padding-right:18px;">'
                f'<span style="font-size:18px;">{emoji}</span>'
                f'<span style="font-size:14px;font-weight:600;'
                f'color:#F3F4F6;">{label}</span>'
                f'</div>'
                f'<div style="font-size:11px;color:#94A3B8;line-height:1.4;">'
                f'{descr}</div>'
                f'</a>'
            )
        st.markdown(
            '<div style="display:grid;grid-template-columns:repeat('
            'auto-fill,minmax(220px,1fr));gap:10px;margin-top:8px;">'
            + "".join(feat_cards) + '</div>',
            unsafe_allow_html=True,
        )


# Footer
st.markdown("<br>", unsafe_allow_html=True)
st.caption(
    "Contenido escrito a mano con fuentes verificables. Las lecciones "
    "marcadas ● verde tienen las 10 secciones completas; las otras tienen "
    "stub + materiales recomendados. Sin llamadas a APIs externas — "
    "todo el contenido vive en el código."
)

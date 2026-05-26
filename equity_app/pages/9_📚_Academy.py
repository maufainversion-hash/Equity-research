"""
Academy — masterclass financiera con Gemini, navegada vía query params.

Layout en 3 estados (selector vía ``?topic=`` / ``?cat=``):

1. Landing (sin params) — hero + cards de categorías grandes +
   featured topics.
2. Categoría seleccionada (``?cat=...``) — header con breadcrumb +
   grid de topics de esa categoría.
3. Topic seleccionado (``?topic=...``) — la lección generada por
   Gemini + breadcrumb arriba.

Click en cualquier card es un <a> que setea query params; Streamlit
re-renderiza sin necesidad de st.button (que no permite styling).
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
# Colour theme per category — gives the page a clear visual map
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


# ============================================================
# Inject inline CSS for card hover + clickable anchors
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
.aca-cat-card {
  position:relative;
  overflow:hidden;
}
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
}
.aca-topic-card:hover {
  border-color:#64748B;
  border-left-color:var(--accent-hover, #94A3B8);
  transform:translateX(2px);
}
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# Query params — single source of truth for navigation
# ============================================================
qp = st.query_params
selected_topic = qp.get("topic")
selected_cat = qp.get("cat")


# ============================================================
# Hero header
# ============================================================
n_topics = sum(len(v) for v in CATALOG.values())
st.markdown(
    f"""
<div style="background:linear-gradient(135deg,#0b1220 0%,#131826 100%);
border:1px solid #334155;border-radius:12px;padding:24px 28px;
margin-bottom:24px;position:relative;overflow:hidden;">
  <div style="position:absolute;top:-40px;right:-40px;width:200px;
height:200px;border-radius:50%;background:radial-gradient(circle,
rgba(201,169,97,0.18) 0%,transparent 70%);"></div>
  <div style="display:flex;align-items:baseline;gap:14px;
margin-bottom:8px;">
    <h1 style="margin:0;font-size:30px;font-weight:700;color:#F3F4F6;
letter-spacing:-0.02em;">Academy</h1>
    <span style="color:#C9A961;font-size:11px;letter-spacing:0.1em;
text-transform:uppercase;font-weight:600;">
      Masterclass financiera · AI-powered
    </span>
  </div>
  <div style="color:#cbd5e1;font-size:14px;line-height:1.55;max-width:760px;">
    Lecciones nivel research institucional generadas con Gemini.
    Cada tema en 10 secciones — concepto, métricas, señales, impacto
    en valuación, caso práctico, errores comunes y mentalidad de
    analista. Pensado para aprender a <b style="color:#F3F4F6;">pensar
    como un buy-side / sell-side</b>, no memorizar fórmulas.
  </div>
  <div style="display:flex;gap:28px;margin-top:16px;
border-top:1px solid #1F2937;padding-top:14px;">
    <div>
      <div style="font-size:22px;font-weight:700;color:#F3F4F6;
font-variant-numeric:tabular-nums;">{n_topics}</div>
      <div style="font-size:10px;color:#94A3B8;letter-spacing:0.08em;
text-transform:uppercase;">temas</div>
    </div>
    <div>
      <div style="font-size:22px;font-weight:700;color:#F3F4F6;
font-variant-numeric:tabular-nums;">{len(CATALOG)}</div>
      <div style="font-size:10px;color:#94A3B8;letter-spacing:0.08em;
text-transform:uppercase;">categorías</div>
    </div>
    <div>
      <div style="font-size:22px;font-weight:700;color:#F3F4F6;
font-variant-numeric:tabular-nums;">10</div>
      <div style="font-size:10px;color:#94A3B8;letter-spacing:0.08em;
text-transform:uppercase;">secciones / lección</div>
    </div>
    <div>
      <div style="font-size:22px;font-weight:700;color:#10B981;
font-variant-numeric:tabular-nums;">24h</div>
      <div style="font-size:10px;color:#94A3B8;letter-spacing:0.08em;
text-transform:uppercase;">cache</div>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)


# ============================================================
# Breadcrumb (only when navigated into cat/topic)
# ============================================================
def _breadcrumb(cat: str | None, topic_label: str | None = None) -> None:
    parts = ['<a href="?" style="color:#94A3B8;text-decoration:none;">📚 Academy</a>']
    if cat:
        parts.append(
            f'<span style="color:#475569;">›</span>'
            f'<a href="?cat={cat}" style="color:#94A3B8;'
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
# State 3: topic selected → render lesson
# ============================================================
if selected_topic:
    topic = find_topic(selected_topic)
    if topic is None:
        st.error(f"Tema desconocido: `{selected_topic}`")
        st.markdown('<a href="?" style="color:#3B82F6;">← Volver</a>',
                    unsafe_allow_html=True)
    else:
        cat, _, label, descr = topic
        theme = _theme(cat)
        _breadcrumb(cat, label)

        # Lesson header card
        st.markdown(
            f"""
<div style="background:#0f172a;border:1px solid #334155;
border-left:4px solid {theme['accent']};border-radius:8px;
padding:16px 20px;margin-bottom:18px;">
  <div style="display:flex;justify-content:space-between;
align-items:baseline;">
    <div>
      <div style="font-size:11px;color:{theme['accent']};
letter-spacing:0.08em;text-transform:uppercase;font-weight:700;
margin-bottom:4px;">{cat}</div>
      <h2 style="margin:0;font-size:20px;color:#F3F4F6;
font-weight:600;">{label}</h2>
      <div style="font-size:12px;color:#94A3B8;margin-top:4px;">{descr}</div>
    </div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

        col_a, col_b = st.columns([6, 1])
        with col_b:
            if st.button("🔁 Regenerar", key=f"regen_{selected_topic}",
                          width="stretch",
                          help="Limpia el cache de esta lección y "
                               "vuelve a llamar a Gemini para una "
                               "nueva versión"):
                generate_lesson.clear()
                st.rerun()

        with st.spinner("Generando masterclass…"):
            lesson_md = generate_lesson(selected_topic)

        if lesson_md.startswith("⚠️"):
            st.warning(lesson_md, icon="⚠️")
        else:
            st.markdown(lesson_md)

        st.markdown("---")
        st.caption(
            f"Tema: **{label}** · Generado por Gemini · Cacheado 24h. "
            f"Si querés otra perspectiva, usá 🔁 Regenerar."
        )

# ============================================================
# State 2: category selected → grid of topic cards
# ============================================================
elif selected_cat and selected_cat in CATALOG:
    theme = _theme(selected_cat)
    _breadcrumb(selected_cat)

    # Cat hero strip
    st.markdown(
        f"""
<div style="background:#0f172a;border:1px solid #334155;
border-left:4px solid {theme['accent']};border-radius:8px;
padding:16px 20px;margin-bottom:18px;">
  <h2 style="margin:0;font-size:20px;color:#F3F4F6;
font-weight:600;">{selected_cat}</h2>
  <div style="font-size:12px;color:#94A3B8;margin-top:4px;">
    {len(CATALOG[selected_cat])} lecciones disponibles · click en
    cualquier card para generar la masterclass
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    # Topic cards grid (auto-fill)
    cards: list[str] = []
    for slug, label, descr in CATALOG[selected_cat]:
        cards.append(
            f'<a class="aca-topic-card" href="?topic={slug}" '
            f'style="--accent:{theme["accent"]};--accent-hover:{theme["accent"]};">'
            f'<div style="font-size:14px;font-weight:600;color:#F3F4F6;'
            f'margin-bottom:6px;">{label}</div>'
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
# State 1: landing — category grid + featured + search
# ============================================================
else:
    # Inline search (works on the landing only — cat/topic pages have
    # the back-link in the breadcrumb instead).
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
                cards.append(
                    f'<a class="aca-topic-card" href="?topic={slug}" '
                    f'style="--accent:{theme["accent"]};">'
                    f'<div style="font-size:10px;color:{theme["accent"]};'
                    f'letter-spacing:0.06em;text-transform:uppercase;'
                    f'font-weight:700;margin-bottom:4px;">{cat}</div>'
                    f'<div style="font-size:14px;font-weight:600;'
                    f'color:#F3F4F6;margin-bottom:4px;">{label}</div>'
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
        # Category big-card grid — visual map of the catalog
        st.markdown(
            '<div class="eq-section-label" style="margin-top:6px;">'
            'EXPLORÁ POR CATEGORÍA</div>',
            unsafe_allow_html=True,
        )

        cat_cards: list[str] = []
        for cat, topics in CATALOG.items():
            theme = _theme(cat)
            # Sample 3 hooks to preview the depth
            sample = ", ".join(t[1] for t in topics[:3])
            if len(topics) > 3:
                sample += "…"
            cat_cards.append(
                f'<a class="aca-card aca-cat-card" href="?cat={cat}">'
                f'<div class="aca-glow" style="background:{theme["accent"]};"></div>'
                f'<div style="display:flex;justify-content:space-between;'
                f'align-items:baseline;margin-bottom:8px;position:relative;">'
                f'<div style="font-size:18px;font-weight:700;color:#F3F4F6;'
                f'letter-spacing:-0.01em;">{cat}</div>'
                f'<span class="aca-pill" style="background:{theme["tint"]};'
                f'color:{theme["accent"]};">{len(topics)} temas</span>'
                f'</div>'
                f'<div style="font-size:12px;color:#94A3B8;line-height:1.5;'
                f'position:relative;">{sample}</div>'
                f'</a>'
            )
        st.markdown(
            '<div style="display:grid;grid-template-columns:repeat('
            'auto-fill,minmax(280px,1fr));gap:14px;margin-top:8px;'
            'margin-bottom:28px;">'
            + "".join(cat_cards) + '</div>',
            unsafe_allow_html=True,
        )

        # Featured topics — quick start
        st.markdown(
            '<div class="eq-section-label">⭐ SUGERIDOS PARA EMPEZAR</div>',
            unsafe_allow_html=True,
        )
        featured = [
            ("free_cash_flow",   "💵", "Free Cash Flow"),
            ("roic",             "📐", "ROIC vs WACC"),
            ("dcf",              "🧮", "DCF"),
            ("margin_of_safety", "🛡️", "Margin of safety"),
            ("moats",            "🏰", "Moats económicos"),
            ("yield_curve",      "📈", "Yield curve"),
            ("inflation",        "🔥", "Inflación"),
            ("market_regimes",   "🌐", "Market regimes"),
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
                f'<div style="display:flex;align-items:baseline;gap:8px;'
                f'margin-bottom:6px;">'
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
    "Lecciones cacheadas 24h por tema · cada llamada a Gemini cuenta "
    "en la página API Usage. Free tier ~250 req/día — con cache "
    "incluso 10 lecciones nuevas por día son ~10 calls."
)

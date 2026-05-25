"""
Earnings-quality flags card — Beneish M-Score · Piotroski F-Score · Sloan ratio.

Wraps the existing :mod:`analysis.earnings_quality` output into a
compact 3-card row, one chip per signal. Each chip carries the
score, a colour flag (green / yellow / red) and a one-line
explanation pulled straight from the analyser. The row closes
with an overall verdict derived from worst-of the three.

The card stays silent (renders nothing) when the analyser couldn't
compute any of the three signals — typically a thin-data ticker
where balance / cash flow are missing.
"""
from __future__ import annotations
from typing import Optional

import streamlit as st


_FLAG_COLORS: dict[str, tuple[str, str]] = {
    # (bg, fg) — bg is alpha-suffixed so the card blends with the panel.
    "green":   ("#10B98122", "#10B981"),
    "yellow":  ("#F59E0B22", "#FBBF24"),
    "red":     ("#EF444422", "#F87171"),
    "unknown": ("#33415522", "#94A3B8"),
}
_FLAG_LABEL: dict[str, str] = {
    "green":   "LIMPIO",
    "yellow":  "ATENCIÓN",
    "red":     "RIESGO",
    "unknown": "S/D",
}


def _chip_html(flag: str, label: str) -> str:
    bg, fg = _FLAG_COLORS.get(flag, _FLAG_COLORS["unknown"])
    txt = _FLAG_LABEL.get(flag, label)
    return (
        f'<span style="display:inline-block;padding:3px 10px;'
        f'border-radius:4px;background:{bg};color:{fg};'
        f'font-size:10px;font-weight:700;letter-spacing:0.08em;">'
        f'{txt}</span>'
    )


def _card(name: str, subtitle: str, score: str, flag: str,
          explanation: str) -> str:
    bg, fg = _FLAG_COLORS.get(flag, _FLAG_COLORS["unknown"])
    return (
        f'<div style="background:#0f172a;border:1px solid #334155;'
        f'border-left:3px solid {fg};border-radius:8px;'
        f'padding:14px 16px;">'
        f'<div style="display:flex;justify-content:space-between;'
        f'align-items:center;margin-bottom:6px;">'
        f'<div style="font-size:12px;font-weight:600;color:#E8EAED;'
        f'letter-spacing:0.05em;text-transform:uppercase;">{name}</div>'
        f'{_chip_html(flag, "?")}</div>'
        f'<div style="font-size:11px;color:#94A3B8;margin-bottom:8px;">'
        f'{subtitle}</div>'
        f'<div style="font-size:18px;font-weight:700;color:{fg};'
        f'font-variant-numeric:tabular-nums;margin-bottom:4px;">{score}</div>'
        f'<div style="font-size:11px;color:#94A3B8;line-height:1.4;">'
        f'{explanation}</div>'
        f'</div>'
    )


def render_quality_flags_card(eq) -> None:
    """Render the 3-flag earnings-quality row.

    ``eq`` is the :class:`analysis.earnings_quality.EarningsQuality`
    dataclass. Renders nothing when None or when all three signals
    are missing."""
    if eq is None:
        return

    flags = [
        ("Beneish M-Score", "Manipulación de earnings", eq.beneish),
        ("Piotroski F-Score", "Solidez fundamental (0-9)", eq.piotroski),
        ("Sloan Ratio", "Calidad de earnings (acruales)", eq.sloan),
    ]

    # Skip the section entirely when nothing landed.
    if not any(f for _, _, f in flags):
        return

    st.markdown(
        '<div class="eq-section-label">QUALITY FLAGS · EARNINGS</div>',
        unsafe_allow_html=True,
    )

    cards: list[str] = []
    for name, subtitle, flag_obj in flags:
        if flag_obj is None:
            cards.append(_card(name, subtitle, "—", "unknown",
                               "Datos insuficientes para computar."))
            continue
        # Format the score: M-Score and Sloan are decimals; Piotroski is 0-9.
        score_val = flag_obj.score
        if name.startswith("Piotroski"):
            score_txt = f"{int(score_val)}/9"
        elif name.startswith("Sloan"):
            score_txt = f"{score_val:+.2%}"
        else:
            score_txt = f"{score_val:+.2f}"
        cards.append(_card(
            name, subtitle, score_txt,
            flag_obj.flag, flag_obj.explanation,
        ))

    st.markdown(
        '<div style="display:grid;grid-template-columns:repeat(3,1fr);'
        'gap:12px;margin-top:6px;">'
        + "".join(cards)
        + '</div>',
        unsafe_allow_html=True,
    )

    # Overall verdict line
    overall = eq.overall_flag
    overall_msg = {
        "green":   "Veredicto global: **earnings limpios**. Los tres "
                   "tests no detectan señales de manipulación ni de baja "
                   "calidad contable.",
        "yellow":  "Veredicto global: **atención**. Al menos un test "
                   "muestra señal moderada — monitorear próximos "
                   "trimestres.",
        "red":     "Veredicto global: **riesgo de earnings quality**. Al "
                   "menos un test entra en zona roja — revisar el detalle "
                   "antes de descontar los earnings reportados.",
        "unknown": "Veredicto global: datos insuficientes para evaluar.",
    }.get(overall, "")
    bg, fg = _FLAG_COLORS.get(overall, _FLAG_COLORS["unknown"])
    if overall_msg:
        st.markdown(
            f'<div style="margin-top:10px;padding:10px 14px;'
            f'background:{bg};border-left:3px solid {fg};'
            f'border-radius:0 6px 6px 0;font-size:12px;color:#E8EAED;'
            f'line-height:1.5;">{overall_msg}</div>',
            unsafe_allow_html=True,
        )

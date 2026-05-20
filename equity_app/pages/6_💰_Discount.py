"""
Discount — screener of stocks trading below their intrinsic value.

Reads the precomputed snapshot (``data/discount_snapshot.json``, built
by ``scripts/build_discount_snapshot.py``) and lists companies whose
combined intrinsic value exceeds market price — quick buy ideas grouped
by market and industry. Zero API calls when the page loads; each row
expands to show ratios and a valuation summary.
"""
from __future__ import annotations
from datetime import datetime

import streamlit as st

from data.discount_data import load_snapshot

# ============================================================
# Display constants
# ============================================================
_VERDICT_MD = {            # colour the verdict label in markdown
    "STRONG BUY":  ":green[**STRONG BUY**]",
    "BUY":         ":green[**BUY**]",
    "HOLD":        ":orange[HOLD]",
    "SELL":        ":red[SELL]",
    "STRONG SELL": ":red[**STRONG SELL**]",
}
_REGION_ORDER = ("North America", "Europe", "Asia", "Latin America")

# Credible discount: intrinsic above price but capped at +100%. A larger
# upside is almost always a data artefact (share count, intl banks on
# noisy book values), not a real opportunity.
_MAX_CREDIBLE_UPSIDE = 100.0


# ============================================================
# Formatters  ($ is escaped in markdown context — an unescaped pair
# of '$' triggers Streamlit's LaTeX render)
# ============================================================
def _usd_plain(v) -> str:
    """``US$1,234.56`` — for st.metric (plain text, no markdown)."""
    try:
        return f"US${float(v):,.2f}"
    except (TypeError, ValueError):
        return "—"


def _usd_md(v) -> str:
    """``US\\$1,234.56`` — for markdown / expander labels."""
    try:
        return f"US\\${float(v):,.2f}"
    except (TypeError, ValueError):
        return "—"


def _big(v) -> str:
    """Abbreviated currency — US$1.23 B / 456 M."""
    try:
        f = float(v)
    except (TypeError, ValueError):
        return "—"
    a = abs(f)
    if a >= 1e12:
        return f"US${f / 1e12:,.2f} T"
    if a >= 1e9:
        return f"US${f / 1e9:,.1f} B"
    if a >= 1e6:
        return f"US${f / 1e6:,.0f} M"
    return f"US${f:,.0f}"


def _pct(v, *, signed: bool = False) -> str:
    try:
        f = float(v)
        return f"{f:+,.1f}%" if signed else f"{f:,.1f}%"
    except (TypeError, ValueError):
        return "—"


def _num(v, suffix: str = "") -> str:
    try:
        return f"{float(v):,.2f}{suffix}"
    except (TypeError, ValueError):
        return "—"


# ============================================================
# Style — card-shaped expanders + mini stat cards
# ============================================================
st.markdown("""
<style>
div[data-testid="stExpander"] details {
    border: 1px solid var(--border, #2A2E39);
    border-radius: 10px;
    background: var(--surface, #14171F);
    margin-bottom: 7px;
    transition: border-color .15s ease;
}
div[data-testid="stExpander"] details:hover {
    border-color: var(--accent, #9A7B33);
}
div[data-testid="stExpander"] summary { padding: 4px 6px; }
.dx-stat {
    background: var(--surface, #14171F);
    border: 1px solid var(--border, #2A2E39);
    border-radius: 12px; padding: 14px 16px; height: 100%;
}
.dx-stat .lab {
    font-size: 11px; letter-spacing:.06em; text-transform:uppercase;
    color: var(--text-muted, #8A8F9C);
}
.dx-stat .val {
    font-size: 24px; font-weight: 600; margin-top: 4px;
    color: var(--text-primary, #E8EAED);
}
.dx-stat .sub { font-size: 12px; color: var(--text-secondary, #B4B8C0); }
</style>
""", unsafe_allow_html=True)


def _stat(label: str, value: str, sub: str = "") -> str:
    return (f'<div class="dx-stat"><div class="lab">{label}</div>'
            f'<div class="val">{value}</div>'
            f'<div class="sub">{sub}</div></div>')


# ============================================================
# Load the snapshot
# ============================================================
st.markdown(
    '<div class="eq-section-label" style="color:var(--accent);">'
    'BUY IDEAS</div>',
    unsafe_allow_html=True,
)
st.title("💰 Stocks at a Discount")

snap = load_snapshot()
companies = snap.get("companies", []) if snap else []

if not companies:
    st.warning(
        "No valuation snapshot yet. Build it by running:\n\n"
        "```\npython scripts/build_discount_snapshot.py\n```\n\n"
        "The script values the whole catalog once and writes the "
        "result; this page then just reads it — no API calls."
    )
    st.stop()

gen = snap.get("generated_utc", "")
try:
    when = datetime.fromisoformat(gen).strftime("%d %b %Y %H:%M UTC")
except Exception:
    when = gen or "—"

n_total = len(companies)
discounted_all = [c for c in companies
                  if 0 < (c.get("upside_pct") or 0) <= _MAX_CREDIBLE_UPSIDE]

# ---- Summary ----
if discounted_all:
    best = max(discounted_all, key=lambda c: c.get("upside_pct") or 0)
    avg = sum(c["upside_pct"] for c in discounted_all) / len(discounted_all)
else:
    best, avg = None, 0.0

s1, s2, s3, s4 = st.columns(4)
s1.markdown(_stat("Companies analyzed", str(n_total),
                  f"snapshot {when}"), unsafe_allow_html=True)
s2.markdown(_stat("At a discount", str(len(discounted_all)),
                  "intrinsic &gt; price"), unsafe_allow_html=True)
s3.markdown(_stat("Average discount", _pct(avg, signed=True),
                  "of the cheap ones"), unsafe_allow_html=True)
s4.markdown(_stat("Best opportunity",
                  best["ticker"] if best else "—",
                  _pct(best["upside_pct"], signed=True) if best else ""),
            unsafe_allow_html=True)
st.write("")

# ============================================================
# Refresh the snapshot — runs the builder on demand
# ============================================================
if st.session_state.pop("_discount_refreshed", None):
    st.toast("Valuation snapshot refreshed ✓")

with st.expander("🔄 Refresh data"):
    st.caption(
        "Re-values the whole catalog with fresh prices and statements. "
        "Takes several minutes and makes hundreds of API calls — run "
        "this only when you want the data refreshed."
    )
    if st.button("Refresh snapshot now", key="discount_refresh"):
        from analysis.discount_builder import build_snapshot
        bar = st.progress(0.0, text="Starting…")

        def _prog(done: int, total: int, msg: str) -> None:
            bar.progress(done / total, text=f"[{done}/{total}]  {msg}")

        with st.spinner("Valuing the catalog… (don't close the page)"):
            res = build_snapshot(progress=_prog)
        bar.progress(1.0, text="Done")
        st.session_state["_discount_refreshed"] = True
        st.success(
            f"{res['ok']} valued · {res['discounted']} at a discount · "
            f"{res['skipped']} skipped (high inflation) · "
            f"{res['fail']} no data."
        )
        st.rerun()

# ============================================================
# Filters
# ============================================================
f1, f2, f3 = st.columns([1.4, 1.6, 2.0])
with f1:
    regions_present = [r for r in _REGION_ORDER
                       if any(c.get("region") == r for c in companies)]
    region_opts = ["All markets"] + regions_present
    region_pick = st.selectbox("Market", region_opts)
with f2:
    if region_pick == "All markets":
        pool = companies
    else:
        pool = [c for c in companies if c.get("region") == region_pick]
    sectors_present = sorted({c.get("sector", "—") for c in pool})
    sector_pick = st.selectbox("Industry",
                               ["All industries"] + sectors_present)
with f3:
    min_upside = st.slider(
        "Minimum discount (upside %)", 0, 60, 0, step=5,
        help="Only show companies whose intrinsic value exceeds the "
             "price by at least this much.")

rows = list(discounted_all)
if region_pick != "All markets":
    rows = [c for c in rows if c.get("region") == region_pick]
if sector_pick != "All industries":
    rows = [c for c in rows if c.get("sector") == sector_pick]
rows = [c for c in rows if (c.get("upside_pct") or 0) >= min_upside]
rows.sort(key=lambda c: c.get("upside_pct") or 0, reverse=True)

if not rows:
    st.info("No companies match the current filters. "
            "Try lowering the minimum discount or changing market.")
    st.stop()

st.markdown(f"**{len(rows)}** companies at a discount with the current filters.")


# ============================================================
# Render — grouped by market and industry
# ============================================================
def _kv_rows(pairs: list[tuple[str, str]]) -> str:
    """Compact key-value list for the card body."""
    out = []
    for k, v in pairs:
        out.append(
            "<div style='display:flex;justify-content:space-between;"
            "border-bottom:1px solid var(--border,#2A2E39);"
            "padding:3px 0;font-size:13px;'>"
            f"<span style='color:var(--text-muted,#8A8F9C);'>{k}</span>"
            f"<span style='font-weight:500;'>{v}</span></div>")
    return "".join(out)


def _render_company(c: dict) -> None:
    """One expandable card: headline + ratios + valuation snapshot."""
    up = c.get("upside_pct")
    verdict = c.get("verdict", "—") or "—"
    verdict_md = _VERDICT_MD.get(verdict, verdict)
    label = (
        f"**{c.get('ticker','—')}**  ·  {c.get('name','')}　"
        f"{_usd_md(c.get('price'))} → {_usd_md(c.get('intrinsic'))}　"
        f":green[**▲ {_pct(up, signed=True)}**]　{verdict_md}"
    )
    with st.expander(label):
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Market price", _usd_plain(c.get("price")))
        m2.metric("Intrinsic value", _usd_plain(c.get("intrinsic")),
                  delta=_pct(up, signed=True))
        m3.metric("Verdict", verdict)
        m4.metric("P/E", _num(c.get("pe")) if c.get("pe") else "—")

        col_r, col_v = st.columns(2)
        with col_r:
            st.markdown("**Financial ratios**")
            ratios = c.get("ratios", {}) or {}
            if ratios:
                pairs = [(k, _pct(v) if k.endswith("%") else _num(v, "×"))
                         for k, v in ratios.items()]
                st.markdown(_kv_rows(pairs), unsafe_allow_html=True)
            else:
                st.caption("Ratios unavailable.")
        with col_v:
            st.markdown("**Valuation (quick look)**")
            val = c.get("valuation", {}) or {}
            disp = val.get("dispersion_pct")
            pairs = [
                ("DCF / share", _usd_md(val.get("dcf"))),
                ("Multiples / share", _usd_md(val.get("multiples"))),
                ("EPV / share", _usd_md(val.get("epv"))),
                ("Combined intrinsic", _usd_md(c.get("intrinsic"))),
                ("Market cap", _big(c.get("market_cap")).replace("$", "\\$")),
                ("Models used", str(val.get("n_models") or "—")),
                ("Model dispersion",
                 _pct(disp) if disp is not None else "—"),
                ("WACC", _pct(c.get("wacc_pct"))),
            ]
            st.markdown(_kv_rows(pairs), unsafe_allow_html=True)
        st.caption(
            f"{c.get('country','')} · {c.get('sector','')} — quick view; "
            f"for the full analysis, search the ticker in Equity analysis.")


for region in _REGION_ORDER:
    region_rows = [c for c in rows if c.get("region") == region]
    if not region_rows:
        continue
    st.markdown(
        f"<div style='margin-top:18px;font-size:20px;font-weight:600;"
        f"color:var(--text-primary,#E8EAED);border-left:3px solid "
        f"var(--accent,#9A7B33);padding-left:10px;'>"
        f"{region}</div>",
        unsafe_allow_html=True)
    sectors_in_region = sorted({c.get("sector", "—") for c in region_rows})
    for sec in sectors_in_region:
        sec_rows = [c for c in region_rows if c.get("sector") == sec]
        sec_rows.sort(key=lambda c: c.get("upside_pct") or 0, reverse=True)
        st.markdown(
            f"<div class='eq-section-label' style='margin-top:12px;'>"
            f"{sec} · {len(sec_rows)}</div>", unsafe_allow_html=True)
        for c in sec_rows:
            _render_company(c)

st.divider()
st.caption(
    "Intrinsic value combines DCF, two-stage intrinsic multiples, EPV "
    "and other models. Only discounts up to +100% are listed: a larger "
    "upside is almost always data noise, not an opportunity. A discount "
    "is NOT a guarantee of return — it's a starting point for further "
    "research with the full analysis. Not investment advice.")

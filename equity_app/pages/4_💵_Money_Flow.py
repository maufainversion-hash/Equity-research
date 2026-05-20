"""
Money Flow — where does investor money go?

A company's market capitalization IS the money investors have parked
in it. This page aggregates the catalog by market and industry to show
where that capital is concentrated: which companies and which
industries hold the bulk of the money.

Reads the precomputed snapshot (``data/discount_snapshot.json``) — no
API calls. Refresh via ``scripts/build_discount_snapshot.py`` or the
button on the Discount page.
"""
from __future__ import annotations
from datetime import datetime

import streamlit as st
import plotly.graph_objects as go

from data.discount_data import load_snapshot

# ============================================================
# Constants
# ============================================================
_REGION_ORDER = ("North America", "Europe", "Asia", "Latin America")
_CHART_BG = "#0B0E14"
_ACCENT = "#9A7B33"


def _big(v) -> str:
    """Abbreviated currency — US$1.23 T / 456 B / 12 M."""
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


# ============================================================
# Style
# ============================================================
st.markdown("""
<style>
.mf-stat {
    background: var(--surface, #14171F);
    border: 1px solid var(--border, #2A2E39);
    border-radius: 12px; padding: 14px 16px; height: 100%;
}
.mf-stat .lab {
    font-size: 11px; letter-spacing:.06em; text-transform:uppercase;
    color: var(--text-muted, #8A8F9C);
}
.mf-stat .val {
    font-size: 23px; font-weight: 600; margin-top: 4px;
    color: var(--text-primary, #E8EAED);
}
.mf-stat .sub { font-size: 12px; color: var(--text-secondary, #B4B8C0); }
</style>
""", unsafe_allow_html=True)


def _stat(label: str, value: str, sub: str = "") -> str:
    return (f'<div class="mf-stat"><div class="lab">{label}</div>'
            f'<div class="val">{value}</div>'
            f'<div class="sub">{sub}</div></div>')


# ============================================================
# Header + load
# ============================================================
st.markdown(
    '<div class="eq-section-label" style="color:var(--accent);">'
    'CAPITAL FLOW</div>',
    unsafe_allow_html=True,
)
st.title("💵 Where the money goes")

snap = load_snapshot()
companies = [c for c in (snap.get("companies", []) if snap else [])
             if c.get("market_cap") and float(c["market_cap"]) > 0]

if not companies:
    st.warning(
        "The snapshot has no market-cap data yet. Rebuild it with:\n\n"
        "```\npython scripts/build_discount_snapshot.py\n```\n\n"
        "The script values the catalog and stores market cap, price "
        "and ratios; this page just reads that file."
    )
    st.stop()

gen = snap.get("generated_utc", "")
try:
    when = datetime.fromisoformat(gen).strftime("%d %b %Y")
except Exception:
    when = gen or "—"

st.caption(
    "Market cap is the money investors have parked in each company. "
    "Below is where that capital is concentrated — by company and by "
    f"industry. Snapshot from {when}."
)

# ---- Market selector ----
regions_present = [r for r in _REGION_ORDER
                   if any(c.get("region") == r for c in companies)]
opts = ["All markets"] + regions_present
# Default: North America if available — usual focus.
default_idx = (opts.index("North America") if "North America" in opts else 0)
market = st.selectbox("Market", opts, index=default_idx)

if market == "All markets":
    rows = list(companies)
else:
    rows = [c for c in companies if c.get("region") == market]

rows.sort(key=lambda c: float(c["market_cap"]), reverse=True)
total_cap = sum(float(c["market_cap"]) for c in rows)

# ============================================================
# Summary
# ============================================================
by_sector: dict[str, float] = {}
for c in rows:
    by_sector[c["sector"]] = by_sector.get(c["sector"], 0.0) + float(c["market_cap"])
top_sector = max(by_sector, key=by_sector.get) if by_sector else "—"
top10_share = (sum(float(c["market_cap"]) for c in rows[:10]) / total_cap * 100.0
               if total_cap else 0.0)

s1, s2, s3, s4 = st.columns(4)
s1.markdown(_stat("Total capital", _big(total_cap),
                  f"{len(rows)} companies"), unsafe_allow_html=True)
s2.markdown(_stat("Largest company",
                  rows[0]["ticker"] if rows else "—",
                  _big(rows[0]["market_cap"]) if rows else ""),
            unsafe_allow_html=True)
s3.markdown(_stat("Leading industry", top_sector,
                  f"{by_sector.get(top_sector, 0)/total_cap*100:,.0f}% of capital"
                  if total_cap else ""), unsafe_allow_html=True)
s4.markdown(_stat("Top-10 concentration", f"{top10_share:,.0f}%",
                  "of capital in 10 companies"), unsafe_allow_html=True)
st.write("")

# ============================================================
# Treemap — money by industry and company
# ============================================================
st.markdown("#### Capital map — industry → company")
st.caption("Each rectangle is a company sized by its market cap. The "
           "big blocks are where the money is parked.")

sector_names = list(by_sector.keys())
labels = sector_names + [c["ticker"] for c in rows]
parents = [""] * len(sector_names) + [c["sector"] for c in rows]
values = [by_sector[s] for s in sector_names] + [
    float(c["market_cap"]) for c in rows]
hover = ["" for _ in sector_names] + [c.get("name", "") for c in rows]

fig = go.Figure(go.Treemap(
    labels=labels, parents=parents, values=values,
    branchvalues="total",
    text=hover,
    texttemplate="<b>%{label}</b><br>%{value:$.3s}",
    hovertemplate="<b>%{label}</b> %{text}<br>%{value:$.4s}"
                  "<br>%{percentRoot:.1%} of market<extra></extra>",
    marker=dict(
        colors=values,
        colorscale=[[0, "#1A1D27"], [0.5, "#5C5230"], [1, _ACCENT]],
        line=dict(color=_CHART_BG, width=1.5),
    ),
    tiling=dict(pad=2),
    pathbar=dict(visible=True),
))
fig.update_layout(
    height=460, margin=dict(t=10, l=0, r=0, b=0),
    paper_bgcolor=_CHART_BG, plot_bgcolor=_CHART_BG,
    font=dict(color="#E8EAED"),
)
st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

# ============================================================
# Sector concentration
# ============================================================
st.markdown("#### Capital by industry")
sec_sorted = sorted(by_sector.items(), key=lambda kv: kv[1], reverse=True)
bar = go.Figure(go.Bar(
    x=[v / total_cap * 100.0 for _, v in sec_sorted],
    y=[s for s, _ in sec_sorted],
    orientation="h",
    marker=dict(color=_ACCENT),
    text=[f"{v/total_cap*100:,.1f}%" for _, v in sec_sorted],
    textposition="outside",
    hovertemplate="%{y}<br>%{customdata}<br>%{x:.1f}% of market"
                  "<extra></extra>",
    customdata=[_big(v) for _, v in sec_sorted],
))
bar.update_layout(
    height=max(240, 34 * len(sec_sorted)),
    margin=dict(t=10, l=0, r=40, b=10),
    paper_bgcolor=_CHART_BG, plot_bgcolor=_CHART_BG,
    font=dict(color="#E8EAED"),
    xaxis=dict(title="% of market capital", showgrid=False),
    yaxis=dict(autorange="reversed"),
)
st.plotly_chart(bar, width="stretch", config={"displayModeBar": False})

# ============================================================
# Top holdings — where the most money is invested
# ============================================================
st.markdown("#### Companies with the most invested capital")
import pandas as pd

table = pd.DataFrame([
    {
        "Ticker":     c["ticker"],
        "Company":    c.get("name", ""),
        "Industry":   c.get("sector", ""),
        "Country":    c.get("country", ""),
        "Market cap": _big(c["market_cap"]),
        "Weight":     f"{float(c['market_cap'])/total_cap*100:,.2f}%",
    }
    for c in rows[:20]
])
st.dataframe(table, width="stretch", hide_index=True)

st.divider()
st.caption(
    "Market cap = price × shares outstanding: the value the market "
    "assigns to a company, and therefore the money investors have "
    "parked in it. The concentration in a few mega-caps is a "
    "structural feature of cap-weighted indices.")

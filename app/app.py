"""
Dynamic Alignment Observatory
Who votes with whom — and how that's changing.
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.data_loader import load_anchor_scores, load_bloc_summaries, load_actors, load_dyad_scores
from utils.plots import world_map_tilt, bloc_cohesion_chart, bloc_tilt_chart, diplomacy_vs_trade_scatter, COLORS
from utils.text import CAVEAT_BOX

st.set_page_config(
    page_title="Dynamic Alignment Observatory",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Load data ──
anchor = load_anchor_scores()
bloc = load_bloc_summaries()
dyad = load_dyad_scores()
latest_year = int(anchor["year"].max())

# ── Header ──
st.title("Dynamic Alignment Observatory")
st.markdown("**Who votes with whom — and how that's changing.**")
n_countries = anchor["country"].nunique() + 2  # +2 for USA and CHN (anchor states)
st.markdown(
    f"*Tracking diplomatic alignment across {n_countries} countries using "
    f"UN General Assembly voting patterns ({int(anchor['year'].min())}–{latest_year}).*"
)

# ── Sidebar ──
with st.sidebar:
    st.header("Settings")
    map_year = st.slider("Map year", int(anchor["year"].min()), latest_year, latest_year)
    st.markdown("---")
    st.markdown("**Navigate**")
    st.page_link("pages/1_Country_Explorer.py", label="🔍 Country Explorer")
    st.page_link("pages/2_Dyad_Comparison.py", label="↔️ Compare Two Countries")
    st.page_link("pages/3_Bloc_Dashboard.py", label="🏛️ Bloc Dashboard")
    st.page_link("pages/4_Alignment_Space.py", label="🗺️ Diplomatic Alignment Space")
    st.page_link("pages/5_Methodology.py", label="📖 Methodology & Caveats")
    st.markdown("---")
    st.caption(f"Data through {latest_year} UNGA session.")
    st.caption("Minhas (MSU) × CSIS")

# ── World Map ──
map_metric = st.selectbox(
    "Map metric",
    ["Diplomatic alignment (UNGA voting)", "Trade dependence (bilateral trade)"],
    index=0,
)

if map_metric == "Trade dependence (bilateral trade)" and "trade_US_minus_China" in anchor.columns:
    _trade_anchor = anchor.copy()
    _trade_years = _trade_anchor.loc[_trade_anchor["trade_US_minus_China"].notna(), "year"]
    _trade_map_year = map_year
    if _trade_years[_trade_years <= map_year].empty:
        _trade_map_year = int(_trade_years.max()) if len(_trade_years) > 0 else map_year
    else:
        _trade_map_year = int(_trade_years[_trade_years <= map_year].max())
    _trade_anchor["US_minus_China"] = _trade_anchor["trade_US_minus_China"]
    fig_map = world_map_tilt(_trade_anchor, _trade_map_year)
    fig_map.update_layout(title=f"Trade Dependence: US vs China ({_trade_map_year})")
    fig_map.update_layout(coloraxis_colorbar=dict(
        title="Trade balance",
        tickvals=[-0.8, -0.4, 0, 0.4, 0.8],
        ticktext=["← China", "", "Balanced", "", "US →"],
    ))
    st.plotly_chart(fig_map, use_container_width=True)
    st.caption(f"Showing trade data for {_trade_map_year}. Color = share of trade with US minus share with China.")
else:
    st.plotly_chart(world_map_tilt(anchor, map_year), use_container_width=True)

# ── Headline metrics ──
col1, col2, col3, col4 = st.columns(4)

bloc_latest = bloc[bloc["year"] == latest_year]


def _bloc_metric(bloc_name):
    row = bloc_latest[bloc_latest["bloc"] == bloc_name]
    if len(row) == 0:
        return None, None
    val = row.iloc[0]["within_cohesion"]
    prev = bloc[(bloc["bloc"] == bloc_name) & (bloc["year"] == latest_year - 5)]
    if len(prev) > 0:
        delta = val - prev.iloc[0]["within_cohesion"]
        return val, delta
    return val, None


for col, bloc_name in zip([col1, col2, col3, col4], ["G7", "BRICS", "NATO", "Global South"]):
    val, delta = _bloc_metric(bloc_name)
    if val is not None:
        col.metric(
            f"{bloc_name} Cohesion",
            f"{val:.2f}",
            f"{delta:+.3f} vs 5yr ago" if delta is not None else None,
            help=f"Mean pairwise diplomatic alignment among {bloc_name} members (0–1 scale). "
                 f"Higher = members vote more similarly at the UNGA.",
        )

# ── Caveat ──
with st.expander("⚠️ What this measures — read before exploring", expanded=False):
    st.markdown(CAVEAT_BOX)
    st.markdown(
        "**Note on the map colors:** Most countries appear red (China-tilted) because "
        "the US frequently votes in small minorities at the UNGA. This doesn't mean "
        "most countries are Chinese allies — it means their diplomatic *positions* on "
        "UN issues differ from the US more than from China. The map is most informative "
        "for comparing *relative* positions and tracking *changes* over time."
    )

# ── Bloc charts ──
st.markdown("---")
col_left, col_right = st.columns(2)
with col_left:
    st.plotly_chart(bloc_cohesion_chart(bloc), use_container_width=True)
with col_right:
    st.plotly_chart(bloc_tilt_chart(bloc), use_container_width=True)

# ── Diplomacy vs Trade scatter ──
if "trade_share_US" in anchor.columns:
    st.markdown("---")
    st.plotly_chart(diplomacy_vs_trade_scatter(anchor, latest_year), use_container_width=True)
    st.caption(
        "Countries on the dashed diagonal are consistent — their diplomatic alignment "
        "and trade dependence point the same direction. Countries off the diagonal show "
        "a divergence: they vote one way at the UNGA but trade in the other direction. "
        "Trade data from IMF Direction of Trade Statistics and World Bank WITS."
    )

# ── Key takeaways (computed from data) ──
st.markdown("---")
st.subheader(f"Key Takeaways ({latest_year})")

# Helper to safely get bloc cohesion
def _get_cohesion(bloc_name, year):
    row = bloc[(bloc["bloc"] == bloc_name) & (bloc["year"] == year)]
    return row.iloc[0]["within_cohesion"] if len(row) > 0 else None

def _get_dyad_alignment(c1, c2, year, df=dyad):
    row = df[((df["iso3_1"]==c1)&(df["iso3_2"]==c2)) | ((df["iso3_1"]==c2)&(df["iso3_2"]==c1))]
    row = row[row["year"] == year]
    return row.iloc[0]["structural_alignment"] if len(row) > 0 else None

def _get_tilt(country, year):
    row = anchor[(anchor["country"]==country) & (anchor["year"]==year)]
    return row.iloc[0]["US_minus_China"] if len(row) > 0 else None

min_year = int(anchor["year"].min())

# Compute all numbers from actual data
brics_early = _get_cohesion("BRICS", min_year)
brics_late = _get_cohesion("BRICS", latest_year)
g7_late = _get_cohesion("G7", latest_year)

cnrus_early = _get_dyad_alignment("CHN", "RUS", min_year)
cnrus_late = _get_dyad_alignment("CHN", "RUS", latest_year)
usgbr_late = _get_dyad_alignment("USA", "GBR", latest_year)

kor_us_early = _get_dyad_alignment("USA", "KOR", min_year)
kor_us_late = _get_dyad_alignment("USA", "KOR", latest_year)

takeaways = []

if brics_early and brics_late and g7_late:
    takeaways.append(
        f"**BRICS is converging on G7-level diplomatic cohesion.** "
        f"BRICS within-group diplomatic alignment rose from {brics_early:.2f} ({min_year}) to "
        f"{brics_late:.2f} ({latest_year}), nearly matching G7's {g7_late:.2f}."
    )

if cnrus_early and cnrus_late and usgbr_late:
    takeaways.append(
        f"**China-Russia diplomatic convergence has been steady.** "
        f"Their diplomatic alignment score rose from {cnrus_early:.2f} ({min_year}) to "
        f"{cnrus_late:.2f} ({latest_year}), approaching the US-UK level of {usgbr_late:.2f}."
    )

if kor_us_early and kor_us_late:
    takeaways.append(
        f"**South Korea is one of the biggest movers toward US positions** — "
        f"diplomatic alignment with the US rose from {kor_us_early:.2f} ({min_year}) to "
        f"{kor_us_late:.2f} ({latest_year})."
    )

ukr_tilt_2000 = _get_tilt("UKR", 2000)
ukr_tilt_latest = _get_tilt("UKR", latest_year)
kaz_tilt_2000 = _get_tilt("KAZ", 2000)
kaz_tilt_latest = _get_tilt("KAZ", latest_year)
if ukr_tilt_2000 is not None and ukr_tilt_latest is not None and kaz_tilt_2000 is not None and kaz_tilt_latest is not None:
    ukr_shift = ukr_tilt_latest - ukr_tilt_2000
    kaz_shift = kaz_tilt_latest - kaz_tilt_2000
    takeaways.append(
        f"**Ukraine and Kazakhstan are mirror-image movers.** "
        f"Ukraine shifted {ukr_shift:+.2f} toward the US since 2000; Kazakhstan shifted "
        f"{kaz_shift:+.2f} toward China over the same period."
    )

takeaways.append(
    "**India votes with the Global South, not with the US** — even as "
    "US-India security ties deepen. This reflects shared positions "
    "on sovereignty and development, not strategic alignment with Beijing."
)

# Trade divergence takeaway
if "trade_share_US" in anchor.columns:
    trade_yr = anchor.loc[anchor["trade_share_US"].notna() & (anchor["trade_share_US"] > 0), "year"]
    if len(trade_yr) > 0:
        lt = int(trade_yr.max())
        tdf = anchor[(anchor["year"] == lt) & (anchor["trade_share_US"].notna()) & (anchor["trade_share_US"] > 0)]
        n_div = int(((tdf["US_minus_China"] > 0) != (tdf["trade_US_minus_China"] > 0)).sum())
        aus = tdf[tdf["country"] == "AUS"]
        if n_div > 0 and len(aus) > 0:
            a = aus.iloc[0]
            takeaways.append(
                f"**Diplomacy and trade often point in different directions.** "
                f"{n_div} countries show a divergence between how they vote and where they trade "
                f"({lt}). Australia votes with the US (tilt {a['US_minus_China']:+.2f}) but sends "
                f"{a['trade_share_China']:.0%} of its trade to China versus "
                f"{a['trade_share_US']:.0%} to the US."
            )

for t in takeaways:
    st.markdown(f"- {t}")

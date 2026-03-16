"""Country Explorer — full alignment profile for any country."""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import (
    load_anchor_scores, load_dyad_scores, load_actors,
    get_country_list, get_country_name,
)
from utils.plots import country_trajectory, tilt_trajectory, COLORS
from utils.text import CAVEAT_BOX, format_alignment_description, format_tilt_description

st.set_page_config(page_title="Country Explorer", page_icon="🔍", layout="wide")
st.title("🔍 Country Explorer")

# ── Load data ──
anchor = load_anchor_scores()
dyad = load_dyad_scores()
actors = load_actors()
countries = get_country_list()

# ── Country selector ──
country_labels = [c[0] for c in countries]
country_codes = [c[1] for c in countries]

selected_label = st.selectbox(
    "Select a country",
    country_labels,
    index=country_labels.index("South Korea (KOR)") if "South Korea (KOR)" in country_labels else 0,
)
selected_iso3 = country_codes[country_labels.index(selected_label)]
selected_name = get_country_name(selected_iso3, actors)

latest_year = int(anchor["year"].max())
latest = anchor[(anchor["country"] == selected_iso3) & (anchor["year"] == latest_year)]

if selected_iso3 in ("USA", "CHN"):
    st.info(
        f"{selected_name} is used as an **anchor state** in this analysis. "
        f"All other countries' alignment is measured relative to the US and China, "
        f"so {selected_name} does not have its own tilt score. "
        f"Use the **Dyad Comparison** tab to see {selected_name}'s alignment with any other country."
    )
    # Still show dyad-level data
    st.markdown(f"## {selected_name}")
    st.markdown(f"### Who is most aligned with {selected_name}? ({latest_year})")
    dyad_latest = dyad[dyad["year"] == latest_year]
    country_dyads = dyad_latest[
        (dyad_latest["iso3_1"] == selected_iso3) | (dyad_latest["iso3_2"] == selected_iso3)
    ].copy()
    country_dyads["partner"] = country_dyads.apply(
        lambda r: r["iso3_2"] if r["iso3_1"] == selected_iso3 else r["iso3_1"], axis=1
    )
    country_dyads["partner_name"] = country_dyads.apply(
        lambda r: r["name_2"] if r["iso3_1"] == selected_iso3 else r["name_1"], axis=1
    )
    col_most, col_least = st.columns(2)
    with col_most:
        st.markdown("**Most aligned**")
        top = country_dyads.nlargest(10, "structural_alignment")[
            ["partner_name", "structural_alignment"]].reset_index(drop=True)
        top.columns = ["Country", "Alignment"]
        top.index = top.index + 1
        st.dataframe(top.style.format({"Alignment": "{:.3f}"}), use_container_width=True)
    with col_least:
        st.markdown("**Least aligned**")
        bottom = country_dyads.nsmallest(10, "structural_alignment")[
            ["partner_name", "structural_alignment"]].reset_index(drop=True)
        bottom.columns = ["Country", "Alignment"]
        bottom.index = bottom.index + 1
        st.dataframe(bottom.style.format({"Alignment": "{:.3f}"}), use_container_width=True)
    st.stop()

if len(latest) == 0:
    st.warning(f"No data available for {selected_name} in {latest_year}.")
    st.stop()

latest = latest.iloc[0]

# ── Profile header ──
st.markdown(f"## {selected_name}")

col1, col2, col3 = st.columns(3)
col1.metric("Alignment with US", f"{latest['alignment_with_US']:.2f}",
            help="0 = very distant, 1 = very close to US diplomatic positions")
col2.metric("Alignment with China", f"{latest['alignment_with_China']:.2f}",
            help="0 = very distant, 1 = very close to China's diplomatic positions")
col3.metric("US-China Tilt", f"{latest['US_minus_China']:+.2f}",
            help="Positive = closer to US, negative = closer to China")

col4, col5, col6 = st.columns(3)
col4.metric("Alignment with G7", f"{latest['alignment_with_G7']:.2f}",
            help="Mean diplomatic alignment with G7 members (0–1)")
col5.metric("Alignment with BRICS", f"{latest['alignment_with_BRICS']:.2f}",
            help="Mean diplomatic alignment with BRICS members (0–1)")
g7_brics_tilt = latest.get("G7_minus_BRICS", None)
if g7_brics_tilt is not None and pd.notna(g7_brics_tilt):
    col6.metric("G7-BRICS Tilt", f"{g7_brics_tilt:+.2f}",
                help="Positive = closer to G7, negative = closer to BRICS")

# Trade coupling (if available)
has_trade = "trade_coupling_US" in latest.index and pd.notna(latest.get("trade_coupling_US"))
if has_trade:
    col7, col8, col9 = st.columns(3)
    col7.metric("Trade Coupling with US", f"{latest['trade_coupling_US']:.2f}",
                help="How closely linked via bilateral trade to the US (0–1)")
    col8.metric("Trade Coupling with China", f"{latest['trade_coupling_China']:.2f}",
                help="How closely linked via bilateral trade to China (0–1)")
    trade_tilt = latest.get("trade_US_minus_China", None)
    if trade_tilt is not None and pd.notna(trade_tilt):
        col9.metric("Trade US-China Tilt", f"{trade_tilt:+.2f}",
                    help="Positive = more trade-coupled with US, negative = with China")

tilt_desc = format_tilt_description(latest["US_minus_China"])
st.markdown(f"**{latest_year} assessment:** {tilt_desc}")

# Flag where diplomacy and trade diverge
if has_trade:
    diplo_us = latest["alignment_with_US"]
    trade_us = latest["trade_coupling_US"]
    gap = diplo_us - trade_us
    if abs(gap) > 0.2:
        if gap > 0:
            st.info(
                f"**Diplomacy-trade gap:** {selected_name} is diplomatically closer to the US "
                f"(alignment {diplo_us:.2f}) than its trade patterns suggest (coupling {trade_us:.2f}). "
                f"This may indicate a country whose economic relationships lag behind its diplomatic repositioning."
            )
        else:
            st.info(
                f"**Diplomacy-trade gap:** {selected_name} is more economically coupled with the US "
                f"(trade coupling {trade_us:.2f}) than its diplomatic positions suggest (alignment {diplo_us:.2f}). "
                f"This country trades heavily with the US-led economic order while voting differently at the UNGA."
            )

# ── Trajectory charts ──
col_left, col_right = st.columns(2)
with col_left:
    st.plotly_chart(
        country_trajectory(anchor, selected_iso3, selected_name),
        use_container_width=True,
    )
with col_right:
    st.plotly_chart(
        tilt_trajectory(anchor, selected_iso3, selected_name),
        use_container_width=True,
    )

# ── Change over time ──
st.markdown("### How has alignment changed?")
col_a, col_b = st.columns(2)

# Compute change from earliest to latest
earliest = anchor[(anchor["country"] == selected_iso3)].sort_values("year").iloc[0]
with col_a:
    delta_us = latest["alignment_with_US"] - earliest["alignment_with_US"]
    st.metric(
        f"Change in US alignment ({int(earliest['year'])}→{latest_year})",
        f"{latest['alignment_with_US']:.2f}",
        f"{delta_us:+.3f}",
    )
with col_b:
    delta_cn = latest["alignment_with_China"] - earliest["alignment_with_China"]
    st.metric(
        f"Change in China alignment ({int(earliest['year'])}→{latest_year})",
        f"{latest['alignment_with_China']:.2f}",
        f"{delta_cn:+.3f}",
    )

# ── Most and least aligned ──
st.markdown(f"### Who is {selected_name} most aligned with? ({latest_year})")

dyad_latest = dyad[dyad["year"] == latest_year]
country_dyads = dyad_latest[
    (dyad_latest["iso3_1"] == selected_iso3) | (dyad_latest["iso3_2"] == selected_iso3)
].copy()
country_dyads["partner"] = country_dyads.apply(
    lambda r: r["iso3_2"] if r["iso3_1"] == selected_iso3 else r["iso3_1"], axis=1
)
country_dyads["partner_name"] = country_dyads.apply(
    lambda r: r["name_2"] if r["iso3_1"] == selected_iso3 else r["name_1"], axis=1
)

col_most, col_least = st.columns(2)
with col_most:
    st.markdown("**Most aligned**")
    top = country_dyads.nlargest(10, "structural_alignment")[
        ["partner_name", "structural_alignment"]
    ].reset_index(drop=True)
    top.columns = ["Country", "Alignment"]
    top.index = top.index + 1
    st.dataframe(top.style.format({"Alignment": "{:.3f}"}), use_container_width=True)

with col_least:
    st.markdown("**Least aligned**")
    bottom = country_dyads.nsmallest(10, "structural_alignment")[
        ["partner_name", "structural_alignment"]
    ].reset_index(drop=True)
    bottom.columns = ["Country", "Alignment"]
    bottom.index = bottom.index + 1
    st.dataframe(bottom.style.format({"Alignment": "{:.3f}"}), use_container_width=True)

# ── Group memberships ──
groups_row = latest
memberships = []
if groups_row.get("g7"):
    memberships.append("G7")
if groups_row.get("brics_original"):
    memberships.append("BRICS")
if groups_row.get("nato"):
    memberships.append("NATO")
if groups_row.get("asean"):
    memberships.append("ASEAN")
if groups_row.get("oecd"):
    memberships.append("OECD")
if groups_row.get("global_south"):
    memberships.append("Global South")

if memberships:
    st.markdown(f"**Group memberships:** {' · '.join(memberships)}")

# ── Caveat ──
with st.expander("⚠️ Important caveats"):
    st.markdown(CAVEAT_BOX)

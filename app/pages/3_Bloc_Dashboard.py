"""Bloc Dashboard — group-level alignment trends."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import (
    load_anchor_scores, load_bloc_summaries, load_group_membership, load_actors,
)
from utils.plots import (
    bloc_cohesion_chart, bloc_tilt_chart, country_trajectory, COLORS, BLOC_COLORS,
)
from utils.text import CAVEAT_BOX

st.set_page_config(page_title="Bloc Dashboard", page_icon="", layout="wide")
st.title("Bloc Dashboard")

# ── Load data ──
anchor = load_anchor_scores()
bloc = load_bloc_summaries()
groups = load_group_membership()
actors = load_actors()
latest_year = int(anchor["year"].max())

# ── Bloc selector ──
bloc_options = {
    "G7": {"col": "g7", "desc": "Canada, France, Germany, Italy, Japan, UK, USA", "bloc_key": "G7"},
    "BRICS": {"col": "brics_original", "desc": "Brazil, Russia, India, China, South Africa", "bloc_key": "BRICS"},
    "BRICS+": {"col": "brics_plus", "desc": "BRICS + Egypt, Ethiopia, Iran, Saudi Arabia, UAE", "bloc_key": "BRICS"},
    "NATO": {"col": "nato", "desc": "32-member military alliance", "bloc_key": "NATO"},
    "ASEAN": {"col": "asean", "desc": "10 Southeast Asian nations", "bloc_key": "ASEAN"},
    "Global South": {"col": "global_south", "desc": "Non-OECD developing countries", "bloc_key": "Global South"},
}

selected_bloc = st.selectbox("Select a bloc", list(bloc_options.keys()), index=0)
bloc_info = bloc_options[selected_bloc]
st.markdown(f"*{bloc_info['desc']}*")

# ── Get bloc members ──
bloc_col = bloc_info["col"]
members = groups[groups[bloc_col] == True]["iso3"].tolist()
member_names = []
for iso3 in sorted(members):
    row = actors[actors["iso3"] == iso3]
    name = row.iloc[0]["name_common"] if len(row) > 0 else iso3
    member_names.append(f"{name} ({iso3})")

# Filter to members actually in our data
members_in_data = [m for m in members if m in set(anchor["country"].unique()) | {"USA", "CHN"}]
st.markdown(f"**Members in data ({len(members_in_data)} of {len(members)}):** {', '.join(sorted(member_names))}")
if len(members_in_data) < len(members):
    st.caption(f"Note: {len(members) - len(members_in_data)} {selected_bloc} member(s) "
               f"are not in the current dataset.")

# ── Overview charts ──
st.markdown("---")
col_left, col_right = st.columns(2)

with col_left:
    st.plotly_chart(bloc_cohesion_chart(bloc), use_container_width=True)

with col_right:
    st.plotly_chart(bloc_tilt_chart(bloc), use_container_width=True)

# ── Individual member trajectories ──
st.markdown("---")
st.subheader(f"{selected_bloc} Member Diplomatic Alignment with US vs China")

# Filter anchor data to bloc members
bloc_anchor = anchor[anchor["country"].isin(members)].copy()
# anchor already has name_common; only merge if missing
if "name_common" not in bloc_anchor.columns:
    bloc_anchor = bloc_anchor.merge(
        actors[["iso3", "name_common"]], left_on="country", right_on="iso3", how="left"
    )
elif "name_common_x" in bloc_anchor.columns:
    bloc_anchor = bloc_anchor.rename(columns={"name_common_x": "name_common"})
    bloc_anchor = bloc_anchor.drop(columns=["name_common_y"], errors="ignore")

# Small multiples: tilt trajectory for each member
fig = go.Figure()
for iso3 in sorted(members):
    df = bloc_anchor[bloc_anchor["country"] == iso3].sort_values("year")
    name = df["name_common"].iloc[0] if len(df) > 0 and "name_common" in df.columns else iso3
    if len(df) > 0:
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["US_minus_China"],
            name=name, mode="lines", line=dict(width=1.5),
        ))

fig.add_hline(y=0, line_dash="dash", line_color="#999999")
fig.update_layout(
    title=f"{selected_bloc} Members: Voting Closer to US or China?",
    xaxis_title=None,
    yaxis_title="← Votes more like China · Votes more like US →",
    height=500,
    legend=dict(orientation="h", yanchor="top", y=-0.1, font=dict(size=10)),
    hovermode="x unified",
)
st.plotly_chart(fig, use_container_width=True)

# ── Snapshot table ──
st.markdown(f"### {selected_bloc} Diplomatic Alignment & Trade Dependence Snapshot ({latest_year})")
snap_cols = ["name_common", "country", "alignment_with_US", "alignment_with_China", "US_minus_China"]
# Add G7/BRICS alignment if columns exist
has_g7_brics = "alignment_with_G7" in bloc_anchor.columns
if has_g7_brics:
    snap_cols.extend(["alignment_with_G7", "alignment_with_BRICS", "G7_minus_BRICS"])
# Add trade if available
has_trade = "trade_share_US" in bloc_anchor.columns
if has_trade:
    snap_cols.extend(["trade_share_US", "trade_share_China", "trade_US_minus_China"])

snapshot = bloc_anchor[bloc_anchor["year"] == latest_year][snap_cols].sort_values(
    "US_minus_China", ascending=False
).reset_index(drop=True)

col_names = {"name_common": "Country", "country": "ISO3",
             "alignment_with_US": "Diplo. with US", "alignment_with_China": "Diplo. with China",
             "US_minus_China": "Diplo. Tilt",
             "alignment_with_G7": "Diplo. with G7", "alignment_with_BRICS": "Diplo. with BRICS",
             "G7_minus_BRICS": "G7-BRICS Tilt",
             "trade_share_US": "Trade w/ US", "trade_share_China": "Trade w/ China",
             "trade_US_minus_China": "Trade Tilt"}
snapshot = snapshot.rename(columns=col_names)
snapshot.index = snapshot.index + 1

fmt = {"Diplo. with US": "{:.3f}", "Diplo. with China": "{:.3f}", "Diplo. Tilt": "{:+.3f}"}
if has_g7_brics:
    fmt.update({"Diplo. with G7": "{:.3f}", "Diplo. with BRICS": "{:.3f}", "G7-BRICS Tilt": "{:+.3f}"})
if has_trade:
    fmt.update({"Trade w/ US": "{:.1%}", "Trade w/ China": "{:.1%}", "Trade Tilt": "{:+.1%}"})

st.dataframe(
    snapshot.style.format(fmt).background_gradient(
        subset=["Diplo. Tilt"], cmap="RdBu", vmin=-1, vmax=1),
    use_container_width=True,
)

# ── How to read ──
with st.expander("How to read this page"):
    st.markdown("""
**Cohesion chart**: Shows how similarly bloc members vote with each other
over time. Higher values mean the group acts as a more unified diplomatic
bloc. A value of 0.90 means the average pair within the group votes very
similarly.

**Tilt chart**: Shows whether the bloc as a whole votes more like the US
(positive) or more like China (negative). The dashed line at zero means
equidistant.

**Member chart**: Each line is one country's tilt over time, so you can see
which members are pulling the bloc in different directions.

**Snapshot table**: The most recent year's scores for every member, including
both diplomatic alignment and trade dependence where available. The
"Diplo. Tilt" column is color-coded: blue = votes more like the US, red =
votes more like China.
""")

# ── Caveat ──
with st.expander("Important caveats"):
    st.markdown(CAVEAT_BOX)

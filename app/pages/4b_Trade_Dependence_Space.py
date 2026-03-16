"""Trade Dependence Space — where countries sit based on who they trade with."""

import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import load_anchor_scores, load_group_membership
from utils.text import CAVEAT_BOX
import plotly.graph_objects as go

st.set_page_config(page_title="Trade Dependence Space", page_icon="", layout="wide")
st.title("The Trade Dependence Space")

st.markdown(
    "Each dot is a country positioned by its trade relationships. "
    "The **horizontal axis** shows trade dependence on the US versus China "
    "(right = more trade with US, left = more with China). "
    "The **vertical axis** shows trade dependence on the G7 versus BRICS "
    "(top = more trade with G7, bottom = more with BRICS). "
    "Use the slider to watch trade patterns shift over time."
)

# ── Load data ──
anchor = load_anchor_scores()
groups = load_group_membership()

# Find years with trade data
trade_years = sorted(anchor.loc[
    anchor["trade_share_US"].notna() & (anchor["trade_share_US"] > 0), "year"
].unique())

if len(trade_years) == 0:
    st.warning("No trade data available.")
    st.stop()

min_yr = int(min(trade_years))
max_yr = int(max(trade_years))

# ── Controls ──
year = st.slider("Year", min_yr, max_yr, max_yr, step=1)

# ── Build scatter ──
df = anchor[(anchor["year"] == year)].copy()
df = df.dropna(subset=["trade_share_US", "trade_share_China",
                        "trade_share_G7", "trade_share_BRICS"])

if len(df) == 0:
    st.warning(f"No trade data for {year}.")
    st.stop()

df["group_label"] = "Other"
df.loc[df["g7"] == True, "group_label"] = "G7"
df.loc[df["brics_original"] == True, "group_label"] = "BRICS"
df.loc[(df["global_south"] == True) & (df["group_label"] == "Other"), "group_label"] = "Global South"

color_map = {"G7": "#2166AC", "BRICS": "#B2182B",
             "Global South": "#1B7837", "Other": "#AAAAAA"}

fig = go.Figure()

# Quadrant lines
fig.add_hline(y=0, line_dash="dash", line_color="#EEEEEE")
fig.add_vline(x=0, line_dash="dash", line_color="#EEEEEE")

# Quadrant labels
fig.add_annotation(x=0.45, y=0.45, text="Trades with US & G7",
                   showarrow=False, font=dict(size=10, color="#BBBBBB"))
fig.add_annotation(x=-0.45, y=0.45, text="Trades with China & G7",
                   showarrow=False, font=dict(size=10, color="#BBBBBB"))
fig.add_annotation(x=0.45, y=-0.45, text="Trades with US & BRICS",
                   showarrow=False, font=dict(size=10, color="#BBBBBB"))
fig.add_annotation(x=-0.45, y=-0.45, text="Trades with China & BRICS",
                   showarrow=False, font=dict(size=10, color="#BBBBBB"))

for group_name in ["G7", "BRICS", "Global South", "Other"]:
    gdf = df[df["group_label"] == group_name]
    if len(gdf) == 0:
        continue
    fig.add_trace(go.Scatter(
        x=gdf["trade_US_minus_China"].tolist(),
        y=gdf["trade_G7_minus_BRICS"].tolist(),
        mode="markers",
        marker=dict(
            size=9,
            color=color_map.get(group_name, "#AAAAAA"),
            opacity=0.7,
            line=dict(width=0.5, color="white"),
        ),
        name=group_name,
        text=gdf["name_common"].tolist(),
        customdata=np.stack([
            gdf["country"].values,
            gdf["trade_share_US"].values,
            gdf["trade_share_China"].values,
            gdf["trade_share_G7"].values,
            gdf["trade_share_BRICS"].values,
        ], axis=-1),
        hovertemplate=(
            "<b>%{text}</b><br>"
            "%{customdata[0]}<br>"
            "Trade with US: %{customdata[1]:.1%}<br>"
            "Trade with China: %{customdata[2]:.1%}<br>"
            "Trade with G7: %{customdata[3]:.1%}<br>"
            "Trade with BRICS: %{customdata[4]:.1%}"
            "<extra></extra>"
        ),
    ))

# Key country labels
key_labels = ["USA", "GBR", "JPN", "DEU", "CAN", "MEX", "AUS", "KOR",
              "CHN", "RUS", "BRA", "IND", "SAU", "TUR", "VNM", "PRK",
              "CUB", "ZAF", "NGA", "IDN", "IRN"]
for _, row in df[df["country"].isin(key_labels)].iterrows():
    fig.add_annotation(
        x=row["trade_US_minus_China"], y=row["trade_G7_minus_BRICS"],
        text=row["country"], showarrow=False,
        font=dict(size=8, color="#333333"), yshift=10,
    )

fig.update_layout(
    title=dict(text=f"Trade Dependence Space ({year})", y=0.98),
    xaxis=dict(
        title="← More trade with China · More trade with US →",
        zeroline=True, zerolinecolor="#EEEEEE",
        range=[-1.05, 1.05],
    ),
    yaxis=dict(
        title="← More trade with BRICS · More trade with G7 →",
        zeroline=True, zerolinecolor="#EEEEEE",
        range=[-0.7, 0.7],
    ),
    height=650, margin=dict(t=100, l=60, r=20, b=60),
    legend=dict(orientation="h", yanchor="bottom", y=1.08, x=0.5, xanchor="center"),
    plot_bgcolor="white",
)

st.plotly_chart(fig, use_container_width=True)

# ── How to read ──
with st.expander("How to read this chart"):
    st.markdown("""
**What you're looking at:** Each country is positioned by where it trades.
The horizontal axis shows whether a country trades more with the US (right)
or China (left). The vertical axis shows whether it trades more with G7
countries (top) or BRICS countries (bottom).

**Quadrants:**
- **Top-right**: Trades predominantly with the US and G7 (e.g., Canada, Mexico)
- **Bottom-left**: Trades predominantly with China and BRICS (e.g., North Korea)
- **Top-left**: Trades more with China than the US, but more with G7 overall (e.g., many European and Asian economies that trade with both)
- **Bottom-right**: Trades more with the US than China, but more with BRICS overall (uncommon)

**What to look for:**
- **Clusters** reveal trade blocs
- **Movement over time** shows how trade dependence shifts (use the year slider)
- **Compare with the Diplomatic Alignment Space** — countries in different positions on the two maps show a diplomacy-trade divergence
""")

# ── Caveat ──
with st.expander("Important caveats"):
    st.markdown(CAVEAT_BOX)
    st.markdown(
        "**Note:** Trade shares are computed from bilateral trade flows "
        "(IMF Direction of Trade Statistics, 1990-2020; World Bank WITS, "
        "2021-2023). They reflect goods trade only and do not include "
        "services, investment, or financial flows."
    )

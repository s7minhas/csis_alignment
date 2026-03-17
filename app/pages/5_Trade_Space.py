"""Trade Space — circular layout of directed trade latent positions."""

import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import load_trade_latent_positions, load_group_membership
from utils.plots import trade_latent_space_scatter
from utils.text import CAVEAT_BOX

st.set_page_config(page_title="Trade Space", page_icon="", layout="wide")
st.title("Trade Alignment Space")

st.markdown(
    "Each country appears twice: once as an **exporter** "
    "(outer ring, triangles) and once as an **importer** (inner ring, circles). "
    "Countries with similar export profiles cluster together on the outer ring; "
    "countries with similar import profiles cluster together on the inner ring. "
    "**Node size** reflects how distinctive a country's trade pattern is. "
    "Use the slider to watch trade positions shift over time."
)

# load data
trade_latent = load_trade_latent_positions()
groups = load_group_membership()

if trade_latent is None or len(trade_latent) == 0:
    st.warning(
        "No trade latent position data available. "
        "Run the R pipeline to generate trade_latent_positions.csv."
    )
    st.stop()

min_yr = int(trade_latent["year"].min())
max_yr = int(trade_latent["year"].max())

# controls
year = st.slider("Year", min_yr, max_yr, max_yr, step=1)

# build circplot
fig = trade_latent_space_scatter(trade_latent, year, groups)
st.plotly_chart(fig, use_container_width=True)

# how to read
with st.expander("How to read this chart"):
    st.markdown("""
This visualization applies the same LAME framework used for diplomatic
alignment to **directed bilateral trade flows**. The critical difference
is that trade is inherently directed: exports from A to B are not the same
as exports from B to A. As Minhas et al. argue in "Taking Dyads Seriously"
(2022), properly modeling directed networks requires separate latent
positions for senders and receivers. Collapsing them into a single position
discards information about the asymmetric structure of the network.

The model therefore estimates two latent vectors per country in each year.
The **sender positions** (U) capture each country's role as an exporter:
countries with similar U positions export to similar destinations. The
**receiver positions** (V) capture each country's role as an importer:
countries with similar V positions import from similar sources.

**Outer ring (triangles):** Sender (exporter) positions. Clustering on
this ring indicates countries that compete in or supply similar export
markets. The angle on the circle reflects which group of trade partners
a country's exports flow toward; the magnitude (node size) reflects how
distinctive that export profile is.

**Inner ring (circles):** Receiver (importer) positions. Clustering here
indicates countries that source imports from similar origins. A country
can have a very different importer profile than its exporter profile,
which is precisely why the model keeps these dimensions separate.

When a country's outer triangle and inner circle point in different
directions, that country has **asymmetric trade relationships**: it
exports to one set of partners but imports from a different set.
Comparing this chart with the Diplomatic Alignment Space reveals where
trade structure and diplomatic position-taking diverge.
""")

# caveat
with st.expander("Important caveats"):
    st.markdown(CAVEAT_BOX)
    st.markdown(
        "**Note on trade data:** Trade positions are estimated from bilateral "
        "trade flows (IMF Direction of Trade Statistics, 1990 to 2020; World Bank "
        "WITS, 2021 to 2023). They reflect goods trade only and do not include "
        "services, investment, or financial flows."
    )

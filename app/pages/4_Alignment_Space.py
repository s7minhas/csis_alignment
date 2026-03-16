"""Alignment Space — interactive 2D latent space visualization."""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import load_latent_positions, load_group_membership
from utils.plots import latent_space_scatter
from utils.text import CAVEAT_BOX

st.set_page_config(page_title="Alignment Space", page_icon="🗺️", layout="wide")
st.title("🗺️ The Diplomatic Alignment Space")

st.markdown(
    "Each dot is a country, positioned by a statistical model that finds the "
    "underlying structure in UN General Assembly voting. **Countries that vote "
    "with the same coalitions appear close together.** Use the slider to watch "
    "positions shift over time."
)

# ── Load data ──
latent = load_latent_positions()
groups = load_group_membership()

min_year = int(latent["year"].min())
max_year = int(latent["year"].max())

# ── Year slider ──
year = st.slider("Year", min_year, max_year, max_year, step=1)

# ── Scatter plot ──
fig = latent_space_scatter(latent, year, groups)
st.plotly_chart(fig, use_container_width=True)

# ── How to read this ──
with st.expander("How to read this chart"):
    st.markdown("""
**What you're looking at:** A map of diplomatic alignment based on UNGA voting.
Each dot is a country. The closer two countries are, the more similarly they
vote at the UN.

**What the axes mean:** The two dimensions don't have inherent labels — they're
the two main patterns the model finds in voting data. Roughly:
- Countries on the **right** tend to vote with Western democracies
- Countries on the **left** tend to vote with the Global South / non-aligned bloc
- The **vertical** axis often captures secondary divisions (e.g., Middle East issues)

**What to look for:**
- **Clusters**: Countries that appear together vote as a bloc
- **Movement over time**: Use the slider to see who's drifting where
- **Outliers**: Countries far from any cluster have distinctive voting patterns

**Key pattern**: The US and Israel typically appear as outliers on one side,
while most countries cluster toward the Global South position. This reflects
the reality that the US frequently votes in small minorities at the UNGA.
""")

# ── Caveat ──
with st.expander("⚠️ Important caveats"):
    st.markdown(CAVEAT_BOX)

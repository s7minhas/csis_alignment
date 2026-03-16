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
    "Each dot is a country placed on a circle according to its latent voting "
    "direction. **Countries that vote with the same coalitions appear near each "
    "other on the circle.** The distance from the center reflects how strongly "
    "a country's voting deviates from the global average. Use the slider to "
    "watch positions shift over time."
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
**What you're looking at:** Each country's latent voting position is shown as
a direction on a circle. The model estimates a two-dimensional vector for each
country; the **angle** on the circle represents the direction of that vector
(which coalition a country votes with), and the **distance from center**
represents its magnitude (how strongly the country's voting deviates from
the global average).

**What to look for:**
- **Nearby countries** on the circle vote with the same coalitions
- **Countries on opposite sides** vote with opposing coalitions
- **Countries closer to center** have weaker or more ambiguous voting patterns
- **Countries further from center** have distinctive, consistent voting patterns

**Key pattern**: The US and Israel typically appear isolated from the main
cluster. Most countries group on the opposite side, reflecting the Global
South consensus on many UNGA issues. Use the year slider to watch how
positions evolve.
""")

# ── Caveat ──
with st.expander("⚠️ Important caveats"):
    st.markdown(CAVEAT_BOX)

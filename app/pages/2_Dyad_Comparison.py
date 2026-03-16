"""Dyad Comparison — compare alignment between any two countries."""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import (
    load_dyad_scores, load_actors, get_dyad_country_list, get_country_name,
)
from utils.plots import dyad_trajectory
from utils.text import CAVEAT_BOX, format_alignment_description

st.set_page_config(page_title="Compare Countries", page_icon="↔️", layout="wide")
st.title("↔️ Compare Two Countries")

# ── Load data ──
dyad = load_dyad_scores()
actors = load_actors()
countries = get_dyad_country_list()
country_labels = [c[0] for c in countries]
country_codes = [c[1] for c in countries]

# ── Selectors ──
col1, col2 = st.columns(2)
with col1:
    label_1 = st.selectbox(
        "Country 1",
        country_labels,
        index=country_labels.index("United States (USA)") if "United States (USA)" in country_labels else 0,
    )
    iso3_1 = country_codes[country_labels.index(label_1)]

with col2:
    label_2 = st.selectbox(
        "Country 2",
        country_labels,
        index=country_labels.index("China (CHN)") if "China (CHN)" in country_labels else 1,
    )
    iso3_2 = country_codes[country_labels.index(label_2)]

name_1 = get_country_name(iso3_1, actors)
name_2 = get_country_name(iso3_2, actors)

if iso3_1 == iso3_2:
    st.warning("Please select two different countries.")
    st.stop()

# ── Find dyad data ──
dyad_data = dyad[
    ((dyad["iso3_1"] == iso3_1) & (dyad["iso3_2"] == iso3_2)) |
    ((dyad["iso3_1"] == iso3_2) & (dyad["iso3_2"] == iso3_1))
].sort_values("year")

if len(dyad_data) == 0:
    st.warning(f"No diplomatic alignment data available for {name_1} — {name_2}.")
    st.stop()

latest = dyad_data.iloc[-1]
earliest = dyad_data.iloc[0]

# ── Headline ──
st.markdown(f"## {name_1} ↔ {name_2}")

col_a, col_b, col_c = st.columns(3)
col_a.metric(
    f"Diplomatic Alignment ({int(latest['year'])})",
    f"{latest['structural_alignment']:.3f}",
    help="0 = very distant, 1 = perfectly aligned",
)
delta = latest["structural_alignment"] - earliest["structural_alignment"]
col_b.metric(
    f"Change since {int(earliest['year'])}",
    f"{delta:+.3f}",
    help="Positive = converging, negative = diverging",
)
col_c.markdown(
    f"**Assessment:** {format_alignment_description(latest['structural_alignment'])}"
)

# ── Context bar ──
st.markdown("**For context:**")
# Find some reference dyads
ref_dyads = [
    ("USA", "GBR", "US-UK"),
    ("USA", "CHN", "US-China"),
    ("CHN", "RUS", "China-Russia"),
    ("USA", "RUS", "US-Russia"),
]
ref_text = []
latest_year = int(latest["year"])
for r1, r2, label in ref_dyads:
    ref = dyad[
        (dyad["year"] == latest_year) &
        (((dyad["iso3_1"] == r1) & (dyad["iso3_2"] == r2)) |
         ((dyad["iso3_1"] == r2) & (dyad["iso3_2"] == r1)))
    ]
    if len(ref) > 0:
        ref_text.append(f"{label}: {ref.iloc[0]['structural_alignment']:.2f}")

if ref_text:
    st.markdown(f"*{' · '.join(ref_text)}*")

# ── Trajectory ──
st.plotly_chart(
    dyad_trajectory(dyad, iso3_1, iso3_2, name_1, name_2),
    use_container_width=True,
)

# ── Data table ──
with st.expander("Show year-by-year data"):
    display = dyad_data[["year", "structural_alignment"]].copy()
    display.columns = ["Year", "Diplomatic Alignment"]
    display = display.sort_values("Year", ascending=False)
    st.dataframe(
        display.style.format({"Diplomatic Alignment": "{:.4f}"}),
        use_container_width=True,
        hide_index=True,
    )

# ── Caveat ──
with st.expander("⚠️ Important caveats"):
    st.markdown(CAVEAT_BOX)
    st.markdown(
        "**Reminder:** This score is based on UN General Assembly voting. "
        "It captures diplomatic position-taking, not the full bilateral "
        "relationship. Trade, military cooperation, intelligence sharing, "
        "and personal diplomacy are not reflected here."
    )

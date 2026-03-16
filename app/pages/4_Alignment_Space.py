"""Alignment Space — interactive circular latent space visualization."""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import load_latent_positions, load_group_membership, load_anchor_scores
from utils.plots import latent_space_scatter
from utils.text import CAVEAT_BOX

st.set_page_config(page_title="Alignment Space", page_icon="🗺️", layout="wide")
st.title("🗺️ The Diplomatic Alignment Space")

st.markdown(
    "Each dot is a country placed on a circle according to its latent voting "
    "direction. **Countries that vote with the same coalitions appear near each "
    "other on the circle.** Node size reflects how strongly a country's voting "
    "deviates from the global average. Use the slider to watch positions shift "
    "over time."
)

# ── Load data ──
latent = load_latent_positions()
groups = load_group_membership()
anchor = load_anchor_scores()

min_year = int(latent["year"].min())
max_year = int(latent["year"].max())

# ── Controls ──
col_slider, col_color = st.columns([3, 1])
with col_slider:
    year = st.slider("Year", min_year, max_year, max_year, step=1)

# Merge trade data into latent for coloring
has_trade = "trade_US_minus_China" in anchor.columns
color_options = ["Bloc membership"]
if has_trade:
    color_options.append("Trade US-China tilt")
    color_options.append("Diplomacy-trade gap")

with col_color:
    color_by = st.selectbox("Color by", color_options)

# ── Build the plot ──
if color_by == "Bloc membership":
    fig = latent_space_scatter(latent, year, groups)
else:
    # Merge anchor trade data into latent positions for this year
    import numpy as np
    from utils.plots import go, COLORS

    lat_yr = latent[latent["year"] == year].copy()

    # Get trade data — fall back to previous year if needed
    anchor_yr = anchor[anchor["year"] == year]
    if has_trade and anchor_yr["trade_US_minus_China"].notna().sum() < 10:
        anchor_yr = anchor[anchor["year"] == year - 1]

    lat_merged = lat_yr.merge(
        anchor_yr[["country", "US_minus_China", "trade_US_minus_China"]].rename(columns={"country": "iso3"}),
        on="iso3", how="left"
    )

    # Compute circle positions (same logic as latent_space_scatter)
    mag = np.sqrt(lat_merged["dim1"].values**2 + lat_merged["dim2"].values**2)
    safe_mag = np.where(mag > 1e-10, mag, 1.0)
    u_norm_x = lat_merged["dim1"].values / safe_mag
    u_norm_y = lat_merged["dim2"].values / safe_mag
    n = len(lat_merged)
    mag_rank = pd.Series(mag).rank().values / (n + 1)
    radii = 1.0 + 0.15 * (mag_rank - 0.5)
    lat_merged["cx"] = u_norm_x * radii
    lat_merged["cy"] = u_norm_y * radii
    mag_min, mag_range = mag.min(), mag.max() - mag.min() + 0.01
    lat_merged["node_size"] = 4 + 16 * (mag - mag_min) / mag_range

    if color_by == "Trade US-China tilt":
        color_col = "trade_US_minus_China"
        color_label = "Trade tilt"
        cmin, cmax = -0.8, 0.8
    else:
        # Diplomacy-trade gap = diplomatic tilt minus trade tilt
        lat_merged["gap"] = lat_merged["US_minus_China"] - lat_merged["trade_US_minus_China"]
        color_col = "gap"
        color_label = "Diplo - Trade gap"
        cmin, cmax = -0.8, 0.8

    fig = go.Figure()

    # reference circle
    theta_vals = np.linspace(0, 2 * np.pi, 200)
    fig.add_trace(go.Scatter(
        x=np.cos(theta_vals).tolist(), y=np.sin(theta_vals).tolist(),
        mode="lines", line=dict(color="#DDDDDD", dash="dot", width=1),
        showlegend=False, hoverinfo="skip",
    ))

    valid = lat_merged.dropna(subset=[color_col])
    fig.add_trace(go.Scatter(
        x=valid["cx"].tolist(), y=valid["cy"].tolist(),
        mode="markers",
        marker=dict(
            size=valid["node_size"].tolist(),
            color=valid[color_col].tolist(),
            colorscale=[[0, "#B2182B"], [0.5, "#F7F7F7"], [1, "#2166AC"]],
            cmin=cmin, cmax=cmax,
            colorbar=dict(title=color_label, tickvals=[cmin, 0, cmax],
                          ticktext=["← China", "Neutral", "US →"]),
            line=dict(width=0.5, color="white"),
            opacity=0.85,
        ),
        text=valid["name_common"].tolist(),
        customdata=np.stack([valid["iso3"].values, valid[color_col].values], axis=-1),
        hovertemplate="<b>%{text}</b><br>%{customdata[0]}<br>" + color_label + ": %{customdata[1]:.2f}<extra></extra>",
        showlegend=False,
    ))

    # labels
    key_labels = ["USA", "CHN", "RUS", "GBR", "IND", "BRA", "JPN", "KOR",
                  "SAU", "TUR", "ISR", "UKR", "CUB", "PRK", "DEU", "AUS", "ZAF"]
    for _, row in valid[valid["iso3"].isin(key_labels)].iterrows():
        fig.add_annotation(
            x=row["cx"], y=row["cy"], text=row["iso3"],
            showarrow=False, font=dict(size=9, color="#333333"),
            yshift=max(8, row["node_size"] / 2 + 4),
        )

    yr_label = year if color_col != "gap" else f"{min(year, year-1)}"
    fig.update_layout(
        title=dict(text=f"Alignment Space colored by {color_label} ({yr_label})", y=0.98),
        height=700, margin=dict(t=100, l=20, r=20, b=20),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title="",
                   range=[-1.4, 1.4]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title="",
                   range=[-1.4, 1.4], scaleanchor="x", scaleratio=1),
        plot_bgcolor="white",
    )

st.plotly_chart(fig, use_container_width=True)

# ── How to read this ──
with st.expander("How to read this chart"):
    st.markdown("""
**What you're looking at:** Each country's latent voting position is shown as
a direction on a circle. The model estimates a two-dimensional vector for each
country; the **angle** on the circle represents the direction of that vector
(which coalition a country votes with). **Node size** reflects magnitude
(how strongly the country's voting deviates from the global average).

**Color modes:**
- **Bloc membership**: Countries colored by G7, BRICS, Global South, or Other
- **Trade US-China tilt**: Blue = trades more with US, red = trades more with China. Shows where economic relationships sit relative to diplomatic positions.
- **Diplomacy-trade gap**: Blue = diplomatically closer to US than trade suggests, red = diplomatically closer to China than trade suggests. Countries in white are consistent; colored countries show divergence.

**What to look for:**
- **Nearby countries** on the circle vote with the same coalitions
- **Countries on opposite sides** vote with opposing coalitions
- In trade-colored mode: a **red dot on the US side** of the circle means a country votes with the US but trades with China (e.g., Australia)
""")

# ── Caveat ──
with st.expander("⚠️ Important caveats"):
    st.markdown(CAVEAT_BOX)

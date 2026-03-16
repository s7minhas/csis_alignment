"""Plotly figure builders for the dashboard."""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Color scheme
COLORS = {
    "us": "#2166AC",
    "china": "#B2182B",
    "russia": "#7B3294",
    "g7": "#2166AC",
    "brics": "#B2182B",
    "nato": "#4393C3",
    "asean": "#1B7837",
    "global_south": "#1B7837",
    "neutral": "#636363",
    "positive": "#2166AC",
    "negative": "#B2182B",
}

BLOC_COLORS = {
    "G7": COLORS["g7"],
    "BRICS": COLORS["brics"],
    "NATO": COLORS["nato"],
    "ASEAN": COLORS["asean"],
    "Global South": COLORS["global_south"],
}

def diplomacy_vs_trade_scatter(anchor_df, year):
    """Scatter: diplomatic tilt (x) vs trade tilt (y) for each country.
    Countries on the diagonal are consistent. Off-diagonal = divergence."""
    import numpy as np

    df = anchor_df[(anchor_df["year"] == year)].copy()
    # need both diplomatic and trade tilt
    df = df.dropna(subset=["US_minus_China", "trade_US_minus_China"])
    if len(df) == 0:
        # fall back to previous year
        df = anchor_df[(anchor_df["year"] == year - 1)].copy()
        df = df.dropna(subset=["US_minus_China", "trade_US_minus_China"])
        year = year - 1

    if len(df) == 0:
        return go.Figure().update_layout(title="No trade data available")

    df["group_label"] = "Other"
    df.loc[df["g7"] == True, "group_label"] = "G7"
    df.loc[df["brics_original"] == True, "group_label"] = "BRICS"
    df.loc[(df["global_south"] == True) & (df["group_label"] == "Other"), "group_label"] = "Global South"

    color_map = {"G7": COLORS["g7"], "BRICS": COLORS["brics"],
                 "Global South": COLORS["global_south"], "Other": "#AAAAAA"}

    fig = go.Figure()

    # diagonal line (consistency)
    fig.add_trace(go.Scatter(
        x=[-1, 1], y=[-1, 1], mode="lines",
        line=dict(color="#DDDDDD", dash="dash", width=1),
        showlegend=False, hoverinfo="skip",
    ))

    # quadrant labels
    fig.add_annotation(x=0.6, y=-0.4, text="Votes US, trades China",
                       showarrow=False, font=dict(size=10, color="#999999"))
    fig.add_annotation(x=-0.6, y=0.4, text="Votes China, trades US",
                       showarrow=False, font=dict(size=10, color="#999999"))

    # plot each group
    for group_name in ["G7", "BRICS", "Global South", "Other"]:
        gdf = df[df["group_label"] == group_name]
        if len(gdf) == 0:
            continue
        fig.add_trace(go.Scatter(
            x=gdf["US_minus_China"].tolist(),
            y=gdf["trade_US_minus_China"].tolist(),
            mode="markers",
            marker=dict(size=8, color=color_map.get(group_name, "#AAAAAA"), opacity=0.7),
            name=group_name,
            text=gdf["name_common"].tolist(),
            customdata=np.stack([gdf["country"].values,
                                 gdf["US_minus_China"].values,
                                 gdf["trade_US_minus_China"].values], axis=-1),
            hovertemplate="<b>%{text}</b><br>Diplomatic tilt: %{customdata[1]:.2f}<br>"
                          "Trade tilt: %{customdata[2]:.2f}<extra></extra>",
        ))

    # key country labels
    for _, row in df[df["country"].isin(
        ["AUS", "KOR", "IND", "MEX", "BRA", "RUS", "GBR", "JPN",
         "SAU", "TUR", "DEU", "CAN", "VNM", "PRK", "CUB"])].iterrows():
        fig.add_annotation(
            x=row["US_minus_China"], y=row["trade_US_minus_China"],
            text=row["country"], showarrow=False,
            font=dict(size=8, color="#333333"), yshift=10,
        )

    fig.update_layout(
        title=f"Diplomacy vs Trade: Where Do They Diverge? ({year})",
        xaxis=dict(title="← China · Diplomatic Tilt · US →", range=[-1.1, 1.1], zeroline=True,
                   zerolinecolor="#EEEEEE"),
        yaxis=dict(title="← China · Trade Tilt · US →", range=[-1.1, 1.1], zeroline=True,
                   zerolinecolor="#EEEEEE"),
        height=500, margin=dict(t=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        plot_bgcolor="white",
    )
    return fig


EVENT_ANNOTATIONS = [
    (1991, "USSR Dissolves"),
    (2001, "9/11"),
    (2008, "Financial Crisis"),
    (2014, "Crimea"),
    (2020, "COVID-19"),
    (2022, "Ukraine Invasion"),
]


def _add_event_lines(fig, years_range=None):
    """Add dashed vertical lines for key geopolitical events."""
    for year, label in EVENT_ANNOTATIONS:
        if years_range and (year < years_range[0] or year > years_range[1]):
            continue
        fig.add_vline(
            x=year, line_dash="dot", line_color="#CCCCCC",
            annotation_text=label, annotation_position="top",
            annotation_font_size=9, annotation_font_color="#999999",
        )


def world_map_tilt(anchor_df, year):
    """Choropleth map of US-China tilt for a given year."""
    df = anchor_df[anchor_df["year"] == year].copy()

    fig = px.choropleth(
        df,
        locations="country",
        color="US_minus_China",
        hover_name="name_common",
        hover_data={
            "US_minus_China": ":.2f",
            "alignment_with_US": ":.2f",
            "alignment_with_China": ":.2f",
            "country": False,
        },
        color_continuous_scale=["#B2182B", "#F4A582", "#F7F7F7", "#92C5DE", "#2166AC"],
        color_continuous_midpoint=0,
        range_color=[-1, 1],
        labels={"US_minus_China": "US-China Tilt"},
        title=f"Diplomatic Alignment: US vs China Tilt ({year})",
    )
    fig.update_layout(
        geo=dict(showframe=False, showcoastlines=True, coastlinecolor="#CCCCCC",
                 projection_type="natural earth"),
        margin=dict(l=0, r=0, t=40, b=0),
        height=450,
        coloraxis_colorbar=dict(
            title="Tilt",
            tickvals=[-0.8, -0.4, 0, 0.4, 0.8],
            ticktext=["← China", "", "Neutral", "", "US →"],
        ),
    )
    return fig


def country_trajectory(anchor_df, iso3, country_name):
    """Combined chart: diplomatic alignment AND trade shares with US and China."""
    from plotly.subplots import make_subplots

    df = anchor_df[anchor_df["country"] == iso3].sort_values("year")
    has_trade = "trade_share_US" in df.columns and df["trade_share_US"].notna().any()

    if has_trade:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
    else:
        fig = go.Figure()

    # diplomatic alignment (left y-axis, solid lines)
    fig.add_trace(go.Scatter(
        x=df["year"], y=df["alignment_with_US"],
        name="Diplomatic: US", mode="lines",
        line=dict(color=COLORS["us"], width=2.5),
    ), secondary_y=False if has_trade else None)

    fig.add_trace(go.Scatter(
        x=df["year"], y=df["alignment_with_China"],
        name="Diplomatic: China", mode="lines",
        line=dict(color=COLORS["china"], width=2.5),
    ), secondary_y=False if has_trade else None)

    # trade shares (right y-axis, dashed lines)
    if has_trade:
        trade_df = df.dropna(subset=["trade_share_US"])
        fig.add_trace(go.Scatter(
            x=trade_df["year"], y=trade_df["trade_share_US"],
            name="Trade: US", mode="lines",
            line=dict(color=COLORS["us"], width=2, dash="dash"),
        ), secondary_y=True)

        fig.add_trace(go.Scatter(
            x=trade_df["year"], y=trade_df["trade_share_China"],
            name="Trade: China", mode="lines",
            line=dict(color=COLORS["china"], width=2, dash="dash"),
        ), secondary_y=True)

    _add_event_lines(fig, (df["year"].min(), df["year"].max()))

    title = f"{country_name}: Diplomatic Alignment"
    if has_trade:
        title += " & Trade Dependence"

    fig.update_layout(
        title=title,
        xaxis_title=None,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=420, margin=dict(t=70),
        hovermode="x unified",
    )

    if has_trade:
        fig.update_yaxes(title_text="Diplomatic Alignment", range=[0, 1],
                         secondary_y=False)
        fig.update_yaxes(title_text="Trade Share", range=[0, 1],
                         tickformat=".0%", secondary_y=True)
    else:
        fig.update_yaxes(title_text="Alignment Score", range=[0, 1])

    return fig


def tilt_trajectory(anchor_df, iso3, country_name):
    """Combined tilt chart: diplomatic tilt and trade tilt on the same axes."""
    df = anchor_df[anchor_df["country"] == iso3].sort_values("year")
    has_trade = "trade_US_minus_China" in df.columns and df["trade_US_minus_China"].notna().any()

    fig = go.Figure()

    # diplomatic tilt
    fig.add_trace(go.Scatter(
        x=df["year"], y=df["US_minus_China"],
        name="Diplomatic tilt", mode="lines",
        line=dict(color=COLORS["neutral"], width=2.5),
        fill="tozeroy", fillcolor="rgba(33,102,172,0.10)",
    ))

    # trade tilt
    if has_trade:
        trade_df = df.dropna(subset=["trade_US_minus_China"])
        fig.add_trace(go.Scatter(
            x=trade_df["year"], y=trade_df["trade_US_minus_China"],
            name="Trade tilt", mode="lines",
            line=dict(color="#E08214", width=2.5, dash="dash"),
        ))

    fig.add_hline(y=0, line_dash="dash", line_color="#CCCCCC")

    title = f"{country_name}: US-China Tilt"
    if has_trade:
        title += " (Diplomacy vs Trade)"

    fig.update_layout(
        title=title,
        xaxis_title=None,
        yaxis_title="← China · US →",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=420, margin=dict(t=70),
        hovermode="x unified",
    )
    return fig


def dyad_trajectory(dyad_df, iso3_1, iso3_2, name_1, name_2):
    """Line chart: structural alignment between two countries over time."""
    df = dyad_df[
        ((dyad_df["iso3_1"] == iso3_1) & (dyad_df["iso3_2"] == iso3_2)) |
        ((dyad_df["iso3_1"] == iso3_2) & (dyad_df["iso3_2"] == iso3_1))
    ].sort_values("year")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["year"], y=df["structural_alignment"],
        mode="lines+markers",
        line=dict(color=COLORS["neutral"], width=2.5),
        marker=dict(size=4),
        name="Alignment",
    ))

    _add_event_lines(fig, (df["year"].min(), df["year"].max()))

    fig.update_layout(
        title=f"{name_1} ↔ {name_2}: Diplomatic Alignment",
        xaxis_title=None, yaxis_title="Alignment Score",
        yaxis_range=[0, 1],
        height=400, margin=dict(t=60),
        showlegend=False,
    )
    return fig


def bloc_cohesion_chart(bloc_df):
    """Line chart: within-bloc cohesion over time."""
    fig = go.Figure()
    for bloc in bloc_df["bloc"].unique():
        df = bloc_df[bloc_df["bloc"] == bloc].sort_values("year")
        color = BLOC_COLORS.get(bloc, COLORS["neutral"])
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["within_cohesion"],
            name=bloc, mode="lines",
            line=dict(color=color, width=2.5),
        ))

    _add_event_lines(fig, (bloc_df["year"].min(), bloc_df["year"].max()))

    fig.update_layout(
        title="Within-Bloc Diplomatic Cohesion",
        xaxis_title=None, yaxis_title="Mean Pairwise Alignment",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=400, margin=dict(t=60),
        hovermode="x unified",
    )
    return fig


def bloc_tilt_chart(bloc_df):
    """Line chart: bloc-level US vs China tilt."""
    fig = go.Figure()
    for bloc in bloc_df["bloc"].unique():
        df = bloc_df[bloc_df["bloc"] == bloc].sort_values("year")
        color = BLOC_COLORS.get(bloc, COLORS["neutral"])
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["US_minus_China"],
            name=bloc, mode="lines",
            line=dict(color=color, width=2.5),
        ))

    fig.add_hline(y=0, line_dash="dash", line_color="#999999")
    _add_event_lines(fig, (bloc_df["year"].min(), bloc_df["year"].max()))

    fig.update_layout(
        title="Bloc-Level US vs China Tilt",
        xaxis_title=None,
        yaxis_title="← China · US →",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=400, margin=dict(t=60),
        hovermode="x unified",
    )
    return fig


def latent_space_scatter(latent_df, year, groups_df):
    """Circular layout of latent positions following lame's uv_plot.

    Each country's latent vector is normalized to unit length to get its
    angle (direction = which coalition it votes with). Countries are placed
    ON the reference circle at that angle, with a small rank-based radial
    jitter so overlapping nodes separate. Node SIZE encodes magnitude
    (how strongly the country's voting deviates from the global mean).
    """
    import numpy as np

    df = latent_df[latent_df["year"] == year].copy()

    # magnitude and unit direction (matching lame uv_plot lines 186-200)
    mag = np.sqrt(df["dim1"].values**2 + df["dim2"].values**2)
    df["magnitude"] = mag

    # normalize to unit vectors for angle
    safe_mag = np.where(mag > 1e-10, mag, 1.0)
    u_norm_x = df["dim1"].values / safe_mag
    u_norm_y = df["dim2"].values / safe_mag

    # rank-based radial jitter (matching lame uv_plot lines 204-211)
    n = len(df)
    mag_rank = pd.Series(mag).rank().values / (n + 1)
    jitter_factor = 0.15
    radii = 1.0 + jitter_factor * (mag_rank - 0.5)

    # place on circle at unit-vector angle, radius ~ 1 with jitter
    df["cx"] = u_norm_x * radii
    df["cy"] = u_norm_y * radii

    # node size scaled by magnitude (matching lame uv_plot lines 272-276)
    mag_min = mag.min()
    mag_range = mag.max() - mag_min + 0.01
    df["node_size"] = 4 + 16 * (mag - mag_min) / mag_range

    # group labels
    df["group_label"] = "Other"
    df.loc[df["g7"] == True, "group_label"] = "G7"
    df.loc[df["brics_original"] == True, "group_label"] = "BRICS"
    df.loc[(df["global_south"] == True) & (df["group_label"] == "Other"), "group_label"] = "Global South"

    color_map = {"G7": COLORS["g7"], "BRICS": COLORS["brics"],
                 "Global South": COLORS["global_south"], "Other": "#AAAAAA"}

    fig = go.Figure()

    # reference circle
    theta = np.linspace(0, 2 * np.pi, 200)
    fig.add_trace(go.Scatter(
        x=np.cos(theta).tolist(), y=np.sin(theta).tolist(),
        mode="lines", line=dict(color="#DDDDDD", dash="dot", width=1),
        showlegend=False, hoverinfo="skip",
    ))

    # plot each group separately for legend
    for group_name in ["G7", "BRICS", "Global South", "Other"]:
        gdf = df[df["group_label"] == group_name]
        if len(gdf) == 0:
            continue
        fig.add_trace(go.Scatter(
            x=gdf["cx"].tolist(),
            y=gdf["cy"].tolist(),
            mode="markers",
            marker=dict(
                size=gdf["node_size"].tolist(),
                color=color_map.get(group_name, "#AAAAAA"),
                opacity=0.8,
                line=dict(width=0.5, color="white"),
            ),
            name=group_name,
            text=gdf["name_common"].tolist(),
            customdata=np.stack([gdf["iso3"].values, gdf["magnitude"].values], axis=-1),
            hovertemplate="<b>%{text}</b><br>%{customdata[0]}<br>Magnitude: %{customdata[1]:.3f}<extra></extra>",
        ))

    # labels for key countries
    key_labels = ["USA", "CHN", "RUS", "GBR", "IND", "BRA", "JPN", "KOR",
                  "SAU", "TUR", "ISR", "UKR", "CUB", "PRK", "DEU", "AUS", "ZAF"]
    for _, row in df[df["iso3"].isin(key_labels)].iterrows():
        fig.add_annotation(
            x=row["cx"], y=row["cy"], text=row["iso3"],
            showarrow=False, font=dict(size=9, color="#333333"),
            yshift=max(8, row["node_size"] / 2 + 4),
        )

    fig.update_layout(
        title=dict(text=f"Diplomatic Alignment Space ({year})", y=0.98),
        height=700, margin=dict(t=100, l=20, r=20, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.08, x=0.5, xanchor="center"),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False,
                   title="", range=[-1.4, 1.4]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False,
                   title="", range=[-1.4, 1.4], scaleanchor="x", scaleratio=1),
        plot_bgcolor="white",
    )
    return fig

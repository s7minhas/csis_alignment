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
    """Line chart: alignment with US vs China over time for one country."""
    df = anchor_df[anchor_df["country"] == iso3].sort_values("year")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["year"], y=df["alignment_with_US"],
        name="Alignment with US", mode="lines",
        line=dict(color=COLORS["us"], width=2.5),
    ))
    fig.add_trace(go.Scatter(
        x=df["year"], y=df["alignment_with_China"],
        name="Alignment with China", mode="lines",
        line=dict(color=COLORS["china"], width=2.5),
    ))

    _add_event_lines(fig, (df["year"].min(), df["year"].max()))

    fig.update_layout(
        title=f"{country_name}: Diplomatic Alignment Trajectory",
        xaxis_title=None, yaxis_title="Alignment Score",
        yaxis_range=[0, 1],
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=400, margin=dict(t=60),
        hovermode="x unified",
    )
    return fig


def tilt_trajectory(anchor_df, iso3, country_name):
    """Area chart: US-minus-China tilt over time."""
    df = anchor_df[anchor_df["country"] == iso3].sort_values("year")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["year"], y=df["US_minus_China"],
        fill="tozeroy", mode="lines",
        line=dict(color=COLORS["neutral"], width=2),
        fillcolor="rgba(33,102,172,0.15)",
    ))
    fig.add_hline(y=0, line_dash="dash", line_color="#999999")

    # Color the area: blue above 0, red below
    fig.update_layout(
        title=f"{country_name}: US-China Tilt",
        xaxis_title=None,
        yaxis_title="← China · US →",
        height=300, margin=dict(t=50),
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
    """Scatter plot of 2D latent positions for a given year."""
    df = latent_df[latent_df["year"] == year].copy()

    df["group_label"] = "Other"
    df.loc[df["g7"] == True, "group_label"] = "G7"
    df.loc[df["brics_original"] == True, "group_label"] = "BRICS"
    df.loc[(df["global_south"] == True) & (df["group_label"] == "Other"), "group_label"] = "Global South"

    color_map = {"G7": COLORS["g7"], "BRICS": COLORS["brics"],
                 "Global South": COLORS["global_south"], "Other": "#AAAAAA"}

    fig = px.scatter(
        df, x="dim1", y="dim2",
        color="group_label",
        hover_name="name_common",
        hover_data={"dim1": ":.2f", "dim2": ":.2f", "iso3": True, "group_label": False},
        color_discrete_map=color_map,
        title=f"Diplomatic Alignment Space ({year})",
        labels={"dim1": "Dimension 1", "dim2": "Dimension 2", "group_label": "Group"},
    )

    # Add labels for key countries
    key_labels = ["USA", "CHN", "RUS", "GBR", "IND", "BRA", "JPN", "KOR",
                  "SAU", "TUR", "ISR", "UKR", "CUB", "PRK", "DEU", "AUS", "ZAF"]
    for _, row in df[df["iso3"].isin(key_labels)].iterrows():
        fig.add_annotation(
            x=row["dim1"], y=row["dim2"], text=row["iso3"],
            showarrow=False, font=dict(size=9, color="#333333"),
            yshift=12,
        )

    fig.update_layout(
        height=550, margin=dict(t=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    fig.update_traces(marker=dict(size=10, opacity=0.8))
    return fig

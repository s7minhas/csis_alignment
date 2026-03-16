"""Cached data loading for the dashboard."""

import pandas as pd
import streamlit as st
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


@st.cache_data
def load_anchor_scores():
    df = pd.read_csv(DATA_DIR / "country_year_anchor.csv")
    return df


@st.cache_data
def load_dyad_scores():
    df = pd.read_csv(DATA_DIR / "dyad_year_scores.csv")
    return df


@st.cache_data
def load_bloc_summaries():
    df = pd.read_csv(DATA_DIR / "bloc_year_summaries_model.csv")
    return df


@st.cache_data
def load_latent_positions():
    df = pd.read_csv(DATA_DIR / "latent_positions.csv")
    return df


@st.cache_data
def load_group_membership():
    df = pd.read_csv(DATA_DIR / "group_membership.csv")
    return df


@st.cache_data
def load_actors():
    df = pd.read_csv(DATA_DIR / "actors_master.csv")
    return df


@st.cache_data
def load_raw_agreement():
    """Load raw UNGA agreement — large file, only load when needed."""
    df = pd.read_csv(DATA_DIR / "dyad_year_unga_agreement.csv")
    return df


def has_trade_data():
    """Check if trade coupling columns exist in the anchor data."""
    anchor = load_anchor_scores()
    return "trade_coupling_US" in anchor.columns


def get_country_name(iso3, actors_df=None):
    """Get common name from ISO3 code."""
    if actors_df is None:
        actors_df = load_actors()
    match = actors_df[actors_df["iso3"] == iso3]
    if len(match) > 0:
        return match.iloc[0]["name_common"]
    return iso3


def get_country_list():
    """Get sorted list of (name, iso3) tuples for dropdowns.
    Includes USA and CHN (anchor states) so users can search for them."""
    anchor = load_anchor_scores()
    dyad = load_dyad_scores()
    actors = load_actors()
    # Union of anchor countries + dyad countries (includes USA, CHN)
    iso3s = sorted(set(anchor["country"].unique()) |
                   set(dyad["iso3_1"].unique()) |
                   set(dyad["iso3_2"].unique()))
    result = []
    for code in iso3s:
        name = get_country_name(code, actors)
        result.append((f"{name} ({code})", code))
    result.sort()
    return result


def get_dyad_country_list():
    """Get sorted country list from dyad scores."""
    dyad = load_dyad_scores()
    actors = load_actors()
    iso3s = sorted(set(dyad["iso3_1"].unique()) | set(dyad["iso3_2"].unique()))
    result = []
    for code in iso3s:
        name = get_country_name(code, actors)
        result.append((f"{name} ({code})", code))
    result.sort()
    return result

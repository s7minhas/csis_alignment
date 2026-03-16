"""Methodology & Caveats — full documentation for non-technical audiences."""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.text import METHODOLOGY_FULL, ABOUT_TEXT, CAVEAT_BOX

st.set_page_config(page_title="Methodology", page_icon="📖", layout="wide")
st.title("📖 Methodology & Caveats")

st.markdown(CAVEAT_BOX)

st.markdown("---")

st.markdown(METHODOLOGY_FULL)

st.markdown("---")

st.markdown(ABOUT_TEXT)

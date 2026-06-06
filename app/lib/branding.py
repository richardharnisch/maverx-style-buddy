"""Maverx branding for the Decker Streamlit UI.

Centralises the palette, typography, and shared page chrome so every page
looks consistent. Colours come from the Maverx slide dictionary.
"""

from __future__ import annotations

import streamlit as st

# Maverx palette
PRIMARY_DARK = "#0D006A"
DARK_PURPLE = "#1A0040"
DEEP_PURPLE = "#3F0576"
ORANGE = "#F48A28"
TEAL = "#00B0F0"
ROSE = "#EF4453"
BG_LAVENDER = "#EDE9FF"
OFF_WHITE = "#F2F2F2"

_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Raleway:wght@400;600&display=swap');

html, body, [class*="css"] {{
    font-family: 'Raleway', sans-serif;
    color: {PRIMARY_DARK};
}}
h1, h2, h3, h4, .decker-title {{
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    color: {PRIMARY_DARK};
}}
/* Accent the primary buttons in Maverx orange */
.stButton > button[kind="primary"], .stDownloadButton > button {{
    background-color: {ORANGE};
    border: none;
    color: white;
}}
.decker-header {{
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 0.25rem;
}}
.decker-logo {{
    width: 34px; height: 34px; border-radius: 9px;
    background: linear-gradient(135deg, {DEEP_PURPLE}, {ORANGE});
    display: inline-block;
}}
.decker-wordmark {{
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700; font-size: 1.6rem; color: {PRIMARY_DARK};
}}
.decker-tagline {{ color: {DEEP_PURPLE}; font-size: 0.85rem; }}
</style>
"""


def apply(page_title: str = "Decker", subtitle: str | None = None) -> None:
    """Inject the shared CSS + render the Decker logo header.

    Call once at the top of every page (after st.set_page_config).
    """
    st.markdown(_CSS, unsafe_allow_html=True)
    st.markdown(
        f'<div class="decker-header">'
        f'<span class="decker-logo"></span>'
        f'<span class="decker-wordmark">Decker</span></div>',
        unsafe_allow_html=True,
    )
    if subtitle:
        st.markdown(
            f'<div class="decker-tagline">{subtitle}</div>',
            unsafe_allow_html=True,
        )
    st.divider()

"""Decker — settings. Pick the model used for deck generation."""

import streamlit as st

from lib import api
from lib.branding import apply

st.set_page_config(page_title="Decker — Settings", page_icon="⚙️", layout="centered")
apply(subtitle="Configure how Decker builds your decks")

st.subheader("Model")

try:
    info = api.get_models()
    models = info["models"]
    default = info["default"]
except api.APIError as exc:
    st.error(str(exc))
    st.stop()

# Seed the shared choice if unset, then let the selectbox drive it.
current = st.session_state.get("model", default)
if current not in models:
    current = default

choice = st.selectbox(
    "Model used for deck generation",
    options=models,
    index=models.index(current),
    help="The selected model is sent with each chat message.",
)
st.session_state["model"] = choice
st.session_state["available_models"] = models

st.success(f"Active model: `{choice}`")

st.divider()
with st.expander("Backend status"):
    try:
        st.json(api.health())
    except api.APIError as exc:
        st.error(str(exc))

"""Decker — slide template gallery + upload."""

import streamlit as st

from lib import api
from lib.branding import apply

st.set_page_config(page_title="Decker — Templates", page_icon="🖼️", layout="wide")
apply(subtitle="Browse and upload Maverx slide templates")

st.subheader("Available templates")

try:
    templates = api.list_templates()
except api.APIError as exc:
    st.error(str(exc))
    st.stop()

if not templates:
    st.info("No templates found.")
else:
    st.caption(f"{len(templates)} templates")
    cols_per_row = 3
    for i in range(0, len(templates), cols_per_row):
        row = st.columns(cols_per_row)
        for col, tpl in zip(row, templates[i : i + cols_per_row]):
            with col:
                st.image(
                    api.template_preview_url(tpl["template_id"]),
                    use_container_width=True,
                )
                st.caption(f"**{tpl['title']}**  \n`{tpl['template_id']}`")

st.divider()
st.subheader("Upload a template")
st.caption("Stub — uploads are accepted but not yet persisted.")

uploaded = st.file_uploader(
    "Add a .pptx or image template", type=["pptx", "png", "jpg", "jpeg"]
)
if uploaded is not None and st.button("Upload", type="primary"):
    try:
        result = api.upload_template(
            uploaded.name, uploaded.getvalue(), uploaded.type or "application/octet-stream"
        )
        st.success(result.get("detail", "Uploaded."))
        st.json(result)
    except api.APIError as exc:
        st.error(str(exc))

"""Decker — chat page. Each session is one slide deck."""

import streamlit as st

from lib import api
from lib.branding import apply

st.set_page_config(page_title="Decker — Chat", page_icon="🃏", layout="wide")
apply(subtitle="Chat your way to a Maverx-branded slide deck")


# --- state helpers ------------------------------------------------------

def _init_state() -> None:
    st.session_state.setdefault("decks", {})  # session_id -> {title, messages}
    st.session_state.setdefault("active", None)
    if "model" not in st.session_state:
        try:
            models = api.get_models()
            st.session_state["model"] = models["default"]
            st.session_state["available_models"] = models["models"]
        except api.APIError:
            st.session_state["model"] = "unknown"
            st.session_state["available_models"] = []


def _deck_title(messages: list[dict]) -> str:
    for m in messages:
        if m["role"] == "user" and m.get("content"):
            text = m["content"].strip()
            return (text[:38] + "…") if len(text) > 38 else text
    return "New deck"


def _new_deck() -> None:
    session = api.create_session()
    sid = session["id"]
    st.session_state.decks[sid] = {"title": "New deck", "messages": []}
    st.session_state.active = sid


def _select_deck(sid: str) -> None:
    st.session_state.active = sid
    # Refresh messages from the backend (source of truth).
    msgs = api.list_messages(sid)
    st.session_state.decks[sid]["messages"] = msgs
    st.session_state.decks[sid]["title"] = _deck_title(msgs)


_init_state()


# --- sidebar: deck list (the left rail in the sketch) -------------------

with st.sidebar:
    st.markdown("### 🗂️ Decks")
    if st.button("➕ New deck", use_container_width=True, type="primary"):
        try:
            _new_deck()
        except api.APIError as exc:
            st.error(str(exc))
    st.markdown("---")
    if not st.session_state.decks:
        st.caption("No decks yet. Start one above.")
    for sid, deck in reversed(list(st.session_state.decks.items())):
        is_active = sid == st.session_state.active
        label = ("▸ " if is_active else "") + deck["title"]
        if st.button(label, key=f"deck-{sid}", use_container_width=True):
            _select_deck(sid)
    st.markdown("---")
    st.caption(f"Model: `{st.session_state.get('model')}`")


# --- main: chat transcript + deck preview -------------------------------

active = st.session_state.active

if not active:
    st.info("👈 Create a new deck to start chatting.")
    st.stop()

deck = st.session_state.decks[active]
chat_col, preview_col = st.columns([2, 1], gap="large")

with chat_col:
    st.subheader(deck["title"])
    for msg in deck["messages"]:
        avatar = "🧑" if msg["role"] == "user" else "🃏"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

with preview_col:
    st.markdown("##### Deck preview")
    deck_artifact = next(
        (m.get("deck") for m in reversed(deck["messages"]) if m.get("deck")),
        None,
    )
    if deck_artifact:
        st.success(f"{deck_artifact['filename']} · {deck_artifact['slide_count']} slides")
        st.button("⬇️ Download .pptx", disabled=True, help="Available once generation is wired up")
    else:
        st.container(border=True).markdown(
            "🖼️ *Your generated deck will appear here.*\n\n"
            "Deck generation is not wired up yet — the chat returns a stub reply."
        )


# chat_input must live at the page level (it pins to the bottom).
prompt = st.chat_input("Describe the deck you want to build…")
if prompt:
    try:
        msgs = api.send_message(active, prompt, st.session_state["model"])
        deck["messages"] = msgs
        deck["title"] = _deck_title(msgs)
        st.rerun()
    except api.APIError as exc:
        st.error(str(exc))

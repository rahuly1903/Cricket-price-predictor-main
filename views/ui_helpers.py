"""Shared UI helpers for flash messages and tab navigation."""

import streamlit as st


def show_flash() -> None:
    flash = st.session_state.pop("flash_message", None)
    if not flash:
        return
    kind, text = flash
    if kind == "success":
        st.success(text)
    elif kind == "error":
        st.error(text)
    elif kind == "warning":
        st.warning(text)
    else:
        st.info(text)


def set_flash(kind: str, text: str) -> None:
    st.session_state.flash_message = (kind, text)


def render_tab_selector(session_key: str, tabs: list[tuple[str, str]], default: str) -> str:
    """Button-based tab selector to avoid radio rerun jumping."""
    if session_key not in st.session_state:
        st.session_state[session_key] = default

    active = st.session_state[session_key]
    if active not in [key for key, _ in tabs]:
        st.session_state[session_key] = default
        active = default

    cols = st.columns(len(tabs))
    for col, (key, label) in zip(cols, tabs):
        with col:
            if st.button(
                label,
                key=f"tab_{session_key}_{key}",
                use_container_width=True,
                type="primary" if active == key else "secondary",
            ):
                if st.session_state[session_key] != key:
                    st.session_state[session_key] = key
                    st.rerun()

    return st.session_state[session_key]

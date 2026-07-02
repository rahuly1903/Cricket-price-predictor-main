"""Shared UI helpers for flash messages and tab navigation."""

import streamlit as st

from services.club_context import ClubContext


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


def render_club_selector(ctx: ClubContext, key_suffix: str = "default") -> dict | None:
    """Render a club dropdown and keep the active club in session state."""
    clubs = ctx.get_clubs()
    if not clubs:
        return None

    club_names = [club["name"] for club in clubs]
    active = ctx.get_active_club()
    default_index = club_names.index(active["name"]) if active and active["name"] in club_names else 0

    selected_name = st.selectbox(
        "Select Club",
        club_names,
        index=default_index,
        key=f"club_selector_{key_suffix}",
    )
    selected = next(club for club in clubs if club["name"] == selected_name)

    if ctx.get_active_club_id() != selected["id"]:
        ctx.set_active_club_id(selected["id"])
        st.rerun()

    return selected

"""Club management page."""

import streamlit as st

from services.club_context import ClubContext
from views.ui_helpers import navigate_to_teams, render_tab_selector, set_flash, show_flash


def _toggle_session_flag(key: str) -> None:
    st.session_state[key] = not st.session_state.get(key, False)


def render_club_page(user_id: str | None = None) -> None:
    ctx = ClubContext(user_id)

    if ctx.is_guest:
        st.markdown(
            """
            <div class="feature-card fade-in">
                <h2 style="color: #2E8B57;">🏟️ Club Management</h2>
                <p style="color: #666;">Create and manage multiple clubs without signing in. Data is saved on the server until you delete it.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.info("👋 Guest mode — your clubs are stored separately from logged-in accounts. Sign in to manage your own account data.")
    else:
        st.markdown(
            """
            <div class="feature-card fade-in">
                <h2 style="color: #2E8B57;">🏟️ Club Management</h2>
                <p style="color: #666;">Create and manage multiple cricket clubs. Each club can have its own teams and players.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    show_flash()

    if not ctx.is_guest:
        user = ctx.get_user()
        if not user:
            st.error("User not found. Please log in again.")
            return

    clubs = ctx.get_clubs()
    active_tab = render_tab_selector(
        "club_active_tab",
        [("list", "📋 All Clubs"), ("create", "➕ Create Club")],
        default="list" if clubs else "create",
    )

    if active_tab == "create":
        _render_create_club(ctx)
    else:
        _render_club_list(clubs, ctx)


def _render_create_club(ctx: ClubContext) -> None:
    st.markdown("### Create a New Club")

    with st.form("create_club_form"):
        name = st.text_input("Club Name", placeholder="e.g., Mumbai Strikers")
        description = st.text_area("Description", placeholder="Brief description of your club")
        submitted = st.form_submit_button("Create Club", use_container_width=True, type="primary")

        if submitted:
            if not name.strip():
                st.error("Club name is required.")
                return
            if ctx.club_name_exists(name.strip()):
                st.error(f"A club named '{name.strip()}' already exists.")
                return

            club = ctx.create_club(name.strip(), description.strip())
            st.session_state.club_active_tab = "list"
            set_flash("success", f"Club '{club['name']}' created successfully!")
            st.rerun()


def _render_club_list(clubs: list[dict], ctx: ClubContext) -> None:
    if not clubs:
        st.info("No clubs yet. Use the **Create Club** tab to add your first club.")
        return

    st.markdown(f"### Your Clubs ({len(clubs)})")
    st.caption("Click a club to open its teams. Use Edit to change club details.")

    for club in clubs:
        teams = ctx.get_club_teams(club["id"])
        players = ctx.get_club_players(club["id"])
        is_active = ctx.get_active_club_id() == club["id"]
        edit_visible_key = f"edit_club_visible_{club['id']}"

        open_col, edit_col = st.columns([10, 1])
        with open_col:
            label = f"{'✅ ' if is_active else '🏟️ '}{club['name']} — {len(teams)} team(s), {len(players)} player(s)"
            if st.button(
                label,
                key=f"open_club_{club['id']}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                navigate_to_teams(ctx, club["id"])
        with edit_col:
            if st.button("✏️", key=f"toggle_edit_{club['id']}", help="Edit club details"):
                _toggle_session_flag(edit_visible_key)
                st.rerun()

        if club.get("description") and not st.session_state.get(edit_visible_key):
            st.caption(club["description"])

        if st.session_state.get(edit_visible_key):
            with st.form(f"edit_club_{club['id']}"):
                new_name = st.text_input("Club Name", value=club.get("name", ""), key=f"club_name_{club['id']}")
                new_description = st.text_area(
                    "Description", value=club.get("description", ""), key=f"club_desc_{club['id']}"
                )
                save = st.form_submit_button("Save Changes", use_container_width=True, type="primary")

                if save:
                    if not new_name.strip():
                        st.error("Club name cannot be empty.")
                    elif ctx.club_name_exists(new_name.strip(), exclude_club_id=club["id"]):
                        st.error(f"A club named '{new_name.strip()}' already exists.")
                    else:
                        ctx.update_club(
                            club["id"],
                            {"name": new_name.strip(), "description": new_description.strip()},
                        )
                        set_flash("success", "Club saved successfully!")
                        st.rerun()

            if ctx.can_delete_club(club):
                st.markdown("---")
                if st.checkbox(
                    "I understand this will delete this club, its teams, and its players",
                    key=f"confirm_delete_{club['id']}",
                ):
                    if st.button(f"Delete {club['name']}", key=f"delete_club_{club['id']}", type="secondary"):
                        ctx.delete_club(club["id"])
                        set_flash("warning", f"Club '{club['name']}' deleted.")
                        st.rerun()

        st.markdown("---")

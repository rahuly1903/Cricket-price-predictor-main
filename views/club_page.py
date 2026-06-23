"""Club management page."""

import streamlit as st

from services import storage
from views.ui_helpers import set_flash, show_flash


def render_club_page(user_id: str) -> None:
    st.markdown(
        """
        <div class="feature-card fade-in">
            <h2 style="color: #2E8B57;">🏟️ Club Management</h2>
            <p style="color: #666;">Create and manage your cricket club. Each user can belong to one club only.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    show_flash()

    user = storage.find_by_id("users", user_id)
    if not user:
        st.error("User not found. Please log in again.")
        return

    club = storage.get_user_club(user_id)

    if club:
        _render_existing_club(club, user_id)
    else:
        _render_create_club(user_id)


def _render_create_club(user_id: str) -> None:
    st.info("You are not part of any club yet. Create your club to get started.")

    with st.form("create_club_form"):
        name = st.text_input("Club Name", placeholder="e.g., Mumbai Strikers")
        description = st.text_area("Description", placeholder="Brief description of your club")
        submitted = st.form_submit_button("Create Club", use_container_width=True, type="primary")

        if submitted:
            if not name.strip():
                st.error("Club name is required.")
                return

            club = storage.create_record(
                "clubs",
                {
                    "name": name.strip(),
                    "description": description.strip(),
                    "owner_user_id": user_id,
                },
            )
            storage.update_record("users", user_id, {"club_id": club["id"]})
            set_flash("success", f"Club '{club['name']}' saved successfully!")
            st.rerun()


def _render_existing_club(club: dict, user_id: str) -> None:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### {club['name']}")
        if club.get("description"):
            st.caption(club["description"])

    teams = storage.get_club_teams(club["id"])
    players = storage.get_club_players(club["id"])

    metric_col1, metric_col2, metric_col3 = st.columns(3)
    metric_col1.metric("Teams", len(teams))
    metric_col2.metric("Players", len(players))
    metric_col3.metric("Club ID", club["id"][:8] + "...")

    st.markdown("---")
    st.markdown("#### Quick Actions")
    action_col1, action_col2 = st.columns(2)
    with action_col1:
        if st.button("👥 Manage Teams", use_container_width=True, type="primary"):
            st.session_state.current_page = "🏏 Team Management"
            st.rerun()
    with action_col2:
        if st.button("🧑‍🤝‍🧑 Manage Players", use_container_width=True):
            st.session_state.current_page = "👤 Player Management"
            st.rerun()

    st.markdown("---")
    st.markdown("#### Edit Club")

    with st.form("edit_club_form"):
        new_name = st.text_input("Club Name", value=club.get("name", ""))
        new_description = st.text_area("Description", value=club.get("description", ""))
        save = st.form_submit_button("Save Changes", use_container_width=True, type="primary")

        if save:
            if not new_name.strip():
                st.error("Club name cannot be empty.")
            else:
                storage.update_record(
                    "clubs",
                    club["id"],
                    {"name": new_name.strip(), "description": new_description.strip()},
                )
                set_flash("success", "Club saved successfully!")
                st.rerun()

    if club.get("owner_user_id") == user_id:
        st.markdown("---")
        st.markdown("#### Danger Zone")
        if st.checkbox("I understand this will delete the club, all teams, and all players"):
            if st.button("Delete Club", type="secondary"):
                for player in storage.get_club_players(club["id"]):
                    storage.delete_record("players", player["id"])
                for team in storage.get_club_teams(club["id"]):
                    storage.delete_record("teams", team["id"])
                storage.delete_record("clubs", club["id"])
                storage.update_record("users", user_id, {"club_id": None})
                set_flash("warning", "Club deleted.")
                st.rerun()

"""Team management page."""

import streamlit as st

from services.club_context import ClubContext
from views.ui_helpers import render_tab_selector, set_flash, show_flash


def render_teams_for_club(club_id: str, ctx: ClubContext) -> None:
    """Render team list and details for a club (used inline on club page)."""
    teams = ctx.get_club_teams(club_id)
    if not teams:
        st.info("No teams yet for this club.")
        return
    _render_team_accordions(teams, club_id, ctx)


def render_team_page(user_id: str | None = None) -> None:
    ctx = ClubContext(user_id)

    if ctx.is_guest:
        st.markdown(
            """
            <div class="feature-card fade-in">
                <h2 style="color: #2E8B57;">🏏 Team Management</h2>
                <p style="color: #666;">Create and manage cricket teams across your clubs.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="feature-card fade-in">
                <h2 style="color: #2E8B57;">🏏 Team Management</h2>
                <p style="color: #666;">Create and manage cricket teams across your clubs.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    club = ctx.get_active_club()
    if not club:
        st.warning("You need to create a club first.")
        if st.button("Go to Club Management", type="primary"):
            st.session_state.current_page = "🏟️ Club Management"
            st.rerun()
        return

    teams = ctx.get_club_teams(club["id"])

    show_flash()

    st.markdown(
        """
        <style>
        [data-testid="stExpanderDetails"] [data-testid="stFormSubmitButton"] > button {
            background: linear-gradient(135deg, #2E8B57 0%, #32CD32 100%) !important;
            color: #ffffff !important;
            border: none !important;
            box-shadow: 0 4px 12px rgba(46, 139, 87, 0.3) !important;
            text-transform: none !important;
            letter-spacing: 0 !important;
        }
        [data-testid="stExpanderDetails"] [data-testid="stHorizontalBlock"] [data-testid="column"]:last-child [data-testid="stButton"] > button {
            background: #f9fafb !important;
            color: #6b7280 !important;
            border: 1px solid #e5e7eb !important;
            box-shadow: none !important;
            padding: 0.2rem 0.6rem !important;
            font-size: 0.8rem !important;
            text-transform: none !important;
            letter-spacing: 0 !important;
            min-height: 2rem !important;
        }
        [data-testid="stExpanderDetails"] [data-testid="stHorizontalBlock"] [data-testid="column"]:last-child [data-testid="stButton"] > button:hover {
            background: #f3f4f6 !important;
            color: #374151 !important;
            border-color: #d1d5db !important;
            transform: none !important;
        }
        [data-testid="stExpanderDetails"] > div > [data-testid="stVerticalBlock"]:last-child [data-testid="stButton"] > button {
            background: #dc2626 !important;
            color: #ffffff !important;
            border: none !important;
            box-shadow: none !important;
            text-transform: none !important;
            letter-spacing: 0 !important;
        }
        [data-testid="stExpanderDetails"] > div > [data-testid="stVerticalBlock"]:last-child [data-testid="stButton"] > button:hover {
            background: #b91c1c !important;
            color: #ffffff !important;
            transform: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    active_tab = render_tab_selector(
        "team_active_tab",
        [("list", "📋 All Teams"), ("create", "➕ Create Team")],
        default="list",
    )

    if active_tab == "create":
        _render_create_team(club, ctx)
    else:
        _render_team_accordions(teams, club["id"], ctx)


def _render_create_team(club: dict, ctx: ClubContext) -> None:
    with st.form("create_team_form"):
        name = st.text_input("Team Name", placeholder="e.g., First XI")
        description = st.text_area("Description", placeholder="Optional team description")
        submitted = st.form_submit_button("Create Team", use_container_width=True, type="primary")

        if submitted:
            if not name.strip():
                st.error("Team name is required.")
            elif ctx.team_name_exists(club["id"], name.strip()):
                st.error(f"A team named '{name.strip()}' already exists in this club.")
            else:
                ctx.create_team(club["id"], name.strip(), description.strip())
                st.session_state.team_active_tab = "list"
                set_flash("success", f"Team '{name.strip()}' saved successfully!")
                st.rerun()


def _render_team_accordions(teams: list[dict], club_id: str, ctx: ClubContext) -> None:
    if not teams:
        st.info("No teams yet. Create your first team using the Create Team tab.")
        return

    for team in teams:
        players = ctx.get_team_players(team["id"])
        player_count = len(players)
        player_preview = ", ".join(p.get("player_name", "") for p in players[:5])
        if player_count > 5:
            player_preview += f" +{player_count - 5} more"

        expander_label = f"🏏 {team['name']} — {player_count} player(s)"
        if player_preview:
            expander_label += f" — {player_preview}"

        with st.expander(expander_label, expanded=False):
            _render_team_details(team, club_id, players, ctx)


def _render_team_details(team: dict, club_id: str, players: list[dict], ctx: ClubContext) -> None:
    team_id = team["id"]

    with st.form(f"edit_team_{team_id}"):
        name = st.text_input("Team Name", value=team.get("name", ""), key=f"name_{team_id}")
        description = st.text_area("Description", value=team.get("description", ""), key=f"desc_{team_id}")
        save = st.form_submit_button("Save Changes", use_container_width=True, type="primary")

        if save:
            if not name.strip():
                st.error("Team name cannot be empty.")
            elif ctx.team_name_exists(club_id, name.strip(), exclude_team_id=team_id):
                st.error(f"A team named '{name.strip()}' already exists in this club.")
            else:
                ctx.update_team(
                    team_id,
                    {
                        "name": name.strip(),
                        "description": description.strip(),
                    },
                )
                st.session_state.team_active_tab = "list"
                set_flash("success", f"Team '{name.strip()}' saved successfully!")
                st.rerun()

    st.markdown("**Players**")
    if not players:
        st.caption("No players assigned to this team yet.")
    else:
        for player in players:
            player_col, action_col = st.columns([4, 2])
            with player_col:
                overseas = "Overseas" if player.get("is_overseas") else "Local"
                st.markdown(f"**{player.get('player_name', '')}** · {player.get('role', '')} · {overseas}")
            with action_col:
                if st.button(
                    "Remove from team",
                    key=f"remove_player_{team_id}_{player['id']}",
                    type="secondary",
                    use_container_width=True,
                ):
                    ctx.update_player(player["id"], {"team_id": None})
                    set_flash("success", f"Player '{player.get('player_name')}' removed from team.")
                    st.rerun()

    st.markdown("---")
    if st.button(f"Delete Team: {team['name']}", key=f"delete_team_{team_id}", type="secondary"):
        if players:
            st.error("Cannot delete a team that has players. Remove players from the team first.")
        else:
            ctx.delete_team(team_id)
            st.session_state.team_active_tab = "list"
            set_flash("success", f"Team '{team['name']}' deleted.")
            st.rerun()

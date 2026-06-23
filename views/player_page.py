"""Player management page with CSV import/export."""

import pandas as pd
import streamlit as st

from services import storage
from services.models import CSV_FIELDS, NUMERIC_PLAYER_FIELDS, PLAYER_FIELDS, PLAYER_ROLES
from views.ui_helpers import render_tab_selector, set_flash, show_flash

PLAYER_TABS = [
    ("list", "📋 All Players"),
    ("add", "➕ Add Player"),
    ("csv", "📁 CSV Import"),
]

UNASSIGNED_LABEL = "Unassigned"

SAMPLE_CSV_ROWS = [
    {
        "player_name": "Virat Kohli",
        "role": "Batsman",
        "is_overseas": 0,
        "runs_scored": 8000,
        "innings_batted": 200,
        "balls_faced": 0,
        "strike_rate": 133.3,
        "fours": 700,
        "sixes": 250,
        "wickets": 0,
        "balls_bowled": 0,
        "runs_conceded": 0,
        "economy": 0.0,
        "dot_balls": 0,
        "team": "First XI",
    },
    {
        "player_name": "Jasprit Bumrah",
        "role": "Bowler",
        "is_overseas": 0,
        "runs_scored": 50,
        "innings_batted": 20,
        "balls_faced": 40,
        "strike_rate": 125.0,
        "fours": 2,
        "sixes": 1,
        "wickets": 150,
        "balls_bowled": 0,
        "runs_conceded": 2400,
        "economy": 4.8,
        "dot_balls": 1200,
        "team": "",
    },
]


def get_sample_csv_bytes() -> bytes:
    df = pd.DataFrame(SAMPLE_CSV_ROWS, columns=CSV_FIELDS)
    return df.to_csv(index=False).encode("utf-8")


def _empty_player_stats() -> dict:
    return {field: 0 if field in NUMERIC_PLAYER_FIELDS else "" for field in PLAYER_FIELDS}


def _resolve_team_id(team_name: str, team_options: dict[str, str]) -> tuple[str | None, str | None]:
    name = str(team_name).strip()
    if not name or name.lower() in {"nan", "none"}:
        return None, None
    for label, team_id in team_options.items():
        if label.lower() == name.lower():
            return team_id, None
    return None, f"Unknown team '{name}'. Leave blank to keep unassigned."


def _derive_balls_bowled_if_missing(payload: dict) -> None:
    """Estimate balls_bowled from runs_conceded and economy when not provided."""
    if payload["balls_bowled"] == 0 and payload["runs_conceded"] > 0 and payload["economy"] > 0:
        payload["balls_bowled"] = int(round((payload["runs_conceded"] / payload["economy"]) * 6))


def _derive_balls_faced_if_missing(payload: dict) -> None:
    """Estimate balls_faced from runs_scored and strike_rate when not provided."""
    if payload["balls_faced"] == 0 and payload["runs_scored"] > 0 and payload["strike_rate"] > 0:
        payload["balls_faced"] = int(round((payload["runs_scored"] / payload["strike_rate"]) * 100))


def _derive_missing_stats(payload: dict) -> None:
    _derive_balls_faced_if_missing(payload)
    _derive_balls_bowled_if_missing(payload)


def _validate_player_row(
    row: dict,
    club_id: str,
    team_id: str | None = None,
    exclude_player_id: str | None = None,
    auto_derive_stats: bool = False,
) -> tuple[dict | None, str | None]:
    name = str(row.get("player_name", "")).strip()
    if not name:
        return None, "Player name is required."

    role = str(row.get("role", "Batsman")).strip()
    if role not in PLAYER_ROLES:
        return None, f"Invalid role '{role}'. Must be one of: {', '.join(PLAYER_ROLES)}."

    for player in storage.get_club_players(club_id):
        if exclude_player_id and player.get("id") == exclude_player_id:
            continue
        if player.get("player_name", "").lower() == name.lower():
            return None, f"Player '{name}' already exists in this club."

    if team_id:
        for player in storage.get_team_players(team_id):
            if exclude_player_id and player.get("id") == exclude_player_id:
                continue
            if player.get("player_name", "").lower() == name.lower():
                return None, f"Player '{name}' is already on this team."

    payload = _empty_player_stats()
    payload["player_name"] = name
    payload["role"] = role

    for field in NUMERIC_PLAYER_FIELDS:
        value = row.get(field, 0)
        try:
            if field == "is_overseas":
                payload[field] = 1 if str(value).strip().lower() in {"1", "true", "yes"} else 0
            elif field in {"strike_rate", "economy"}:
                payload[field] = float(value)
            else:
                payload[field] = int(float(value))
        except (TypeError, ValueError):
            return None, f"Invalid numeric value for '{field}'."

    if auto_derive_stats:
        _derive_missing_stats(payload)

    payload["club_id"] = club_id
    payload["team_id"] = team_id
    return payload, None


def _player_form_fields(prefix: str, defaults: dict | None = None) -> dict:
    defaults = defaults or _empty_player_stats()
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Player Name", value=defaults.get("player_name", ""), key=f"{prefix}_name")
        role = st.selectbox(
            "Role",
            PLAYER_ROLES,
            index=PLAYER_ROLES.index(defaults.get("role", "Batsman")) if defaults.get("role") in PLAYER_ROLES else 0,
            key=f"{prefix}_role",
        )
    with col2:
        overseas = st.checkbox(
            "Overseas Player",
            value=bool(defaults.get("is_overseas", 0)),
            key=f"{prefix}_overseas",
        )

    st.markdown("**Batting Statistics**")
    b1, b2, b3 = st.columns(3)
    with b1:
        runs = st.number_input("Runs Scored", 0, 50000, int(defaults.get("runs_scored", 0)), key=f"{prefix}_runs")
        innings = st.number_input("Innings Batted", 0, 1000, int(defaults.get("innings_batted", 0)), key=f"{prefix}_innings")
    with b2:
        balls_faced = st.number_input("Balls Faced", 0, 50000, int(defaults.get("balls_faced", 0)), key=f"{prefix}_balls_faced")
        sr = st.number_input("Strike Rate", 0.0, 300.0, float(defaults.get("strike_rate", 0.0)), key=f"{prefix}_sr")
    with b3:
        fours = st.number_input("Fours", 0, 2000, int(defaults.get("fours", 0)), key=f"{prefix}_fours")
        sixes = st.number_input("Sixes", 0, 2000, int(defaults.get("sixes", 0)), key=f"{prefix}_sixes")

    st.markdown("**Bowling Statistics**")
    w1, w2, w3 = st.columns(3)
    with w1:
        wickets = st.number_input("Wickets", 0, 1000, int(defaults.get("wickets", 0)), key=f"{prefix}_wickets")
        balls_bowled = st.number_input("Balls Bowled", 0, 50000, int(defaults.get("balls_bowled", 0)), key=f"{prefix}_balls_bowled")
    with w2:
        runs_conceded = st.number_input("Runs Conceded", 0, 50000, int(defaults.get("runs_conceded", 0)), key=f"{prefix}_runs_conceded")
        economy = st.number_input("Economy", 0.0, 200.0, float(defaults.get("economy", 0.0)), key=f"{prefix}_economy")
    with w3:
        dot_balls = st.number_input("Dot Balls", 0, 50000, int(defaults.get("dot_balls", 0)), key=f"{prefix}_dot_balls")

    return {
        "player_name": name,
        "role": role,
        "is_overseas": 1 if overseas else 0,
        "runs_scored": runs,
        "innings_batted": innings,
        "balls_faced": balls_faced,
        "strike_rate": sr,
        "fours": fours,
        "sixes": sixes,
        "wickets": wickets,
        "balls_bowled": balls_bowled,
        "runs_conceded": runs_conceded,
        "economy": economy,
        "dot_balls": dot_balls,
    }


def _team_label(team_id: str | None, team_options: dict[str, str]) -> str:
    if not team_id:
        return UNASSIGNED_LABEL
    for name, tid in team_options.items():
        if tid == team_id:
            return name
    return "Unknown"


def render_player_page(user_id: str) -> None:
    st.markdown(
        """
        <div class="feature-card fade-in">
            <h2 style="color: #2E8B57;">👤 Player Management</h2>
            <p style="color: #666;">Add, edit, and assign players. Each player can belong to one team only.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    club = storage.get_user_club(user_id)
    if not club:
        st.warning("You need to create a club first.")
        if st.button("Go to Club Management", type="primary"):
            st.session_state.current_page = "🏟️ Club Management"
            st.rerun()
        return

    teams = storage.get_club_teams(club["id"])
    team_options = {team["name"]: team["id"] for team in teams}
    team_names = list(team_options.keys())
    team_assignment_options = [UNASSIGNED_LABEL] + team_names

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
        [data-testid="stExpanderDetails"] [data-testid="stHorizontalBlock"]:last-of-type
        [data-testid="column"]:last-child [data-testid="stButton"] > button {
            background: #dc2626 !important;
            color: #ffffff !important;
            border: none !important;
            box-shadow: none !important;
            text-transform: none !important;
            letter-spacing: 0 !important;
        }
        [data-testid="stExpanderDetails"] [data-testid="stHorizontalBlock"]:last-of-type
        [data-testid="column"]:last-child [data-testid="stButton"] > button:hover {
            background: #b91c1c !important;
            color: #ffffff !important;
            transform: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    active_tab = render_tab_selector("player_active_tab", PLAYER_TABS, default="list")
    players = storage.get_club_players(club["id"])

    if active_tab == "add":
        _render_add_player(club["id"])
    elif active_tab == "csv":
        _render_csv_import(club["id"], team_options)
    else:
        _render_player_list(club["id"], players, team_options, team_names, team_assignment_options)


def _render_add_player(club_id: str) -> None:
    st.info("New players are created without a team. Assign them to a team from the All Players tab.")

    with st.form("add_player_form"):
        form_data = _player_form_fields("add")
        submitted = st.form_submit_button("Add Player", use_container_width=True, type="primary")

        if submitted:
            payload, error = _validate_player_row(form_data, club_id, team_id=None)
            if error:
                st.error(error)
            else:
                storage.create_record("players", payload)
                st.session_state.player_active_tab = "list"
                set_flash("success", f"Player '{payload['player_name']}' saved successfully!")
                st.rerun()


def _render_csv_import(club_id: str, team_options: dict[str, str]) -> None:
    st.markdown("### Upload Players via CSV")
    st.markdown(
        "Download the sample CSV, fill in your player data, then upload it. "
        "Use the **team** column at the end to assign players (leave blank to keep unassigned). "
        "If **balls_faced** is 0 but **runs_scored** and **strike_rate** are provided, balls faced are calculated automatically. "
        "If **balls_bowled** is 0 but **runs_conceded** and **economy** are provided, balls bowled are calculated automatically."
    )

    st.download_button(
        label="⬇️ Download Sample CSV",
        data=get_sample_csv_bytes(),
        file_name="player_upload_sample.csv",
        mime="text/csv",
        use_container_width=True,
    )

    uploaded = st.file_uploader("Upload Player CSV", type=["csv"], key="player_csv_upload")

    if uploaded:
        try:
            df = pd.read_csv(uploaded)
        except Exception as exc:
            st.error(f"Could not read CSV: {exc}")
            return

        missing = [col for col in PLAYER_FIELDS if col not in df.columns]
        if missing:
            st.error(f"CSV is missing required columns: {', '.join(missing)}")
        else:
            st.dataframe(df.head(), use_container_width=True)
            if st.button("Import Players from CSV", type="primary", use_container_width=True):
                success_count = 0
                errors = []
                for index, row in df.iterrows():
                    row_dict = row.to_dict()
                    team_id, team_error = _resolve_team_id(row_dict.get("team", ""), team_options)
                    if team_error:
                        errors.append(f"Row {index + 2}: {team_error}")
                        continue

                    payload, error = _validate_player_row(
                        row_dict, club_id, team_id=team_id, auto_derive_stats=True
                    )
                    if error:
                        errors.append(f"Row {index + 2}: {error}")
                    else:
                        storage.create_record("players", payload)
                        success_count += 1

                if success_count:
                    st.session_state.player_active_tab = "list"
                    set_flash("success", f"{success_count} player(s) saved successfully!")
                if errors:
                    st.session_state.csv_import_errors = errors[:10]
                if success_count or errors:
                    st.rerun()


def _render_player_accordion(
    player: dict,
    club_id: str,
    team_options: dict[str, str],
    team_assignment_options: list[str],
) -> None:
    player_id = player["id"]
    team_name = _team_label(player.get("team_id"), team_options)
    overseas = "Overseas" if player.get("is_overseas") else "Local"

    with st.expander(f"🏏 {player.get('player_name')} — {player.get('role')} | {team_name} | {overseas}"):
        current_team_label = team_name if team_name in team_assignment_options else UNASSIGNED_LABEL

        with st.form(f"edit_player_{player_id}"):
            if team_assignment_options == [UNASSIGNED_LABEL]:
                st.caption("No teams created yet. Create a team first to assign players.")
                new_team = UNASSIGNED_LABEL
            else:
                new_team = st.selectbox(
                    "Assign to Team",
                    team_assignment_options,
                    index=team_assignment_options.index(current_team_label),
                    key=f"edit_team_{player_id}",
                )

            form_data = _player_form_fields(f"edit_{player_id}", player)
            save = st.form_submit_button("Save Changes", use_container_width=True, type="primary")

            if save:
                new_team_id = None if new_team == UNASSIGNED_LABEL else team_options.get(new_team)
                if new_team_id:
                    for other in storage.get_team_players(new_team_id):
                        if (
                            other.get("id") != player_id
                            and other.get("player_name", "").lower() == form_data["player_name"].lower()
                        ):
                            st.error(f"Player '{form_data['player_name']}' is already on {new_team}.")
                            return

                payload, error = _validate_player_row(
                    form_data,
                    club_id,
                    team_id=new_team_id,
                    exclude_player_id=player_id,
                )
                if error:
                    st.error(error)
                else:
                    storage.update_record("players", player_id, payload)
                    st.session_state.player_active_tab = "list"
                    set_flash("success", f"Player '{payload['player_name']}' saved successfully!")
                    st.rerun()

        action_col1, action_col2 = st.columns(2)
        with action_col1:
            export_df = pd.DataFrame(
                [{field: player.get(field) for field in PLAYER_FIELDS}],
                columns=PLAYER_FIELDS,
            )
            st.download_button(
                "Export as CSV",
                data=export_df.to_csv(index=False).encode("utf-8"),
                file_name=f"{player.get('player_name', 'player')}.csv",
                mime="text/csv",
                key=f"export_{player_id}",
                use_container_width=True,
            )
        with action_col2:
            if st.button("Delete", key=f"delete_player_{player_id}", type="secondary", use_container_width=True):
                storage.delete_record("players", player_id)
                set_flash("success", f"Player '{player.get('player_name')}' deleted.")
                st.rerun()


def _render_player_list(
    club_id: str,
    players: list[dict],
    team_options: dict[str, str],
    team_names: list[str],
    team_assignment_options: list[str],
) -> None:
    csv_errors = st.session_state.pop("csv_import_errors", None)
    if csv_errors:
        st.error("Some rows could not be imported:")
        for err in csv_errors:
            st.write(f"- {err}")

    if not players:
        st.info("No players yet. Add players manually or via CSV.")
        return

    filter_options = ["All Teams", UNASSIGNED_LABEL] + team_names
    filter_team = st.selectbox("Filter by team", filter_options, key="filter_team")
    filtered = players
    if filter_team == UNASSIGNED_LABEL:
        filtered = [p for p in players if not p.get("team_id")]
    elif filter_team != "All Teams":
        team_id = team_options[filter_team]
        filtered = [p for p in players if p.get("team_id") == team_id]

    st.markdown(f"**{len(filtered)} player(s)** — expand a player below to edit or assign to a team.")

    for player in filtered:
        _render_player_accordion(player, club_id, team_options, team_assignment_options)

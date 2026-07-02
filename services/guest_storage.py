"""Persistent JSON storage for guest (pre-login) club, team, and player data."""

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

COLLECTION_FILES = {
    "clubs": "guest_clubs.json",
    "teams": "guest_teams.json",
    "players": "guest_players.json",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id() -> str:
    return str(uuid.uuid4())


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _file_path(collection: str) -> Path:
    if collection not in COLLECTION_FILES:
        raise ValueError(f"Unknown guest collection: {collection}")
    return DATA_DIR / COLLECTION_FILES[collection]


def _default_payload(collection: str) -> dict[str, Any]:
    return {collection: []}


def load_collection(collection: str) -> dict[str, Any]:
    _ensure_data_dir()
    path = _file_path(collection)
    if not path.exists():
        payload = _default_payload(collection)
        save_collection(collection, payload)
        return payload

    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def save_collection(collection: str, payload: dict[str, Any]) -> None:
    _ensure_data_dir()
    path = _file_path(collection)
    temp_path = path.with_suffix(".tmp")
    with open(temp_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    os.replace(temp_path, path)


def _get_all(collection: str) -> list[dict[str, Any]]:
    return load_collection(collection).get(collection, [])


def _save_all(collection: str, records: list[dict[str, Any]]) -> None:
    save_collection(collection, {collection: records})


def get_clubs() -> list[dict[str, Any]]:
    return _get_all("clubs")


def get_club_by_id(club_id: str) -> dict[str, Any] | None:
    for club in get_clubs():
        if club.get("id") == club_id:
            return club
    return None


def find_club_by_name(name: str) -> dict[str, Any] | None:
    name_lower = name.strip().lower()
    for club in get_clubs():
        if club.get("name", "").lower() == name_lower:
            return club
    return None


def club_name_exists(name: str, exclude_club_id: str | None = None) -> bool:
    name_lower = name.strip().lower()
    for club in get_clubs():
        if exclude_club_id and club.get("id") == exclude_club_id:
            continue
        if club.get("name", "").lower() == name_lower:
            return True
    return False


def create_club(name: str, description: str) -> dict[str, Any]:
    clubs = get_clubs()
    club = {
        "id": _new_id(),
        "created_at": _now_iso(),
        "name": name,
        "description": description,
        "owner_user_id": None,
    }
    clubs.append(club)
    _save_all("clubs", clubs)
    return club


def update_club(club_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
    clubs = get_clubs()
    for index, club in enumerate(clubs):
        if club.get("id") == club_id:
            updated = {**club, **updates, "updated_at": _now_iso()}
            clubs[index] = updated
            _save_all("clubs", clubs)
            return updated
    return None


def delete_club(club_id: str) -> bool:
    clubs = get_clubs()
    original_len = len(clubs)
    clubs = [club for club in clubs if club.get("id") != club_id]
    if len(clubs) == original_len:
        return False

    _save_all("clubs", clubs)
    _save_all("teams", [team for team in _get_all("teams") if team.get("club_id") != club_id])
    _save_all("players", [player for player in _get_all("players") if player.get("club_id") != club_id])
    return True


def get_club_teams(club_id: str) -> list[dict[str, Any]]:
    return [team for team in _get_all("teams") if team.get("club_id") == club_id]


def get_club_players(club_id: str) -> list[dict[str, Any]]:
    return [player for player in _get_all("players") if player.get("club_id") == club_id]


def get_team_players(team_id: str) -> list[dict[str, Any]]:
    return [player for player in _get_all("players") if player.get("team_id") == team_id]


def team_name_exists(club_id: str, name: str, exclude_team_id: str | None = None) -> bool:
    name_lower = name.strip().lower()
    for team in get_club_teams(club_id):
        if exclude_team_id and team.get("id") == exclude_team_id:
            continue
        if team.get("name", "").lower() == name_lower:
            return True
    return False


def create_team(club_id: str, name: str, description: str) -> dict[str, Any]:
    teams = _get_all("teams")
    team = {
        "id": _new_id(),
        "created_at": _now_iso(),
        "club_id": club_id,
        "name": name,
        "description": description,
    }
    teams.append(team)
    _save_all("teams", teams)
    return team


def update_team(team_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
    teams = _get_all("teams")
    for index, team in enumerate(teams):
        if team.get("id") == team_id:
            updated = {**team, **updates, "updated_at": _now_iso()}
            teams[index] = updated
            _save_all("teams", teams)
            return updated
    return None


def delete_team(team_id: str) -> bool:
    teams = _get_all("teams")
    original_len = len(teams)
    teams = [team for team in teams if team.get("id") != team_id]
    if len(teams) == original_len:
        return False
    _save_all("teams", teams)
    return True


def create_player(payload: dict[str, Any]) -> dict[str, Any]:
    players = _get_all("players")
    record = {"id": _new_id(), "created_at": _now_iso(), **payload}
    players.append(record)
    _save_all("players", players)
    return record


def update_player(player_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
    players = _get_all("players")
    for index, player in enumerate(players):
        if player.get("id") == player_id:
            updated = {**player, **updates, "updated_at": _now_iso()}
            players[index] = updated
            _save_all("players", players)
            return updated
    return None


def delete_player(player_id: str) -> bool:
    players = _get_all("players")
    original_len = len(players)
    players = [player for player in players if player.get("id") != player_id]
    if len(players) == original_len:
        return False
    _save_all("players", players)
    return True

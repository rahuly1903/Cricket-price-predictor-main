"""JSON file storage layer for users, clubs, teams, and players."""

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

COLLECTION_FILES = {
    "users": "users.json",
    "clubs": "clubs.json",
    "teams": "teams.json",
    "players": "players.json",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _file_path(collection: str) -> Path:
    if collection not in COLLECTION_FILES:
        raise ValueError(f"Unknown collection: {collection}")
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


def new_id() -> str:
    return str(uuid.uuid4())


def get_all(collection: str) -> list[dict[str, Any]]:
    return load_collection(collection).get(collection, [])


def find_by_id(collection: str, record_id: str) -> dict[str, Any] | None:
    for record in get_all(collection):
        if record.get("id") == record_id:
            return record
    return None


def create_record(collection: str, data: dict[str, Any]) -> dict[str, Any]:
    payload = load_collection(collection)
    record = {"id": new_id(), "created_at": _now_iso(), **data}
    payload[collection].append(record)
    save_collection(collection, payload)
    return record


def update_record(collection: str, record_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
    payload = load_collection(collection)
    for index, record in enumerate(payload[collection]):
        if record.get("id") == record_id:
            updated = {**record, **updates, "updated_at": _now_iso()}
            payload[collection][index] = updated
            save_collection(collection, payload)
            return updated
    return None


def delete_record(collection: str, record_id: str) -> bool:
    payload = load_collection(collection)
    original_len = len(payload[collection])
    payload[collection] = [r for r in payload[collection] if r.get("id") != record_id]
    if len(payload[collection]) == original_len:
        return False
    save_collection(collection, payload)
    return True


def get_user_club(user_id: str) -> dict[str, Any] | None:
    user = find_by_id("users", user_id)
    if not user or not user.get("club_id"):
        return None
    return find_by_id("clubs", user["club_id"])


def get_club_teams(club_id: str) -> list[dict[str, Any]]:
    return [team for team in get_all("teams") if team.get("club_id") == club_id]


def get_club_players(club_id: str) -> list[dict[str, Any]]:
    return [player for player in get_all("players") if player.get("club_id") == club_id]


def get_team_players(team_id: str) -> list[dict[str, Any]]:
    return [player for player in get_all("players") if player.get("team_id") == team_id]


def get_unassigned_club_players(club_id: str) -> list[dict[str, Any]]:
    return [
        player
        for player in get_club_players(club_id)
        if not player.get("team_id")
    ]


def team_name_exists(club_id: str, name: str, exclude_team_id: str | None = None) -> bool:
    name_lower = name.strip().lower()
    for team in get_club_teams(club_id):
        if exclude_team_id and team.get("id") == exclude_team_id:
            continue
        if team.get("name", "").lower() == name_lower:
            return True
    return False


def username_exists(username: str, exclude_user_id: str | None = None) -> bool:
    username_lower = username.strip().lower()
    for user in get_all("users"):
        if exclude_user_id and user.get("id") == exclude_user_id:
            continue
        if user.get("username", "").lower() == username_lower:
            return True
    return False


def email_exists(email: str, exclude_user_id: str | None = None) -> bool:
    email_lower = email.strip().lower()
    for user in get_all("users"):
        if exclude_user_id and user.get("id") == exclude_user_id:
            continue
        if user.get("email", "").lower() == email_lower:
            return True
    return False

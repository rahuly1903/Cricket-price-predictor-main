"""Unified data access for authenticated users and guest (pre-login) data."""

from dataclasses import dataclass
from typing import Any

import streamlit as st

from services import guest_storage, storage


@dataclass
class ClubContext:
    user_id: str | None

    @property
    def is_guest(self) -> bool:
        return self.user_id is None

    def _active_club_session_key(self) -> str:
        if self.is_guest:
            return "active_club_id_guest"
        return f"active_club_id_{self.user_id}"

    def get_active_club_id(self) -> str | None:
        return st.session_state.get(self._active_club_session_key())

    def set_active_club_id(self, club_id: str) -> None:
        st.session_state[self._active_club_session_key()] = club_id

    def get_user(self) -> dict[str, Any] | None:
        if self.is_guest:
            return None
        return storage.find_by_id("users", self.user_id)

    def get_clubs(self) -> list[dict[str, Any]]:
        if self.is_guest:
            return guest_storage.get_clubs()
        return storage.get_user_clubs(self.user_id)

    def get_club_by_id(self, club_id: str) -> dict[str, Any] | None:
        if self.is_guest:
            return guest_storage.get_club_by_id(club_id)
        for club in self.get_clubs():
            if club.get("id") == club_id:
                return club
        return None

    def find_club_by_name(self, name: str) -> dict[str, Any] | None:
        if self.is_guest:
            return guest_storage.find_club_by_name(name)
        return storage.find_club_by_name_for_user(self.user_id, name)

    def club_name_exists(self, name: str, exclude_club_id: str | None = None) -> bool:
        if self.is_guest:
            return guest_storage.club_name_exists(name, exclude_club_id)
        return storage.club_name_exists_for_user(self.user_id, name, exclude_club_id)

    def get_active_club(self) -> dict[str, Any] | None:
        clubs = self.get_clubs()
        if not clubs:
            return None

        active_id = self.get_active_club_id()
        if active_id:
            for club in clubs:
                if club.get("id") == active_id:
                    return club

        self.set_active_club_id(clubs[0]["id"])
        return clubs[0]

    def get_club(self) -> dict[str, Any] | None:
        return self.get_active_club()

    def create_club(self, name: str, description: str) -> dict[str, Any]:
        if self.is_guest:
            club = guest_storage.create_club(name, description)
        else:
            club = storage.create_record(
                "clubs",
                {
                    "name": name,
                    "description": description,
                    "owner_user_id": self.user_id,
                },
            )
            storage.update_record("users", self.user_id, {"club_id": club["id"]})

        self.set_active_club_id(club["id"])
        return club

    def update_club(self, club_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
        if self.is_guest:
            return guest_storage.update_club(club_id, updates)
        return storage.update_record("clubs", club_id, updates)

    def delete_club(self, club_id: str) -> bool:
        if self.is_guest:
            deleted = guest_storage.delete_club(club_id)
        else:
            for player in storage.get_club_players(club_id):
                storage.delete_record("players", player["id"])
            for team in storage.get_club_teams(club_id):
                storage.delete_record("teams", team["id"])
            deleted = storage.delete_record("clubs", club_id)
            user = self.get_user()
            if user and user.get("club_id") == club_id:
                storage.update_record("users", self.user_id, {"club_id": None})

        if deleted and self.get_active_club_id() == club_id:
            remaining = self.get_clubs()
            if remaining:
                self.set_active_club_id(remaining[0]["id"])
            else:
                st.session_state.pop(self._active_club_session_key(), None)

        return deleted

    def get_club_teams(self, club_id: str) -> list[dict[str, Any]]:
        if self.is_guest:
            return guest_storage.get_club_teams(club_id)
        return storage.get_club_teams(club_id)

    def get_club_players(self, club_id: str) -> list[dict[str, Any]]:
        if self.is_guest:
            return guest_storage.get_club_players(club_id)
        return storage.get_club_players(club_id)

    def get_all_players(self) -> list[dict[str, Any]]:
        players: list[dict[str, Any]] = []
        for club in self.get_clubs():
            players.extend(self.get_club_players(club["id"]))
        return players

    def get_team_players(self, team_id: str) -> list[dict[str, Any]]:
        if self.is_guest:
            return guest_storage.get_team_players(team_id)
        return storage.get_team_players(team_id)

    def team_name_exists(self, club_id: str, name: str, exclude_team_id: str | None = None) -> bool:
        if self.is_guest:
            return guest_storage.team_name_exists(club_id, name, exclude_team_id)
        return storage.team_name_exists(club_id, name, exclude_team_id)

    def create_team(self, club_id: str, name: str, description: str) -> dict[str, Any]:
        if self.is_guest:
            return guest_storage.create_team(club_id, name, description)
        return storage.create_record(
            "teams",
            {
                "club_id": club_id,
                "name": name,
                "description": description,
            },
        )

    def update_team(self, team_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
        if self.is_guest:
            return guest_storage.update_team(team_id, updates)
        return storage.update_record("teams", team_id, updates)

    def delete_team(self, team_id: str) -> bool:
        if self.is_guest:
            return guest_storage.delete_team(team_id)
        return storage.delete_record("teams", team_id)

    def create_player(self, payload: dict[str, Any]) -> dict[str, Any]:
        if self.is_guest:
            return guest_storage.create_player(payload)
        return storage.create_record("players", payload)

    def update_player(self, player_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
        if self.is_guest:
            return guest_storage.update_player(player_id, updates)
        return storage.update_record("players", player_id, updates)

    def delete_player(self, player_id: str) -> bool:
        if self.is_guest:
            return guest_storage.delete_player(player_id)
        return storage.delete_record("players", player_id)

    def can_delete_club(self, club: dict[str, Any]) -> bool:
        if self.is_guest:
            return True
        return club.get("owner_user_id") == self.user_id

    def can_access_club(self, club_id: str) -> bool:
        return any(club.get("id") == club_id for club in self.get_clubs())

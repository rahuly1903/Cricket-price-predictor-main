"""Data models and constants for club management."""

from typing import Literal

PLAYER_ROLES = ["Batsman", "Bowler", "All-Rounder", "Wicketkeeper"]
TEAM_FORMATS = ["T20", "ODI", "Test"]

PLAYER_FIELDS = [
    "player_name",
    "role",
    "is_overseas",
    "runs_scored",
    "innings_batted",
    "balls_faced",
    "strike_rate",
    "fours",
    "sixes",
    "wickets",
    "balls_bowled",
    "runs_conceded",
    "economy",
    "dot_balls",
]

CSV_FIELDS = PLAYER_FIELDS + ["team"]

NUMERIC_PLAYER_FIELDS = [
    "is_overseas",
    "runs_scored",
    "innings_batted",
    "balls_faced",
    "strike_rate",
    "fours",
    "sixes",
    "wickets",
    "balls_bowled",
    "runs_conceded",
    "economy",
    "dot_balls",
]

RoleType = Literal["Batsman", "Bowler", "All-Rounder", "Wicketkeeper"]
FormatType = Literal["T20", "ODI", "Test"]

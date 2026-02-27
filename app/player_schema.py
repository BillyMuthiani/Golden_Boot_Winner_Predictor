# app/player_schema.py

from dataclasses import dataclass


@dataclass
class PlayerStats:
    player: str
    team: str
    goals: int
    xg: float
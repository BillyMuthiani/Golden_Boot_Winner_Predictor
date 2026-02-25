import soccerdata as sd
import pandas as pd
import os


def generate_data(league: str, season: str):

    print(f"Fetching {league} data for {season}...")

    understat = sd.Understat(leagues=league, seasons=season)

    player_stats = understat.read_player_season_stats().reset_index()
    schedule = understat.read_schedule().reset_index()

    # Safe filename formatting
    safe_league = league.replace(" ", "-")

    player_path = f"data/player_stats_{safe_league}_{season}.csv"
    schedule_path = f"data/schedule_{safe_league}_{season}.csv"

    player_stats.to_csv(player_path, index=False)
    schedule.to_csv(schedule_path, index=False)

    print("CSV files saved successfully.")
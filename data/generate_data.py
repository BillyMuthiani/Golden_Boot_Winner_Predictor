# generate_data.py

import soccerdata as sd
import pandas as pd
import os


def fetch_data(league: str, season: str):
    """
    Fetch player stats and schedule from Understat
    and overwrite CSV files.
    """

    print(f"Fetching data for {league} - {season}")

    try:
        understat = sd.Understat(
            leagues=league,
            seasons=season
        )

        player_stats = understat.read_player_season_stats().reset_index()
        schedule = understat.read_schedule().reset_index()

        # Ensure data folder exists
        os.makedirs("data", exist_ok=True)

        # Overwrite CSV files
        player_stats.to_csv("data/player_stats.csv", index=False)
        schedule.to_csv("data/schedule.csv", index=False)

        print("Data successfully saved to CSV.")

    except Exception as e:
        print("Error fetching data:", e)
        raise e


# Optional CLI support
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python generate_data.py 'ENG-Premier League' 2025")
        sys.exit(1)

    league_arg = sys.argv[1]
    season_arg = sys.argv[2]

    fetch_data(league_arg, season_arg)
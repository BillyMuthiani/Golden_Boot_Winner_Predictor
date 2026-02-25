import soccerdata as sd
import pandas as pd

print("Fetching Understat data...")

understat = sd.Understat(leagues='ENG-Premier League', seasons='2025')

player_stats = understat.read_player_season_stats().reset_index()
schedule = understat.read_schedule().reset_index()

player_stats.to_csv("data/player_stats.csv", index=False)
schedule.to_csv("data/schedule.csv", index=False)

print("CSV files saved successfully.")
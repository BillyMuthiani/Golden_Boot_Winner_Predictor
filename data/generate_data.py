# app/generate_data.py

import soccerdata as sd
import pandas as pd


def fetch_player_data(league: str, season: int) -> pd.DataFrame:
    """
    Fetch player season stats from Understat.
    Returns a pandas DataFrame.
    """

    understat = sd.Understat(
        leagues=[league],
        seasons=[season]
    )

    df = understat.read_player_season_stats().reset_index()

    # Keep only required columns
    df = df[[
        "player",
        "team",
        "goals",
        "xg"
    ]]

    return df
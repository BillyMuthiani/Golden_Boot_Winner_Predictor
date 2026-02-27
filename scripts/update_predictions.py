# scripts/update_predictions.py

import os
from datetime import datetime

from app.database import SessionLocal
from app.models import Prediction
from data.generate_data import fetch_player_data
from app.simulator import run_monte_carlo
from app.player_schema import PlayerStats


LEAGUE = "ENG-Premier League"
SEASON = 2025


def main():

    print("Fetching player data...")
    df = fetch_player_data(LEAGUE, SEASON)

    print("Converting to PlayerStats...")
    players = [
        PlayerStats(
            player=row["player"],
            team=row["team"],
            goals=int(row["goals"]),
            xg=float(row["xg"])
        )
        for _, row in df.iterrows()
    ]

    print("Running simulation...")
    probabilities = run_monte_carlo(players)

    db = SessionLocal()

    try:
        print("Clearing old predictions...")
        db.query(Prediction).filter(
            Prediction.league == LEAGUE,
            Prediction.season == SEASON
        ).delete()

        print("Inserting new predictions...")
        for player_name, prob in probabilities.items():

            db.add(
                Prediction(
                    player=player_name,
                    team=next(p.team for p in players if p.player == player_name),
                    probability=prob,
                    league=LEAGUE,
                    season=SEASON,
                    computed_at=datetime.utcnow()
                )
            )

        db.commit()
        print("Update complete.")

    finally:
        db.close()


if __name__ == "__main__":
    main()
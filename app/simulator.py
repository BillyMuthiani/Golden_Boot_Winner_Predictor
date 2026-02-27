# app/simulator.py

import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from app.models import Prediction

N_SIMULATIONS = 100_000


def run_golden_boot_simulation(db: Session, league: str):

    df = pd.read_csv("data/player_stats.csv")

    player_names = df["player"].values
    lambdas = df["xg"].values

    simulations = np.random.poisson(
        lam=lambdas,
        size=(N_SIMULATIONS, len(df))
    )

    winners = np.argmax(simulations, axis=1)
    win_counts = np.bincount(winners, minlength=len(df))
    probabilities = win_counts / N_SIMULATIONS

    # delete old league predictions
    db.query(Prediction).filter(Prediction.league == league).delete()

    results = []

    for i, row in df.iterrows():
        prediction = Prediction(
            league=league,
            player=row["player"],
            team=row["team"],
            goals=int(row["goals"]),
            xg=float(row["xg"]),
            adjusted_xg_per_90=float(row.get("adjusted_xg_per_90", 0)),
            finishing_diff_per_90=float(row.get("finishing_diff_per_90", 0)),
            remaining_xg_adjusted=float(row.get("remaining_xg_adjusted", 0)),
            expected_total_goals=float(row.get("expected_total_goals", row["xg"])),
            probability=float(probabilities[i]),
        )

        db.add(prediction)
        results.append(prediction)

    db.commit()

    return sorted(results, key=lambda x: x.probability, reverse=True)
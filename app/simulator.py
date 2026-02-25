import os
import pandas as pd
import numpy as np


def run_golden_boot_simulation(
    blend_factor=0.7,
    n_simulations=100000
):
    # Project root = one level above app/
    PROJECT_ROOT = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )

    player_stats_path = os.path.join(PROJECT_ROOT, "data", "player_stats.csv")
    schedule_path = os.path.join(PROJECT_ROOT, "data", "schedule.csv")

    print("Reading:", player_stats_path)
    print("Reading:", schedule_path)

    player_stats = pd.read_csv(player_stats_path)
    schedule = pd.read_csv(schedule_path)

    # ... rest of your simulation code ...

    
    completed = schedule[schedule["is_result"] == True]

    home_played = completed.groupby("home_team").size()
    away_played = completed.groupby("away_team").size()

    games_played = home_played.add(away_played, fill_value=0).astype(int)
    games_remaining = 38 - games_played

    games_remaining_df = pd.DataFrame({
        "team": games_remaining.index,
        "games_remaining": games_remaining.values
    })

    player_stats["team"] = player_stats["team"].str.title()
    games_remaining_df["team"] = games_remaining_df["team"].str.title()

    player_stats = player_stats.merge(
        games_remaining_df,
        on="team",
        how="left"
    )

    player_stats["games_remaining"] = player_stats["games_remaining"].fillna(0)

    

    # xG per 90
    player_stats["xG_per_90"] = np.where(
        player_stats["minutes"] > 0,
        player_stats["xg"] / (player_stats["minutes"] / 90),
        0
    )

    # Avg minutes per game
    player_stats["avg_min_per_game"] = np.where(
        player_stats["matches"] > 0,
        player_stats["minutes"] / player_stats["matches"],
        0
    )

    # Remaining minutes
    player_stats["remaining_minutes"] = (
        player_stats["games_remaining"] *
        player_stats["avg_min_per_game"]
    )

    # Finishing over/under performance
    player_stats["finishing_diff_per_90"] = np.where(
        player_stats["minutes"] > 0,
        (player_stats["goals"] - player_stats["xg"]) /
        (player_stats["minutes"] / 90),
        0
    )

    # Blend finishing skill with regression
    player_stats["adjusted_xG_per_90"] = (
        (1 - blend_factor) * player_stats["xG_per_90"] +
        blend_factor * (
            player_stats["xG_per_90"] +
            player_stats["finishing_diff_per_90"]
        )
    )

    # Remaining xG expectation
    player_stats["remaining_xG_adjusted"] = (
        player_stats["adjusted_xG_per_90"] *
        (player_stats["remaining_minutes"] / 90)
    )

    
    # FILTER CONTENDERS
    
    contenders = player_stats[
        (player_stats["position"].str.contains("F|M", na=False)) &
        (player_stats["minutes"] >= 700) &
        (player_stats["goals"] >= 4)
    ].copy()

    if contenders.empty:
        return []

    
    # MONTE CARLO SIMULATION
    

    # Add minutes uncertainty (injury/rotation risk)
    minutes_noise = np.random.normal(
        loc=1.0,
        scale=0.15,
        size=(len(contenders), n_simulations)
    )

    adjusted_xg_matrix = (
        contenders["remaining_xG_adjusted"].values[:, np.newaxis] *
        minutes_noise
    )

    adjusted_xg_matrix = np.clip(adjusted_xg_matrix, 0, None)

    # Simulate remaining goals via Poisson
    sim_remaining = np.random.poisson(adjusted_xg_matrix)

    # Total goals after simulation
    sim_total = (
        contenders["goals"].values[:, np.newaxis] +
        sim_remaining
    )

    
    # WINNER PROBABILITY
    
    max_per_sim = sim_total.max(axis=0)
    is_top = (sim_total == max_per_sim).astype(float)

    contenders["prob_top_scorer"] = (
        is_top.mean(axis=1) * 100
    )

    
    # EXPECTED & CONFIDENCE INTERVALS
    
    contenders["expected_total"] = sim_total.mean(axis=1)
    contenders["p5_total"] = np.percentile(sim_total, 5, axis=1)
    contenders["p95_total"] = np.percentile(sim_total, 95, axis=1)

    
    # FINAL RANKING (BY PROBABILITY)
    
    result = contenders.sort_values(
        "prob_top_scorer",
        ascending=False
    ).head(11)[
        [
            "player",
            "team",
            "goals",
            "xg",
            "expected_total",
            "p5_total",
            "p95_total",
            "prob_top_scorer"
        ]
    ]

    return result.to_dict(orient="records")

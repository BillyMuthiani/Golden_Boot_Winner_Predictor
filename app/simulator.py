import pandas as pd
import numpy as np
import json

def run_golden_boot_simulation(
    player_stats_path="data/player_stats.csv",
    schedule_path="data/schedule.csv",
    blend_factor=0.7,
    n_simulations=100000
):
    player_stats = pd.read_csv(player_stats_path)
    schedule = pd.read_csv(schedule_path)

    # Remaining matches
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

    player_stats = player_stats.merge(games_remaining_df, on="team", how="left")
    player_stats["games_remaining"] = player_stats["games_remaining"].fillna(0)

    # Metrics
    player_stats["xG_per_90"] = np.where(
        player_stats["minutes"] > 0,
        player_stats["xg"] / (player_stats["minutes"] / 90),
        0
    )

    player_stats["avg_min_per_game"] = np.where(
        player_stats["matches"] > 0,
        player_stats["minutes"] / player_stats["matches"],
        0
    )

    player_stats["remaining_minutes"] = (
        player_stats["games_remaining"] *
        player_stats["avg_min_per_game"]
    )

    player_stats["finishing_diff_per_90"] = np.where(
        player_stats["minutes"] > 0,
        (player_stats["goals"] - player_stats["xg"]) /
        (player_stats["minutes"] / 90),
        0
    )

    player_stats["adjusted_xG_per_90"] = (
        (1 - blend_factor) * player_stats["xG_per_90"] +
        blend_factor * (player_stats["xG_per_90"] + player_stats["finishing_diff_per_90"])
    )

    player_stats["remaining_xG_adjusted"] = (
        player_stats["adjusted_xG_per_90"] *
        (player_stats["remaining_minutes"] / 90)
    )

    contenders = player_stats[
        (player_stats["position"].str.contains("F|M", na=False)) &
        (player_stats["minutes"] >= 700) &
        (player_stats["goals"] >= 4)
    ].copy()

    sim_remaining = np.random.poisson(
        contenders["remaining_xG_adjusted"].values[:, np.newaxis],
        size=(len(contenders), n_simulations)
    )

    sim_total = contenders["goals"].values[:, np.newaxis] + sim_remaining

    max_per_sim = sim_total.max(axis=0)
    is_top = (sim_total == max_per_sim).astype(float)

    contenders["prob_top_scorer"] = is_top.mean(axis=1) * 100
    contenders["expected_total"] = contenders["goals"] + contenders["remaining_xG_adjusted"]

    result = contenders.sort_values("expected_total", ascending=False).head(11)[
        ["player", "team", "goals","xg","finishing_diff_per_90","adjusted_xG_per_90","remaining_xG_adjusted",
         "expected_total", "prob_top_scorer"]
    ]

    return result.to_dict(orient="records")
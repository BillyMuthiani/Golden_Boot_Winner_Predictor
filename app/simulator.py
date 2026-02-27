# app/simulator.py

import numpy as np
from typing import List, Dict
from .player_schema import PlayerStats


SIMULATIONS = 1000


def run_monte_carlo(players: List[PlayerStats]) -> Dict[str, float]:

    win_counts = {p.player: 0 for p in players}

    for _ in range(SIMULATIONS):

        simulated_goals = {}

        for p in players:
            # Simple Poisson model using xG
            simulated = np.random.poisson(lam=p.xg)
            simulated_goals[p.player] = simulated

        winner = max(simulated_goals, key=simulated_goals.get)
        win_counts[winner] += 1

    probabilities = {
        player: win_counts[player] / SIMULATIONS
        for player in win_counts
    }

    return probabilities
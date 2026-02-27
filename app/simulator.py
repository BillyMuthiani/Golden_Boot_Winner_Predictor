# app/simulator.py

import numpy as np
from typing import List, Dict
from app.models import PlayerStats


N_SIMULATIONS = 100_000


def run_monte_carlo(players: List[PlayerStats]) -> Dict[str, float]:
    """
    Runs Monte Carlo simulation and returns
    {player_name: probability_of_winning}
    """

    goal_counts = {p.player: 0 for p in players}

    for _ in range(N_SIMULATIONS):
        simulated = {}

        for p in players:
            # Using xG as Poisson lambda
            simulated[p.player] = np.random.poisson(p.xg)

        winner = max(simulated, key=simulated.get)
        goal_counts[winner] += 1

    probabilities = {
        player: wins / N_SIMULATIONS
        for player, wins in goal_counts.items()
    }

    return probabilities

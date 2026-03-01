import logging
import sys

from app.database import SessionLocal
from data.generate_data import fetch_player_data
from app.simulator import run_monte_carlo # if you have this
from app.player_schema import PlayerStats
from app.models import Prediction

LEAGUE = "EPL"
SEASON = 2024


def main():
    logging.basicConfig(level=logging.INFO)

    try:
        logging.info("Fetching player data...")
        df = fetch_player_data(LEAGUE, SEASON)

        if df.empty:
            logging.warning("Fetched dataframe is empty. Skipping update.")
            sys.exit(0)

    except Exception as e:
        logging.error(f"Data fetch failed: {e}")
        logging.info("Skipping update and keeping old predictions.")
        sys.exit(0)

    try:
        logging.info("Generating predictions...")
        run_monte_carlo(df)

        logging.info("Update completed successfully.")

    except Exception as e:
        logging.error(f"Prediction generation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
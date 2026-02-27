from fastapi import FastAPI
from datetime import datetime, timedelta

from sqlalchemy import engine
from app.database import SessionLocal
from app.models import Prediction
from app.simulator import run_golden_boot_simulation
from data.generate_data import fetch_data

app = FastAPI()

CACHE_HOURS = 6  # predictions valid for 6 hours

@app.get("/")
def root():
    return {"message": "Golden Boot API is running 🚀"}


@app.get("/goldenboot")
def get_golden_boot(league: str, season: str):

    db = SessionLocal()

    # Check if predictions already exist
    existing = db.query(Prediction).filter(
        Prediction.league == league
    ).first()

    if existing:
        # Check how old they are
        time_diff = datetime.utcnow() - existing.computed_at

        if time_diff < timedelta(hours=CACHE_HOURS):
            print("Returning cached predictions.")
            results = db.query(Prediction).filter(
                Prediction.league == league
            ).order_by(Prediction.probability.desc()).all()

            db.close()
            return results

    # If no recent predictions → recompute
    print("Cache expired or not found. Recomputing...")

    # Fetch fresh data
    fetch_data(league, season)

    # Run simulation
    predictions = run_golden_boot_simulation(db, league)

    # Delete old predictions
    db.query(Prediction).filter(
        Prediction.league == league
    ).delete()

    # Store new predictions
    for p in predictions:
        record = Prediction(
            league=league,
            player=p["player"],
            team=p["team"],
            goals=p["goals"],
            xg=p["xg"],
            adjusted_xg_per_90=p["adjusted_xg_per_90"],
            finishing_diff_per_90=p["finishing_diff_per_90"],
            remaining_xg_adjusted=p["remaining_xg_adjusted"],
            expected_total_goals=p["expected_total"],
            probability=p["prob_top_scorer"]
        )
        db.add(record)

    db.commit()

    results = db.query(Prediction).filter(
        Prediction.league == league
    ).order_by(Prediction.probability.desc()).all()

    db.close()

    return results

from app.database import engine
from app.models import Base

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
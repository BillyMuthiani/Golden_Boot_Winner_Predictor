from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from .models import Base, GoldenBootResult
from .simulator import run_golden_boot_simulation
from data.generate_data import generate_data


app = FastAPI()

Base.metadata.create_all(bind=engine)

import soccerdata
print("Soccerdata version:", soccerdata.__version__)


# -------------------
# DB Dependency
# -------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------
# Root
# -------------------

@app.get("/")
def root():
    return {"status": "Golden Boot API running"}


# -------------------
# Run Simulation
# -------------------

@app.post("/run-simulation")
def run_simulation(
    league: str,
    season: str = "2025",
    n_simulations: int = 100000,
    db: Session = Depends(get_db)
):

    # 1️⃣ Fetch fresh data and save CSV
    generate_data(league, season)

    # 2️⃣ Run simulation
    results = run_golden_boot_simulation(
        league=league,
        season=season,
        n_simulations=n_simulations
    )

    # 3️⃣ Delete old results for this league only
    db.query(GoldenBootResult)\
      .filter(GoldenBootResult.league == league)\
      .delete()

    db.commit()

    # 4️⃣ Store new results
    for r in results:
        db.add(GoldenBootResult(
            league=league,
            player_name=r["player_name"],
            win_probability=r["prob_top_scorer"]
        ))

    db.commit()

    return {
        "status": f"{league} simulation complete",
        "top_5": results[:5]
    }


# -------------------
# Get Results
# -------------------

@app.get("/goldenboot")
def golden_boot(
    league: str,
    db: Session = Depends(get_db)
):

    results = db.query(GoldenBootResult)\
        .filter(GoldenBootResult.league == league)\
        .order_by(GoldenBootResult.win_probability.desc())\
        .all()

    return [
        {
            "player": r.player_name,
            "win_probability": r.win_probability
        }
        for r in results
    ]
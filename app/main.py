from fastapi import FastAPI
from .database import engine
from .models import Base
from .models import GoldenBootResult
from .simulator import run_golden_boot_simulation
from sqlalchemy.orm import Session
from .database import SessionLocal
from fastapi import Depends

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"status": "Golden Boot API running"}




@app.post("/run-simulation")
def run_simulation(n_simulations: int = 100000,
                   db: Session = Depends(get_db)):

    results = run_golden_boot_simulation(n_simulations=n_simulations)

    db.query(GoldenBootResult).delete()
    db.commit()

    for r in results:
        db.add(GoldenBootResult(
            player_name=r["player"],
            win_probability=r["win_probability"]
        ))

    db.commit()

    return {"status": "Simulation complete"}
    


@app.get("/goldenboot")
def golden_boot(db: Session = Depends(get_db)):

    results = db.query(GoldenBootResult)\
                .order_by(GoldenBootResult.win_probability.desc())\
                .all()

    return [
        {
            "player": r.player_name,
            "win_probability": r.win_probability
        }
        for r in results
    ]
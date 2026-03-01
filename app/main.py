# app/main.py

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import engine
from .database import get_db, engine
from .models import Base, Prediction

Base.metadata.create_all(bind=engine)

app = FastAPI()



@app.get("/migrate")
def run_migration():
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE predictions ADD COLUMN season INTEGER;"))
        conn.execute(text("UPDATE predictions SET season = 2025 WHERE season IS NULL;"))
        conn.commit()
    return {"status": "migration complete"}


@app.get("/goldenboot")
def get_golden_boot(
    league: str,
    season: int,
    db: Session = Depends(get_db)
):

    predictions = (
        db.query(Prediction)
        .filter(
            Prediction.league == league,
            Prediction.season == season
        )
        .order_by(Prediction.probability.desc())
        .all()
    )

    return predictions
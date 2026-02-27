# app/main.py

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import get_db, engine
from .models import Base, Prediction

Base.metadata.create_all(bind=engine)

app = FastAPI()


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
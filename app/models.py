# app/models.py

from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from .database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    player = Column(String, index=True)
    team = Column(String)
    probability = Column(Float)
    league = Column(String, index=True)
    season = Column(Integer, index=True)
    computed_at = Column(DateTime, default=datetime.utcnow)
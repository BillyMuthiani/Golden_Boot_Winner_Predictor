from sqlalchemy import Column, Integer, Float, String
from .database import Base

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    player = Column(String)
    team = Column(String)

    goals = Column(Integer)

    xg = Column(Float)
    adjusted_xg_per_90 = Column(Float)
    finishing_diff_per_90 = Column(Float)
    remaining_xg_adjusted = Column(Float)
    expected_total_goals = Column(Float)

    probability = Column(Float)


class GoldenBootResult(Base):
    __tablename__ = "golden_boot_results"

    id = Column(Integer, primary_key=True, index=True)
    league = Column(String, index=True)
    player_name = Column(String, index=True)
    win_probability = Column(Float)    
import sys
from app.database import SessionLocal
from app.models import Prediction
from app.simulator import run_golden_boot_simulation

# Get league from command line
league = sys.argv[1]

predictions = run_golden_boot_simulation(league)

db = SessionLocal()

# Delete only this league's predictions
db.query(Prediction).filter(
    Prediction.league == league
).delete()

for p in predictions:
    record = Prediction(
        league=league,   # ADD THIS
        player=p["player"],
        team=p["team"],
        goals=p["goals"],
        xg=p["xg"],
        adjusted_xg_per_90=p["adjusted_xG_per_90"],
        finishing_diff_per_90=p["finishing_diff_per_90"],
        remaining_xg_adjusted=p["remaining_xG_adjusted"],
        expected_total_goals=p["expected_total"],
        probability=p["prob_top_scorer"]
    )
    db.add(record)

db.commit()
db.close()

print(f"{league} predictions saved successfully.")
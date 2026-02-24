from app.database import SessionLocal
from app.models import Prediction
from app.simulator import run_golden_boot_simulation

# Run simulation
predictions = run_golden_boot_simulation()

db = SessionLocal()

# Clear old records
db.query(Prediction).delete()

# Insert new ones
for p in predictions:
    record = Prediction(
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

print("Predictions saved to PostgreSQL successfully.")
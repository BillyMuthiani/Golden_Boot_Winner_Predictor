from fastapi import FastAPI
from .database import engine
from .models import Base
from .simulator import run_golden_boot_simulation

import json

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"status": "Golden Boot API running"}


@app.post("/run-simulation")
def run_simulation():
    results = run_golden_boot_simulation()

    # Save to file
    with open("predictions.json", "w") as f:
        json.dump(results, f, indent=4)

    return {
        "message": "Simulation completed successfully",
        "top_candidate": results[0] if results else None
    }


@app.get("/goldenboot")
def golden_boot():
    try:
        with open("predictions.json") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"error": "No predictions found. Run simulation first."}
from .database import engine
from .models import Base
from fastapi import FastAPI
import json

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"status": "API running"}

@app.get("/goldenboot")
def golden_boot():
    with open("predictions.json") as f:
        return json.load(f)
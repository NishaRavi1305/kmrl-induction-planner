from fastapi import FastAPI, HTTPException
from backend.optimizer.model import run_optimizer
import pandas as pd
import os

app = FastAPI(title="KMRL Induction Planner")

DATA_DIR = "data_samples"

@app.get("/")
def root():
    return {"message": "KMRL Induction Planner API is running 🚇"}

@app.get("/ingest/{filename}")
def ingest_file(filename: str):
    try:
        path = os.path.join(DATA_DIR, filename)
        if not os.path.exists(path):
            raise HTTPException(status_code=404, detail=f"{filename} not found")

        # Load CSV safely
        df = pd.read_csv(path)

        # Fill missing values with empty strings
        df.fillna("", inplace=True)

        # Convert datetime columns safely if they exist
        for date_col in ["rolling_expiry", "signalling_expiry", "telecom_expiry", "window_end"]:
            if date_col in df.columns:
                df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

        # Return full CSV for preview; frontend slider will control rows displayed
        return {
            "rows": len(df),
            "columns": df.columns.tolist(),
            "preview": df.to_dict(orient="records")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/plan/run")
def run_plan(required_service: int, max_mileage: int = 8000):
    return run_optimizer(required_service, max_mileage=max_mileage)

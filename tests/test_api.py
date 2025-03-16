"""
Test script for Cancer Digital Twin API
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
import uvicorn

from backend.core.utils.config import Config
from backend.core.risk_models import calculate_baseline_risk
from backend.core.treatment import simulate_treatment_response, generate_treatment_recommendations
from backend.core.progression.models import ProgressionSimulator

app = FastAPI(title="Cancer Digital Twin API")

class PatientData(BaseModel):
    age: int
    tumor_size: float
    grade: int
    nodes_positive: int
    er_status: str
    pr_status: str
    her2_status: str
    molecular_subtype: str

class TreatmentPlan(BaseModel):
    treatment_type: str
    regimen: str
    duration_months: int

@app.post("/risk-assessment")
async def risk_assessment(patient: PatientData):
    try:
        risk = calculate_baseline_risk(patient.dict())
        return risk
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/treatment-simulation")
async def treatment_simulation(patient: PatientData, treatment: TreatmentPlan):
    try:
        response = simulate_treatment_response(
            patient.dict(),
            treatment.dict()
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/disease-progression")
async def disease_progression(
    patient: PatientData,
    months: Optional[int] = 60,
    simulations: Optional[int] = 100
):
    try:
        simulator = ProgressionSimulator()
        progression = simulator.simulate_progression(
            patient.dict(),
            months=months,
            n_simulations=simulations
        )
        return progression
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/treatment-recommendations")
async def treatment_recommendations(patient: PatientData):
    try:
        recommendations = generate_treatment_recommendations(patient.dict())
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000) 
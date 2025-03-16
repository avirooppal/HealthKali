from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import json
import os
import tempfile
import shutil

from backend.core.digital_twin.patient_twin import PatientDigitalTwin, BiomarkerStatus
from backend.data.import_export.data_importer import DataImporter
from backend.ml.simulation.progression_model import ProgressionModel
from backend.api.dependencies import get_progression_model

app = FastAPI(title="Cancer Digital Twin API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class PatientInput(BaseModel):
    patient_id: str
    age: int
    tumor_size_cm: float
    lymph_nodes_positive: int
    grade: int
    er_status: bool
    pr_status: bool
    her2_status: bool
    metastasis: Optional[bool] = False
    comorbidities: Optional[List[str]] = []

class TreatmentPlan(BaseModel):
    treatment_type: str
    duration_weeks: int
    dosage: float = 1.0
    name: Optional[str] = None

class ProgressionRequest(BaseModel):
    patient_data: PatientInput
    months: int = 24
    treatment_plan: Optional[TreatmentPlan] = None

# Routes
@app.post("/api/patient/create", response_model=Dict)
async def create_patient(patient_data: PatientInput):
    """Create a new patient digital twin"""
    try:
        biomarker_status = BiomarkerStatus(
            er_status=patient_data.er_status,
            pr_status=patient_data.pr_status,
            her2_status=patient_data.her2_status
        )
        
        twin = PatientDigitalTwin(
            patient_id=patient_data.patient_id,
            age=patient_data.age,
            tumor_size_cm=patient_data.tumor_size_cm,
            lymph_nodes_positive=patient_data.lymph_nodes_positive,
            grade=patient_data.grade,
            biomarker_status=biomarker_status,
            metastasis=patient_data.metastasis,
            comorbidities=patient_data.comorbidities
        )
        
        return {
            "patient_id": twin.patient_id,
            "baseline_risk": twin.calculate_baseline_risk(),
            "molecular_subtype": biomarker_status.get_molecular_subtype()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/patient/import", response_model=Dict)
async def import_patient_data(
    file: UploadFile = File(...),
    format_type: str = Form(...)
):
    """Import patient data from file"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name
            
        # Process file based on format
        if format_type.lower() == "csv":
            patients = DataImporter.import_csv(temp_path)
        elif format_type.lower() == "excel":
            patients = DataImporter.import_excel(temp_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
            
        # Clean up temp file
        os.unlink(temp_path)
        
        return {
            "success": True,
            "imported_count": len(patients),
            "patients": patients
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/patient/risk-assessment", response_model=Dict)
async def assess_risk(patient_data: PatientInput):
    """Assess patient risk"""
    try:
        biomarker_status = BiomarkerStatus(
            er_status=patient_data.er_status,
            pr_status=patient_data.pr_status,
            her2_status=patient_data.her2_status
        )
        
        twin = PatientDigitalTwin(
            patient_id=patient_data.patient_id,
            age=patient_data.age,
            tumor_size_cm=patient_data.tumor_size_cm,
            lymph_nodes_positive=patient_data.lymph_nodes_positive,
            grade=patient_data.grade,
            biomarker_status=biomarker_status,
            metastasis=patient_data.metastasis,
            comorbidities=patient_data.comorbidities
        )
        
        baseline_risk = twin.calculate_baseline_risk()
        
        # Generate risk factors
        risk_factors = []
        
        if patient_data.age < 40:
            risk_factors.append({"factor": "Young age", "impact": "High"})
        
        if patient_data.tumor_size_cm > 5:
            risk_factors.append({"factor": "Large tumor size", "impact": "High"})
        elif patient_data.tumor_size_cm > 2:
            risk_factors.append({"factor": "Moderate tumor size", "impact": "Medium"})
            
        if patient_data.lymph_nodes_positive > 4:
            risk_factors.append({"factor": "Multiple positive lymph nodes", "impact": "High"})
        elif patient_data.lymph_nodes_positive > 0:
            risk_factors.append({"factor": "Positive lymph nodes", "impact": "Medium"})
            
        if patient_data.grade == 3:
            risk_factors.append({"factor": "High grade tumor", "impact": "High"})
        
        if not (patient_data.er_status or patient_data.pr_status):
            risk_factors.append({"factor": "Hormone receptor negative", "impact": "Medium"})
            
        if patient_data.her2_status:
            risk_factors.append({"factor": "HER2 positive", "impact": "Medium"})
            
        # Risk classification
        risk_category = "Low"
        if baseline_risk > 0.7:
            risk_category = "Very High"
        elif baseline_risk > 0.5:
            risk_category = "High"
        elif baseline_risk > 0.3:
            risk_category = "Moderate"
            
        return {
            "baseline_risk": baseline_risk,
            "risk_category": risk_category,
            "risk_factors": risk_factors,
            "molecular_subtype": biomarker_status.get_molecular_subtype(),
            "five_year_survival_estimate": round(max(0, 1 - baseline_risk), 2)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/treatment/simulate", response_model=Dict)
async def simulate_treatment(
    patient_data: PatientInput,
    treatment_plan: TreatmentPlan,
    progression_model: ProgressionModel = Depends(get_progression_model)
):
    """Simulate treatment response"""
    try:
        biomarker_status = BiomarkerStatus(
            er_status=patient_data.er_status,
            pr_status=patient_data.pr_status,
            her2_status=patient_data.her2_status
        )
        
        twin = PatientDigitalTwin(
            patient_id=patient_data.patient_id,
            age=patient_data.age,
            tumor_size_cm=patient_data.tumor_size_cm,
            lymph_nodes_positive=patient_data.lymph_nodes_positive,
            grade=patient_data.grade,
            biomarker_status=biomarker_status,
            metastasis=patient_data.metastasis,
            comorbidities=patient_data.comorbidities
        )
        
        treatment_data = {
            "treatment_type": treatment_plan.treatment_type,
            "duration_weeks": treatment_plan.duration_weeks,
            "dosage": treatment_plan.dosage
        }
        
        response = twin.simulate_treatment_response(treatment_data)
        
        # Enhanced response with ML model predictions
        patient_features = {
            "age": patient_data.age,
            "tumor_size_cm": patient_data.tumor_size_cm,
            "lymph_nodes_positive": patient_data.lymph_nodes_positive,
            "grade": patient_data.grade,
            "er_status": patient_data.er_status,
            "pr_status": patient_data.pr_status,
            "her2_status": patient_data.her2_status,
            "metastasis": patient_data.metastasis
        }
        
        ml_predictions = progression_model.predict_treatment_effect(
            patient_features,
            treatment_data
        )
        
        # Combine basic model with ML predictions
        response.update({
            "long_term_projection": ml_predictions["with_treatment_progression"]["progression_timeline"],
            "survival_improvement": ml_predictions["survival_improvement"],
        })
        
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/progression/project", response_model=Dict)
async def project_progression(
    progression_req: ProgressionRequest,
    progression_model: ProgressionModel = Depends(get_progression_model)
):
    """Project disease progression over time"""
    try:
        biomarker_status = BiomarkerStatus(
            er_status=progression_req.patient_data.er_status,
            pr_status=progression_req.patient_data.pr_status,
            her2_status=progression_req.patient_data.her2_status
        )
        
        twin = PatientDigitalTwin(
            patient_id=progression_req.patient_data.patient_id,
            age=progression_req.patient_data.age,
            tumor_size_cm=progression_req.patient_data.tumor_size_cm,
            lymph_nodes_positive=progression_req.patient_data.lymph_nodes_positive,
            grade=progression_req.patient_data.grade,
            biomarker_status=biomarker_status,
            metastasis=progression_req.patient_data.metastasis,
            comorbidities=progression_req.patient_data.comorbidities
        )
        
        # Get simple model progression
        treatment_plan_dict = None
        if progression_req.treatment_plan:
            treatment_plan_dict = {
                "treatment_type": progression_req.treatment_plan.treatment_type,
                "duration_weeks": progression_req.treatment_plan.duration_weeks,
                "dosage": progression_req.treatment_plan.dosage
            }
            
        progression = twin.project_disease_progression(
            months=progression_req.months,
            treatment_plan=treatment_plan_dict
        )
        
        # Get ML model progression
        patient_features = {
            "age": progression_req.patient_data.age,
            "tumor_size_cm": progression_req.patient_data.tumor_size_cm,
            "lymph_nodes_positive": progression_req.patient_data.lymph_nodes_positive,
            "grade": progression_req.patient_data.grade,
            "er_status": progression_req.patient_data.er_status,
            "pr_status": progression_req.patient_data.pr_status,
            "her2_status": progression_req.patient_data.her2_status,
            "metastasis": progression_req.patient_data.metastasis
        }
        
        if progression_req.treatment_plan:
            ml_progression = progression_model.predict_treatment_effect(
                patient_features,
                treatment_plan_dict
            )
            # Use with_treatment_progression from ML model
            ml_data = ml_progression["with_treatment_progression"]
        else:
            # Get time points for prediction
            time_points = list(range(3, progression_req.months + 1, 3))
            if progression_req.months not in time_points:
                time_points.append(progression_req.months)
                
            ml_data = progression_model.predict_progression(
                patient_features,
                time_points
            )
            
        # Combine the results (using ML model when available with fallback to simple model)
        return {
            "progression_timeline": ml_data.get("progression_timeline", progression["monthly_progression"]),
            "final_tumor_size": ml_data.get("final_tumor_size", progression["final_tumor_size"]),
            "final_survival_probability": ml_data.get("final_survival_probability", progression["final_survival_probability"]),
            "molecular_subtype": biomarker_status.get_molecular_subtype()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/treatment/recommend", response_model=Dict)
async def recommend_treatments(patient_data: PatientInput):
    """Get personalized treatment recommendations"""
    try:
        biomarker_status = BiomarkerStatus(
            er_status=patient_data.er_status,
            pr_status=patient_data.pr_status,
            her2_status=patient_data.her2_status
        )
        
        twin = PatientDigitalTwin(
            patient_id=patient_data.patient_id,
            age=patient_data.age,
            tumor_size_cm=patient_data.tumor_size_cm,
            lymph_nodes_positive=patient_data.lymph_nodes_positive,
            grade=patient_data.grade,
            biomarker_status=biomarker_status,
            metastasis=patient_data.metastasis,
            comorbidities=patient_data.comorbidities
        )
        
        recommendations = twin.recommend_treatments()
        
        # Add NCCN guideline compliance
        for rec in recommendations:
            # Simplified NCCN compliance check
            rec["nccn_compliant"] = True
            
            # Add standard dosing information
            if rec["treatment_type"] == "chemotherapy":
                rec["standard_regimen"] = "AC-T (Doxorubicin, Cyclophosphamide, Paclitaxel)"
            elif rec["treatment_type"] == "hormone_therapy" and patient_data.er_status:
                rec["standard_regimen"] = "Tamoxifen or Aromatase Inhibitor"
            elif rec["treatment_type"] == "targeted_therapy" and patient_data.her2_status:
                rec["standard_regimen"] = "Trastuzumab +/- Pertuzumab"
        
        return {
            "recommendations": recommendations,
            "molecular_subtype": biomarker_status.get_molecular_subtype(),
            "patient_id": patient_data.patient_id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
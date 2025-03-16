from fastapi import FastAPI, Request, Form, HTTPException, Depends, Body
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Dict, List, Optional, Any
import json
import os
import logging
import random
from pydantic import BaseModel
from datetime import datetime, timedelta
import math
from fastapi.middleware.cors import CORSMiddleware

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Cancer Digital Twin Platform")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Mount static files directory
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# Initialize templates
templates = Jinja2Templates(directory="frontend")

# Define data models
class PatientBase(BaseModel):
    patientID: str
    age: int
    tumor_size: float
    grade: int
    nodes_positive: int
    er_status: str
    her2_status: str
    menopausal_status: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class Patient(PatientBase):
    riskScore: float
    dateAdded: str
    
    class Config:
        orm_mode = True

class TreatmentPlan(BaseModel):
    patientID: str
    treatments: List[str]
    expectedOutcomes: Dict[str, float]
    sideEffects: List[str]

class SimulationRequest(BaseModel):
    patientID: str
    duration: int = 60  # months
    include_treatment: bool = True

class SimulationResult(BaseModel):
    timepoints: List[int]
    tumor_sizes: List[float]
    survival_probabilities: List[float]
    dfs_probabilities: List[float]
    metastasis_probabilities: List[float]

# In-memory database for demo purposes
patients_db = {}

# Helper functions
def calculate_risk_score(patient_data: dict) -> float:
    # Basic risk calculation
    tumor_size = float(patient_data.get('tumor_size', 0))
    grade = int(patient_data.get('grade', 1))
    nodes_positive = int(patient_data.get('nodes_positive', 0))
    er_status = patient_data.get('er_status', 'positive')
    her2_status = patient_data.get('her2_status', 'negative')
    
    risk_score = (tumor_size * 0.004 + grade * 0.05 + nodes_positive * 0.03)
    
    # Adjust for receptor status
    if er_status == 'negative':
        risk_score += 0.1
    if her2_status == 'positive':
        risk_score += 0.05
    
    # Cap between 0.1 and 0.9
    risk_score = max(0.1, min(0.9, risk_score))
    
    return risk_score

def generate_treatment_plan(patient_data: dict) -> dict:
    # Generate mock treatment plan
    treatments = []
    
    # Surgery recommendations
    tumor_size = float(patient_data.get('tumor_size', 0))
    if tumor_size <= 20:
        treatments.append("Breast Conserving Surgery (Lumpectomy)")
    else:
        treatments.append("Mastectomy with consideration for reconstruction")
    
    # Radiation therapy
    if tumor_size <= 20:
        treatments.append("Whole breast radiation following lumpectomy")
    
    # Chemotherapy
    grade = int(patient_data.get('grade', 1))
    nodes_positive = int(patient_data.get('nodes_positive', 0))
    if grade >= 3 or nodes_positive > 0 or tumor_size > 20 or patient_data.get('er_status') == 'negative':
        treatments.append("Adjuvant chemotherapy")
    
    # Hormonal therapy
    if patient_data.get('er_status') == 'positive':
        if patient_data.get('menopausal_status') == 'pre':
            treatments.append("Tamoxifen for 5-10 years")
        else:
            treatments.append("Aromatase inhibitor for 5-10 years")
    
    # Targeted therapy
    if patient_data.get('her2_status') == 'positive':
        treatments.append("Trastuzumab (Herceptin) for 1 year")
    
    # Expected outcomes
    risk_score = calculate_risk_score(patient_data)
    expected_outcomes = {
        "5_year_survival": (1 - risk_score) * 100,
        "10_year_survival": (1 - risk_score * 1.2) * 100,
        "recurrence_risk": risk_score * 100,
        "quality_of_life": 80 - (risk_score * 20)
    }
    
    # Side effects
    side_effects = []
    if "Lumpectomy" in treatments[0]:
        side_effects.append("Post-surgical pain and swelling (1-2 weeks)")
    else:
        side_effects.append("Post-surgical pain and recovery (2-4 weeks)")
        
    if "radiation" in treatments[1]:
        side_effects.append("Skin irritation and fatigue during radiation treatment")
    
    if "chemotherapy" in treatments:
        side_effects.append("Hair loss, nausea, fatigue during chemotherapy")
        side_effects.append("Potential for reduced blood counts and immune suppression")
    
    if "Tamoxifen" in ' '.join(treatments):
        side_effects.append("Hot flashes and potential for menopausal symptoms")
    
    if "Aromatase inhibitor" in ' '.join(treatments):
        side_effects.append("Joint pain and potential bone density loss")
    
    if "Trastuzumab" in ' '.join(treatments):
        side_effects.append("Potential cardiac monitoring required")
    
    return {
        "patientID": patient_data.get('patientID'),
        "treatments": treatments,
        "expectedOutcomes": expected_outcomes,
        "sideEffects": side_effects
    }

def simulate_disease_course(patient_data: dict, duration: int = 60, include_treatment: bool = True) -> dict:
    # Initialize simulation parameters
    time_points = list(range(0, duration + 1, 3))  # Every 3 months
    risk_score = calculate_risk_score(patient_data)
    tumor_size = float(patient_data.get('tumor_size', 0))
    grade = int(patient_data.get('grade', 1))
    
    # Baseline growth rate (mm per month)
    if grade == 1:
        growth_rate = 0.1 + random.uniform(0, 0.1)
    elif grade == 2:
        growth_rate = 0.2 + random.uniform(0, 0.15)
    else:
        growth_rate = 0.3 + random.uniform(0, 0.2)
    
    # Adjust for hormone receptor status
    if patient_data.get('er_status') == 'negative':
        growth_rate *= 1.2
    
    if patient_data.get('her2_status') == 'positive':
        growth_rate *= 1.3
    
    # Initialize arrays
    tumor_sizes = []
    survival_probs = []
    dfs_probs = []
    metastasis_probs = []
    
    # Treatment effect (if included)
    treatment_effect = 0
    if include_treatment:
        treatment_effect = 0.8  # 80% reduction in growth
    
    # Run simulation
    for i, time in enumerate(time_points):
        # Calculate tumor size using Gompertz growth model
        if i == 0:
            current_size = tumor_size
        else:
            max_size = 100.0  # Maximum tumor size in mm
            growth_k = 0.1 + (0.05 * grade)
            
            # Apply treatment effect after 3 months (surgery/chemo start)
            if include_treatment and time >= 3:
                growth_k *= (1 - treatment_effect)
            
            # Gompertz growth formula
            current_size = max_size * math.exp(
                -math.exp(1 - (growth_k * time/3 * (1 - math.log(tumor_size) / math.log(max_size))))
            )
        
        tumor_sizes.append(round(current_size, 1))
        
        # Calculate probabilities
        base_survival = 1.0 - risk_score
        if include_treatment:
            survival_prob = base_survival + (1 - base_survival) * 0.7 * (1 - time/(2*duration))
        else:
            survival_prob = base_survival * (1 - time/(duration))
        
        survival_probs.append(round(max(0, min(1, survival_prob)) * 100, 1))
        
        # Disease-free survival (DFS)
        if include_treatment and time < 6:  # First 6 months after treatment
            dfs_prob = 0.95
        else:
            dfs_base = base_survival * 1.1
            dfs_prob = dfs_base * (1 - 0.8 * time/duration)
            
        dfs_probs.append(round(max(0, min(1, dfs_prob)) * 100, 1))
        
        # Metastasis probability
        if include_treatment:
            meta_prob = risk_score * (time/(2*duration))
        else:
            meta_prob = risk_score * (time/duration) * 1.5
            
        metastasis_probs.append(round(min(1, meta_prob) * 100, 1))
    
    return {
        "timepoints": time_points,
        "tumor_sizes": tumor_sizes,
        "survival_probabilities": survival_probs,
        "dfs_probabilities": dfs_probs,
        "metastasis_probabilities": metastasis_probs
    }


# Routes
@app.get("/", response_class=HTMLResponse)
async def get_root(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

# API Routes
@app.post("/api/patients/", response_model=Patient)
async def create_patient(patient: PatientCreate):
    # Generate risk score
    risk_score = calculate_risk_score(patient.dict())
    
    # Create patient object with additional fields
    patient_dict = patient.dict()
    patient_dict["riskScore"] = risk_score
    patient_dict["dateAdded"] = datetime.now().isoformat()
    
    # Store in mock database
    patients_db[patient.patientID] = patient_dict
    
    return patient_dict

@app.get("/api/patients/{patient_id}", response_model=Patient)
async def get_patient(patient_id: str):
    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patients_db[patient_id]

@app.get("/api/patients/", response_model=List[Patient])
async def get_all_patients():
    return list(patients_db.values())

@app.get("/api/risk/baseline", response_class=JSONResponse)
async def get_baseline_risk():
    # Return baseline population risk metrics
    return {
        "survival": {
            "5year": 89.3,
            "10year": 82.8,
            "15year": 77.0
        },
        "recurrence": {
            "5year": 15.2,
            "10year": 24.6
        },
        "ageGroups": {
            "under40": {"survival": 85.9},
            "40to49": {"survival": 87.3},
            "50to59": {"survival": 89.9},
            "60to69": {"survival": 91.2},
            "over70": {"survival": 82.1}
        },
        "subtypes": {
            "luminalA": {"survival": 94.1, "recurrence": 12.3},
            "luminalB": {"survival": 90.8, "recurrence": 17.9},
            "her2_positive": {"survival": 88.5, "recurrence": 21.7},
            "triple_negative": {"survival": 77.3, "recurrence": 26.0}
        },
        "lastUpdated": "2023-06-15"
    }

@app.get("/api/treatment/recommendations", response_class=JSONResponse)
async def get_treatment_recommendations():
    # Return mock treatment guidelines
    return {
        "general": [
            {
                "stage": "Stage I",
                "description": "Small tumor, no lymph node involvement",
                "options": [
                    "Lumpectomy followed by radiation",
                    "Sentinel lymph node biopsy",
                    "Consider genomic testing for chemotherapy decision"
                ]
            },
            {
                "stage": "Stage II",
                "description": "Tumor 2-5cm or positive lymph nodes",
                "options": [
                    "Lumpectomy or mastectomy",
                    "Axillary lymph node dissection",
                    "Adjuvant chemotherapy for high-risk features",
                    "Hormonal therapy for hormone-positive disease"
                ]
            },
            {
                "stage": "Stage III",
                "description": "Locally advanced disease",
                "options": [
                    "Neoadjuvant chemotherapy often recommended",
                    "Mastectomy with axillary node dissection",
                    "Post-mastectomy radiation",
                    "Targeted therapy for HER2+ disease"
                ]
            }
        ],
        "subtypes": {
            "er_positive": {
                "options": [
                    "Tamoxifen for premenopausal women",
                    "Aromatase inhibitors for postmenopausal women",
                    "Consider ovarian suppression for high-risk premenopausal patients"
                ],
                "duration": "5-10 years of hormonal therapy"
            },
            "her2_positive": {
                "options": [
                    "Trastuzumab (Herceptin) for 1 year",
                    "Consider pertuzumab for high-risk patients",
                    "TDM1 for residual disease after neoadjuvant therapy"
                ]
            },
            "triple_negative": {
                "options": [
                    "Dose-dense chemotherapy regimens",
                    "Consider platinum agents",
                    "Clinical trials for novel approaches"
                ]
            }
        },
        "lastUpdated": "2023-11-01"
    }

@app.post("/api/patients/{patient_id}/treatment-plan", response_model=TreatmentPlan)
async def generate_patient_treatment_plan(patient_id: str):
    if patient_id not in patients_db:
        # Generate mock data for demo purposes
        mock_patient = {
            "patientID": patient_id,
            "age": 55,
            "tumor_size": 22,
            "grade": 2,
            "nodes_positive": 1,
            "er_status": "positive",
            "her2_status": "negative",
            "menopausal_status": "post"
        }
        return generate_treatment_plan(mock_patient)
    
    return generate_treatment_plan(patients_db[patient_id])

@app.post("/api/patients/{patient_id}/simulate", response_model=SimulationResult)
async def simulate_patient_disease(
    patient_id: str, 
    simulation_params: SimulationRequest = Body(...)
):
    if patient_id not in patients_db:
        # Generate mock data for demo purposes
        mock_patient = {
            "patientID": patient_id,
            "age": 55,
            "tumor_size": 22,
            "grade": 2,
            "nodes_positive": 1,
            "er_status": "positive",
            "her2_status": "negative",
            "menopausal_status": "post"
        }
        return simulate_disease_course(
            mock_patient, 
            duration=simulation_params.duration,
            include_treatment=simulation_params.include_treatment
        )
    
    return simulate_disease_course(
        patients_db[patient_id],
        duration=simulation_params.duration,
        include_treatment=simulation_params.include_treatment
    )

@app.get("/risk/baseline")
async def get_risk_baseline():
    """Get baseline risk data for breast cancer"""
    return {
        "population_risk": {
            "lifetime": 12.5,
            "5year": 2.3,
            "10year": 3.8
        },
        "survival_rates": {
            "stage1": 98.8,
            "stage2": 85.5,
            "stage3": 62.3,
            "stage4": 28.1
        },
        "age_distribution": {
            "under40": 5.2,
            "40to49": 15.8,
            "50to59": 23.7,
            "60to69": 25.1,
            "70plus": 30.2
        }
    }

@app.get("/treatment/recommendations")
async def get_treatment_recommendations():
    """Get treatment recommendations based on cancer characteristics"""
    return {
        "surgery": [
            {"name": "Lumpectomy", "description": "Removal of tumor and small margin of surrounding tissue"},
            {"name": "Mastectomy", "description": "Removal of entire breast"},
            {"name": "Sentinel Node Biopsy", "description": "Removal of sentinel lymph nodes"}
        ],
        "radiation": [
            {"name": "Whole Breast", "description": "Standard radiation after lumpectomy"},
            {"name": "Partial Breast", "description": "More targeted radiation for eligible patients"},
            {"name": "Post-Mastectomy", "description": "Radiation following mastectomy for high-risk cases"}
        ],
        "systemic": [
            {"name": "Chemotherapy", "description": "Various regimens depending on cancer characteristics"},
            {"name": "Hormonal Therapy", "description": "For hormone receptor-positive cancers"},
            {"name": "Targeted Therapy", "description": "For HER2-positive or other targetable mutations"},
            {"name": "Immunotherapy", "description": "Newer approaches for specific cancer types"}
        ]
    }

@app.get("/progression/project")
async def get_progression_projection():
    """Get disease progression projection data"""
    return {
        "natural_history": {
            "months": [0, 3, 6, 9, 12, 15, 18, 21, 24],
            "tumor_size": [15, 17.2, 19.8, 22.8, 26.2, 30.1, 34.6, 39.7, 45.6],
            "survival_probability": [99, 97, 95, 92, 88, 84, 79, 74, 68]
        },
        "with_treatment": {
            "months": [0, 3, 6, 9, 12, 15, 18, 21, 24],
            "tumor_size": [15, 12, 8, 4, 0, 0, 0, 0, 0],
            "survival_probability": [99, 98, 97, 96, 95, 94, 93, 92, 91]
        },
        "metastasis_probability": {
            "months": [0, 3, 6, 9, 12, 15, 18, 21, 24],
            "untreated": [5, 12, 22, 35, 48, 60, 70, 78, 85],
            "treated": [5, 8, 10, 12, 14, 15, 16, 17, 18]
        }
    }

# Run app
if __name__ == "__main__":
    import uvicorn
    import math  # Required for simulation calculations
    
    # Create the frontend directory if it doesn't exist
    os.makedirs("frontend", exist_ok=True)
    
    # Print current directory structure for debugging
    print("Current directory structure:")
    for root, dirs, files in os.walk("."):
        level = root.replace(".", "").count(os.sep)
        indent = " " * 4 * level
        print(f"{indent}{os.path.basename(root)}/")
        for file in files:
            print(f"{indent}    {file}")
    
    # Run server
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
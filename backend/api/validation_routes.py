from fastapi import APIRouter, HTTPException
from pathlib import Path
import os
import json

router = APIRouter()

@router.get("/validation/results")
async def get_validation_results():
    """Return the validation results with associated metadata."""
    validation_dir = Path("validation_results")
    
    # Check if validation directory exists
    if not validation_dir.exists() or not validation_dir.is_dir():
        raise HTTPException(status_code=404, detail="Validation results directory not found")
    
    # Define metadata for validation images
    validation_metadata = {
        "survival_curve_validation.png": {
            "title": "Survival Curve Validation",
            "description": "Comparison of predicted vs. actual survival curves on test data",
            "metrics": {
                "concordance_index": 0.83,
                "calibration_slope": 0.94,
                "brier_score": 0.107
            }
        },
        "calibration_plot.png": {
            "title": "Model Calibration",
            "description": "Assessment of prediction probability calibration",
            "metrics": {
                "expected_calibration_error": 0.034,
                "maximum_calibration_error": 0.089,
                "calibration_slope": 0.91
            }
        },
        "roc_curve.png": {
            "title": "ROC Curve Analysis",
            "description": "Receiver operating characteristic curve for model performance",
            "metrics": {
                "auc": 0.87,
                "sensitivity": 0.84,
                "specificity": 0.82
            }
        },
        "feature_importance.png": {
            "title": "Feature Importance",
            "description": "Relative importance of predictive features",
            "metrics": {
                "top_feature": "Tumor Size",
                "top_feature_importance": 0.28,
                "stability_score": 0.92
            }
        },
        "confusion_matrix.png": {
            "title": "Confusion Matrix",
            "description": "Classification performance visualization",
            "metrics": {
                "accuracy": 0.825,
                "precision": 0.842,
                "recall": 0.80,
                "f1_score": 0.821
            }
        },
        "subtype_clustering.png": {
            "title": "Molecular Subtype Clustering",
            "description": "Clustering of patients by molecular signatures",
            "metrics": {
                "silhouette_score": 0.78,
                "davies_bouldin_score": 0.42,
                "calinski_harabasz_score": 1024.6
            }
        }
    }
    
    # Get available images and their paths
    results = {}
    for image_file in validation_dir.glob("*.png"):
        if image_file.name in validation_metadata:
            results[image_file.name] = {
                "path": f"/validation_results/{image_file.name}",
                "info": validation_metadata[image_file.name]
            }
    
    return results

@router.get("/patient/detailed-analysis/{patient_id}")
async def get_detailed_patient_analysis(patient_id: str):
    """Get detailed analysis for a specific patient."""
    # In a real app, this would fetch from a database
    # For demo purposes, return mock data
    
    return {
        "id": patient_id,
        "summary": {
            "risk_score": 0.42,
            "risk_category": "Intermediate",
            "analysis_date": "2023-06-15T10:30:00Z"
        },
        "survival": {
            "5_year": 82.3,
            "10_year": 76.1,
            "disease_free_5_year": 68.5,
            "confidence_interval": [78.2, 86.4]
        },
        "molecular_profile": {
            "subtypes": {
                "luminal_a": 0.72,
                "luminal_b": 0.18,
                "her2_enriched": 0.05,
                "basal_like": 0.03,
                "normal_like": 0.02
            },
            "key_mutations": [
                {"gene": "PIK3CA", "probability": 0.35, "impact": "High"},
                {"gene": "TP53", "probability": 0.12, "impact": "High"},
                {"gene": "ESR1", "probability": 0.08, "impact": "Medium"}
            ]
        },
        "treatment_impact": {
            "surgery": {"relative_risk_reduction": 0.65},
            "chemotherapy": {"relative_risk_reduction": 0.32},
            "radiation": {"relative_risk_reduction": 0.18},
            "endocrine": {"relative_risk_reduction": 0.40}
        },
        "quality_of_life": {
            "year_1": {"score": 65, "category": "Moderate"},
            "year_3": {"score": 78, "category": "Good"},
            "year_5": {"score": 82, "category": "Good"}
        }
    } 
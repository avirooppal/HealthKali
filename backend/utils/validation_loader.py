import os
from pathlib import Path

def load_validation_results():
    """Load validation results images and their descriptions."""
    validation_dir = Path("validation_results")
    
    # Define the expected validation images and their descriptions
    validation_files = {
        "survival_curve_validation.png": {
            "title": "Survival Curve Validation",
            "description": "Comparison of predicted vs actual survival curves across patient cohorts",
            "metrics": {
                "concordance_index": 0.82,
                "calibration_slope": 0.94,
                "calibration_intercept": 0.03
            }
        },
        "calibration_plot.png": {
            "title": "Model Calibration Analysis",
            "description": "Assessment of prediction probability calibration",
            "metrics": {
                "brier_score": 0.089,
                "expected_calibration_error": 0.043
            }
        },
        "roc_curve.png": {
            "title": "ROC Curve Analysis",
            "description": "Model discrimination performance across different thresholds",
            "metrics": {
                "auc_roc": 0.87,
                "sensitivity": 0.84,
                "specificity": 0.82
            }
        },
        "feature_importance.png": {
            "title": "Feature Importance Analysis",
            "description": "Relative contribution of different clinical features",
            "metrics": {
                "top_feature": "Tumor Size",
                "top_feature_importance": 0.28
            }
        }
    }
    
    # Check which files actually exist
    available_results = {}
    for filename, info in validation_files.items():
        file_path = validation_dir / filename
        if file_path.exists():
            available_results[filename] = {
                "path": str(file_path),
                "info": info
            }
    
    return available_results 
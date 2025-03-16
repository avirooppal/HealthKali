"""
Advanced risk assessment models using statistical methods and machine learning.
These models provide more sophisticated risk estimates and survival predictions.
"""

from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import math
from datetime import datetime, timedelta

def predict_survival_probability(
    patient_features: Dict,
    time_points: List[int],
    model_type: str = "cox"
) -> Dict[str, List[float]]:
    """
    Predict survival probabilities at specified time points
    
    Args:
        patient_features: Dictionary of patient characteristics
        time_points: List of time points (in months) for prediction
        model_type: Type of model to use ('cox', 'rsf', or 'ml')
        
    Returns:
        Dictionary with survival probabilities and confidence intervals
    """
    # Extract key features
    age = patient_features.get('age', 50)
    tumor_size = patient_features.get('tumor_size_cm', 2.0)
    nodes_positive = patient_features.get('lymph_nodes_positive', 0)
    grade = patient_features.get('grade', 2)
    er_status = patient_features.get('er_status', True)
    pr_status = patient_features.get('pr_status', True)
    her2_status = patient_features.get('her2_status', False)
    metastasis = patient_features.get('metastasis', False)
    
    # Base hazard coefficients (simplified Cox model)
    # These would be replaced with actual trained coefficients
    coefficients = {
        'age': 0.01 if age > 50 else -0.01,
        'tumor_size': 0.15,
        'nodes_positive': 0.2,
        'grade': 0.3,
        'er_status': -0.4 if er_status else 0,
        'pr_status': -0.3 if pr_status else 0,
        'her2_status': 0.2 if her2_status else 0,
        'metastasis': 1.0 if metastasis else 0
    }
    
    # Calculate linear predictor
    lp = (coefficients['age'] * (age - 60) / 10 +  # Centered age
          coefficients['tumor_size'] * tumor_size +
          coefficients['nodes_positive'] * min(10, nodes_positive) +
          coefficients['grade'] * (grade - 2) +
          coefficients['er_status'] +
          coefficients['pr_status'] +
          coefficients['her2_status'] +
          coefficients['metastasis'])
    
    # Baseline hazard function (simplified)
    def baseline_hazard(t):
        # This would be replaced with actual baseline hazard function
        return 0.02 * t / 12  # 2% annual hazard
    
    # Calculate survival probabilities
    survival_probs = []
    lower_ci = []
    upper_ci = []
    
    for t in time_points:
        # Cox model: S(t) = S0(t)^exp(lp)
        h0 = baseline_hazard(t)
        surv = math.exp(-h0 * math.exp(lp))
        surv = max(0.01, min(0.99, surv))  # Constrain between 1-99%
        
        # Simplified confidence interval (would be more sophisticated in real model)
        ci_width = 0.05 + 0.02 * t / 12  # Wider CI for longer projections
        
        survival_probs.append(surv)
        lower_ci.append(max(0.01, surv - ci_width))
        upper_ci.append(min(0.99, surv + ci_width))
    
    return {
        'time_points': time_points,
        'survival_probability': survival_probs,
        'lower_ci': lower_ci,
        'upper_ci': upper_ci
    }

def calculate_recurrence_score(
    patient_features: Dict,
    model_type: str = "simplified_oncotype"
) -> Dict[str, Union[int, str, float]]:
    """
    Calculate recurrence score similar to commercial genomic tests
    
    Args:
        patient_features: Dictionary of patient characteristics
        model_type: Type of recurrence score model
        
    Returns:
        Dictionary with score and risk category
    """
    # Extract features
    age = patient_features.get('age', 50)
    tumor_size = patient_features.get('tumor_size_cm', 2.0)
    grade = patient_features.get('grade', 2)
    er_status = patient_features.get('er_status', True)
    pr_status = patient_features.get('pr_status', True)
    her2_status = patient_features.get('her2_status', False)
    ki67 = patient_features.get('ki67_high', None)
    
    # Only meaningful for ER+ tumors
    if not er_status and model_type == "simplified_oncotype":
        return {
            'score': None,
            'category': "Not applicable (ER-negative)",
            'recurrence_risk': None
        }
    
    # Oncotype DX-like simplified model
    if model_type == "simplified_oncotype":
        # Base score
        score = 15  # Average score
        
        # Adjust for grade
        if grade == 1:
            score -= 10
        elif grade == 3:
            score += 15
            
        # Adjust for ER/PR status
        if er_status and pr_status:
            score -= 10
        elif er_status and not pr_status:
            score -= 5
            
        # Adjust for HER2
        if her2_status:
            score += 10
            
        # Adjust for proliferation (Ki67)
        if ki67 is True:
            score += 10
        elif ki67 is False:
            score -= 5
            
        # Constrain to 0-100 range
        score = max(0, min(100, score))
        
        # Determine category
        if score < 18:
            category = "Low"
            recurrence_risk = 0.07  # ~7% at 10 years
        elif score <= 30:
            category = "Intermediate"
            recurrence_risk = 0.14  # ~14% at 10 years
        else:
            category = "High"
            recurrence_risk = 0.30  # ~30% at 10 years
            
        return {
            'score': score,
            'category': category,
            'recurrence_risk': recurrence_risk
        }
        
    # MammaPrint-like simplified model
    elif model_type == "simplified_mammaprint":
        # Calculate a score from 0 to 1
        # Lower values indicate higher risk (opposite of Oncotype)
        
        base_score = 0.5  # Middle range
        
        # Adjust for age
        if age < 40:
            base_score -= 0.1
        elif age > 70:
            base_score += 0.1
            
        # Adjust for grade
        if grade == 1:
            base_score += 0.15
        elif grade == 3:
            base_score -= 0.15
            
        # Adjust for hormone status
        if er_status and pr_status:
            base_score += 0.1
        elif not er_status and not pr_status:
            base_score -= 0.2
            
        # Adjust for HER2
        if her2_status:
            base_score -= 0.05
            
        # Constrain to 0-1 range
        mp_score = max(0, min(1, base_score))
        
        # Determine category (MammaPrint is binary)
        if mp_score < 0.5:
            category = "High Risk"
            recurrence_risk = 0.29  # ~29% at 10 years
        else:
            category = "Low Risk"
            recurrence_risk = 0.12  # ~12% at 10 years
            
        return {
            'score': mp_score,
            'category': category,
            'recurrence_risk': recurrence_risk
        }
    
    else:
        raise ValueError(f"Unknown recurrence score model: {model_type}")

def calculate_competing_risks(
    patient_features: Dict,
    time_years: int = 10
) -> Dict[str, float]:
    """
    Calculate competing risks of cancer mortality vs. other causes
    
    Args:
        patient_features: Dictionary of patient characteristics
        time_years: Time horizon in years
        
    Returns:
        Dictionary with risks of breast cancer death, other death, and survival
    """
    # Extract patient info
    age = patient_features.get('age', 50)
    tumor_size = patient_features.get('tumor_size_cm', 2.0)
    nodes_positive = patient_features.get('lymph_nodes_positive', 0)
    grade = patient_features.get('grade', 2)
    er_status = patient_features.get('er_status', True)
    pr_status = patient_features.get('pr_status', True)
    her2_status = patient_features.get('her2_status', False)
    metastasis = patient_features.get('metastasis', False)
    comorbidities = patient_features.get('comorbidities', [])
    
    # Calculate breast cancer-specific mortality risk
    # Simplified model
    bc_mortality_risk = 0.05  # Base 5% at 10 years
    
    # Adjust for tumor factors
    bc_mortality_risk += min(0.3, tumor_size * 0.03)  # Size adjustment
    bc_mortality_risk += min(0.3, nodes_positive * 0.05)  # Node adjustment
    
    if grade == 3:
        bc_mortality_risk += 0.1
    
    # Biomarker adjustments
    if not (er_status or pr_status):
        bc_mortality_risk += 0.1
        
    if her2_status and not patient_features.get('received_anti_her2', False):
        bc_mortality_risk += 0.05
        
    if metastasis:
        bc_mortality_risk += 0.4
    
    # Scale for time period - simplified approach
    bc_mortality_risk = bc_mortality_risk * (time_years / 10)
    
    # Non-breast cancer mortality (age-dependent)
    # Simplified actuarial approach
    other_mortality_risk = 0.0
    
    # Age-specific annual mortality rates (simplified)
    if age < 50:
        annual_rate = 0.001  # 0.1% per year
    elif age < 60:
        annual_rate = 0.003  # 0.3% per year
    elif age < 70:
        annual_rate = 0.01  # 1% per year
    elif age < 80:
        annual_rate = 0.03  # 3% per year
    else:
        annual_rate = 0.08  # 8% per year
    
    # Adjust for comorbidities
    comorbidity_factor = 1.0
    if len(comorbidities) > 0:
        comorbidity_factor += len(comorbidities) * 0.2  # Each comorbidity increases risk
    
    # Calculate cumulative risk over time period
    # Simplified: doesn't account for competing risks between causes properly
    other_mortality_risk = 1.0 - math.pow(1.0 - annual_rate * comorbidity_factor, time_years)
    
    # Combine risks - this is a simplification, proper approach would use
    # competing risks statistical methods
    total_mortality_risk = min(0.99, bc_mortality_risk + other_mortality_risk - (bc_mortality_risk * other_mortality_risk))
    survival_probability = 1.0 - total_mortality_risk
    
    return {
        'breast_cancer_mortality': round(bc_mortality_risk, 3),
        'other_cause_mortality': round(other_mortality_risk, 3),
        'total_mortality': round(total_mortality_risk, 3),
        'survival_probability': round(survival_probability, 3),
        'time_years': time_years
    }

def risk_stratification(
    patient_features: Dict
) -> Dict[str, str]:
    """
    Stratify patient into risk groups based on clinical and genomic features
    
    Args:
        patient_features: Dictionary of patient characteristics
        
    Returns:
        Dictionary with risk classifications
    """
    # Extract key features
    age = patient_features.get('age', 50)
    tumor_size = patient_features.get('tumor_size_cm', 2.0)
    nodes_positive = patient_features.get('lymph_nodes_positive', 0)
    grade = patient_features.get('grade', 2)
    er_status = patient_features.get('er_status', True)
    pr_status = patient_features.get('pr_status', True)
    her2_status = patient_features.get('her2_status', False)
    metastasis = patient_features.get('metastasis', False)
    
    # Clinical risk (based on AdjuvantOnline-like criteria)
    clinical_risk = "Low"
    
    # High clinical risk criteria
    if any([
        tumor_size > 2.0,
        nodes_positive > 0,
        grade == 3,
        age < 35,
        not (er_status or pr_status)
    ]):
        clinical_risk = "High"
    
    # Genomic risk
    # If recurrence score available, use it
    if 'recurrence_score' in patient_features:
        if patient_features['recurrence_score'] < 18:
            genomic_risk = "Low"
        elif patient_features['recurrence_score'] <= 30:
            genomic_risk = "Intermediate"
        else:
            genomic_risk = "High"
    else:
        # Simplified estimate based on features
        genomic_risk = "Intermediate"  # Default
        
        # Factors suggesting low genomic risk
        if er_status and pr_status and grade == 1:
            genomic_risk = "Low"
            
        # Factors suggesting high genomic risk
        if not (er_status or pr_status) or grade == 3:
            genomic_risk = "High"
    
    # Combined risk classification (simplified approach)
    if clinical_risk == "Low" and genomic_risk in ["Low", "Intermediate"]:
        combined_risk = "Low"
    elif clinical_risk == "High" and genomic_risk == "High":
        combined_risk = "High"
    else:
        combined_risk = "Intermediate"
        
    # For metastatic disease, always high risk
    if metastasis:
        clinical_risk = "High"
        combined_risk = "High"
    
    return {
        'clinical_risk': clinical_risk,
        'genomic_risk': genomic_risk,
        'combined_risk': combined_risk
    } 
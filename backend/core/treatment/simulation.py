"""
Treatment simulation models for the Cancer Digital Twin application.
These models simulate the response to various cancer treatments based on
patient characteristics and biomarker status.
"""

from typing import Dict, List, Optional, Tuple, Union, Any
import numpy as np
import math
from datetime import datetime, timedelta

def simulate_treatment_response(
    patient_data: Dict[str, Any],
    treatment_plan: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Simulate response to a treatment plan based on patient features.
    
    Args:
        patient_data: Dictionary containing patient information
        treatment_plan: Dictionary containing treatment details
        
    Returns:
        Dictionary with simulated response metrics
    """
    # Extract patient features
    age = patient_data.get('age', 60)
    grade = patient_data.get('grade', 2)
    tumor_size = patient_data.get('tumor_size', 20)  # mm
    nodes_positive = patient_data.get('nodes_positive', 0)
    er_status = patient_data.get('er_status', 'positive')
    pr_status = patient_data.get('pr_status', 'positive')
    her2_status = patient_data.get('her2_status', 'negative')
    molecular_subtype = patient_data.get('molecular_subtype', 'unknown')
    
    # Extract treatment details
    treatment_type = treatment_plan.get('treatment_type', 'unknown')
    regimen = treatment_plan.get('regimen', 'unknown')
    duration_months = treatment_plan.get('duration_months', 0)
    
    # Calculate baseline efficacy based on treatment type and molecular subtype
    efficacy = _calculate_treatment_efficacy(
        treatment_type, regimen, molecular_subtype, 
        er_status, pr_status, her2_status
    )
    
    # Adjust efficacy based on patient factors
    if age > 70:
        efficacy *= 0.9  # Reduced efficacy in elderly
    
    if grade == 3:
        efficacy *= 0.85  # High grade tumors less responsive
    
    if nodes_positive > 3:
        efficacy *= 0.8  # Extensive nodal involvement reduces efficacy
    
    # Calculate side effects risk
    side_effects_risk = calculate_side_effects(
        treatment_type, age, duration_months
    )
    
    # Calculate tumor size reduction
    tumor_reduction = _calculate_tumor_reduction(
        tumor_size, efficacy, treatment_type, duration_months
    )
    
    # Calculate survival improvement
    survival_improvement = _calculate_survival_improvement(
        efficacy, nodes_positive, grade, treatment_type
    )
    
    # Format results
    response = {
        'response_probability': efficacy,
        'tumor_size_reduction_percent': tumor_reduction,
        'side_effects_risk': side_effects_risk,
        'expected_survival_improvement_months': survival_improvement,
        'treatment_details': {
            'type': treatment_type,
            'regimen': regimen,
            'duration_months': duration_months
        }
    }
    
    return response

def simulate_treatment_sequence(
    patient_data: Dict[str, Any],
    treatment_sequence: List[Dict[str, Any]],
    time_points: Optional[List[int]] = None
) -> Dict[str, Any]:
    """
    Simulate a sequence of treatments over time.
    
    Args:
        patient_data: Dictionary containing patient information
        treatment_sequence: List of treatment plans in sequence
        time_points: List of time points (months) to report
        
    Returns:
        Dictionary with timeline of tumor size and survival probability
    """
    if time_points is None:
        time_points = [6, 12, 24, 36, 60]  # Default time points in months
    
    # Clone patient data to avoid modifying original
    current_patient = patient_data.copy()
    
    # Initialize tumor size and survival probability
    initial_tumor_size = current_patient.get('tumor_size', 20)  # mm
    current_tumor_size = initial_tumor_size
    
    # Initialize survival probability (simplified model)
    base_monthly_survival = 0.995  # 99.5% monthly survival
    if current_patient.get('nodes_positive', 0) > 0:
        base_monthly_survival = 0.990  # 99% for node positive
    
    # Initialize results
    timeline = {
        'tumor_size': {0: current_tumor_size},
        'survival_probability': {0: 1.0}
    }
    
    # Track current time
    current_month = 0
    
    # Simulate each treatment in sequence
    for treatment in treatment_sequence:
        # Simulate this treatment
        response = simulate_treatment_response(current_patient, treatment)
        
        # Treatment duration
        duration = treatment.get('duration_months', 0)
        
        # Update time
        current_month += duration
        
        # Update tumor size based on treatment response
        size_reduction = response['tumor_size_reduction_percent'] / 100
        current_tumor_size = current_tumor_size * (1 - size_reduction)
        current_tumor_size = max(0, current_tumor_size)  # Can't go below 0
        
        # Update patient with new tumor size
        current_patient['tumor_size'] = current_tumor_size
        
        # Update survival probability
        survival_improvement = response['expected_survival_improvement_months']
        adjusted_monthly_survival = base_monthly_survival * (1 + (survival_improvement / 100))
        
        # Calculate cumulative survival to this point
        cumulative_survival = 1.0
        for month in range(1, current_month + 1):
            if month in timeline['survival_probability']:
                cumulative_survival = timeline['survival_probability'][month]
            else:
                cumulative_survival *= adjusted_monthly_survival
                timeline['survival_probability'][month] = cumulative_survival
        
        # Record tumor size at this point
        timeline['tumor_size'][current_month] = current_tumor_size
    
    # Fill in missing time points
    for month in time_points:
        if month not in timeline['tumor_size']:
            # Find nearest recorded month before this one
            prev_months = [m for m in timeline['tumor_size'].keys() if m <= month]
            if prev_months:
                nearest_month = max(prev_months)
                timeline['tumor_size'][month] = timeline['tumor_size'][nearest_month]
            else:
                timeline['tumor_size'][month] = initial_tumor_size
        
        if month not in timeline['survival_probability']:
            # Find nearest recorded month before this one
            prev_months = [m for m in timeline['survival_probability'].keys() if m <= month]
            if prev_months:
                nearest_month = max(prev_months)
                months_to_extrapolate = month - nearest_month
                probability = timeline['survival_probability'][nearest_month]
                timeline['survival_probability'][month] = probability * (base_monthly_survival ** months_to_extrapolate)
            else:
                timeline['survival_probability'][month] = base_monthly_survival ** month
    
    # Format the final result
    result = {
        'time_points': sorted(set(timeline['tumor_size'].keys()).union(time_points)),
        'tumor_size': [timeline['tumor_size'].get(month, None) for month in sorted(set(timeline['tumor_size'].keys()).union(time_points))],
        'survival_probability': [timeline['survival_probability'].get(month, None) for month in sorted(set(timeline['survival_probability'].keys()).union(time_points))]
    }
    
    return result

def calculate_side_effects(
    treatment_type: str,
    patient_age: int,
    duration_months: float
) -> float:
    """
    Calculate the probability of various side effects
    
    Args:
        treatment_type: Type of treatment
        patient_age: Patient age
        duration_months: Treatment duration in months
        
    Returns:
        Probability of significant side effects
    """
    # Base risk by treatment type
    if treatment_type == 'surgery':
        base_risk = 0.05  # 5% risk of significant surgical complications
    elif treatment_type == 'chemotherapy':
        base_risk = 0.20  # 20% risk of significant chemotherapy toxicity
    elif treatment_type == 'radiation':
        base_risk = 0.10  # 10% risk of significant radiation toxicity
    elif treatment_type == 'hormone_therapy':
        base_risk = 0.05  # 5% risk of significant endocrine toxicity
    elif treatment_type == 'targeted_therapy':
        base_risk = 0.08  # 8% risk of significant targeted therapy toxicity
    else:
        base_risk = 0.05  # Default
    
    # Adjust for age
    age_factor = 1.0
    if patient_age > 70:
        age_factor = 1.5  # 50% increase in elderly
    elif patient_age < 40:
        age_factor = 0.8  # 20% decrease in young
    
    # Adjust for duration
    duration_factor = min(2.0, max(0.5, duration_months / 6))  # Scale with duration, capped
    
    # Calculate final risk
    risk = base_risk * age_factor * duration_factor
    
    return min(1.0, risk)  # Can't exceed 100%

def _calculate_treatment_efficacy(
    treatment_type: str,
    regimen: str,
    molecular_subtype: str,
    er_status: str,
    pr_status: str,
    her2_status: str
) -> float:
    """Calculate treatment efficacy based on patient and treatment factors"""
    # Base efficacy by treatment type
    if treatment_type == 'surgery':
        base_efficacy = 0.95  # 95% effective for local control
    elif treatment_type == 'chemotherapy':
        base_efficacy = 0.70  # 70% effective
    elif treatment_type == 'radiation':
        base_efficacy = 0.85  # 85% effective for local control
    elif treatment_type == 'hormone_therapy':
        base_efficacy = 0.75  # 75% effective
    elif treatment_type == 'targeted_therapy':
        base_efficacy = 0.80  # 80% effective
    else:
        base_efficacy = 0.50  # Default
    
    # Adjust for molecular subtype
    subtype_factor = 1.0
    
    if treatment_type == 'chemotherapy':
        if molecular_subtype == 'Triple Negative':
            subtype_factor = 1.2  # More effective in TNBC
        elif molecular_subtype == 'Luminal A':
            subtype_factor = 0.8  # Less effective in Luminal A
    
    elif treatment_type == 'hormone_therapy':
        if er_status == 'negative' and pr_status == 'negative':
            subtype_factor = 0.1  # Almost ineffective in ER/PR negative
        elif molecular_subtype == 'Luminal A':
            subtype_factor = 1.2  # More effective in Luminal A
    
    elif treatment_type == 'targeted_therapy':
        if her2_status == 'negative' and regimen == 'Trastuzumab':
            subtype_factor = 0.1  # Almost ineffective in HER2 negative
        elif her2_status == 'positive' and regimen == 'Trastuzumab':
            subtype_factor = 1.3  # More effective in HER2 positive
    
    # Calculate final efficacy
    efficacy = base_efficacy * subtype_factor
    
    return min(0.99, efficacy)  # Cap at 99%

def _calculate_tumor_reduction(
    tumor_size: float,
    efficacy: float,
    treatment_type: str,
    duration_months: float
) -> float:
    """Calculate expected tumor size reduction percentage"""
    # Base reduction depends on treatment type
    if treatment_type == 'surgery':
        return 100.0  # Complete removal
    
    elif treatment_type == 'chemotherapy':
        # Reduction scales with efficacy and duration
        base_reduction = 50.0  # 50% base reduction
        duration_factor = min(1.5, max(0.5, duration_months / 4))  # Scale with duration
        return base_reduction * efficacy * duration_factor
    
    elif treatment_type == 'radiation':
        # Radiation mainly affects local control
        return 60.0 * efficacy
    
    elif treatment_type in ['hormone_therapy', 'targeted_therapy']:
        # These often stabilize rather than dramatically shrink
        return 30.0 * efficacy
    
    else:
        return 10.0 * efficacy

def _calculate_survival_improvement(
    efficacy: float,
    nodes_positive: int,
    grade: int,
    treatment_type: str
) -> float:
    """Calculate expected survival improvement in months"""
    # Base improvement in months
    if treatment_type == 'surgery':
        base_improvement = 60.0  # 5 years
    elif treatment_type == 'chemotherapy':
        base_improvement = 24.0  # 2 years
    elif treatment_type == 'radiation':
        base_improvement = 12.0  # 1 year
    elif treatment_type == 'hormone_therapy':
        base_improvement = 36.0  # 3 years
    elif treatment_type == 'targeted_therapy':
        base_improvement = 24.0  # 2 years
    else:
        base_improvement = 6.0  # Default
    
    # Adjust for disease severity
    severity_factor = 1.0
    if nodes_positive > 3:
        severity_factor = 0.6  # Less benefit in extensive disease
    elif nodes_positive == 0:
        severity_factor = 1.3  # More benefit in node-negative disease
    
    if grade == 3:
        severity_factor *= 0.8  # Less benefit in high-grade disease
    
    # Final improvement
    improvement = base_improvement * efficacy * severity_factor
    
    return improvement 
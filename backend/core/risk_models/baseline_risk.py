"""
Baseline risk calculation models based on clinical factors.
These simplified models provide risk estimates based on common clinical variables.
"""

from typing import Dict, Optional, Tuple, List, Any, Union
import math
import logging

def calculate_baseline_risk(
    patient_data: Dict[str, Any]
) -> Dict[str, float]:
    """
    Calculate baseline risk of recurrence and mortality based on clinical factors.
    
    Args:
        patient_data: Dictionary containing patient information including:
            - age: Patient age
            - tumor_size: Tumor size in mm
            - nodes_positive: Number of positive lymph nodes
            - grade: Tumor grade (1-3)
            - er_status: Estrogen receptor status ('positive' or 'negative')
            - pr_status: Progesterone receptor status ('positive' or 'negative')
            - her2_status: HER2 status ('positive' or 'negative')
    
    Returns:
        Dictionary with risk scores and categories
    """
    # Extract parameters from patient data
    age = patient_data.get('age', 60)
    tumor_size_cm = patient_data.get('tumor_size', 0) / 10.0  # Convert mm to cm
    lymph_nodes_positive = patient_data.get('nodes_positive', 0)
    grade = patient_data.get('grade', 2)
    er_status = patient_data.get('er_status', 'positive')
    pr_status = patient_data.get('pr_status', 'positive')
    her2_status = patient_data.get('her2_status', 'negative')
    
    # Calculate NPI (Nottingham Prognostic Index)
    npi_score = calculate_npi_score(tumor_size_cm, lymph_nodes_positive, grade)
    
    # Base risk based on NPI
    if npi_score <= 3.4:
        base_risk_5yr = 0.05  # 5%
        base_risk_10yr = 0.1  # 10%
    elif npi_score <= 5.4:
        base_risk_5yr = 0.15  # 15%
        base_risk_10yr = 0.3  # 30%
    else:
        base_risk_5yr = 0.3  # 30%
        base_risk_10yr = 0.5  # 50%
    
    # Modify risk based on age
    age_factor = 1.0
    if age < 40:
        age_factor = 1.5
    elif age > 70:
        age_factor = 0.7
    
    # Modify risk based on receptor status
    receptor_factor = 1.0
    if er_status == 'negative' and pr_status == 'negative':
        receptor_factor = 1.5
    elif er_status == 'positive' and pr_status == 'positive':
        receptor_factor = 0.7
    
    # Adjust for HER2 status
    her2_factor = 1.2 if her2_status == 'positive' else 1.0
    
    # Calculate adjusted risks
    risk_5yr = min(0.99, base_risk_5yr * age_factor * receptor_factor * her2_factor)
    risk_10yr = min(0.99, base_risk_10yr * age_factor * receptor_factor * her2_factor)
    
    # Calculate additional risks using Adjuvant! Online inspired algorithm
    adjuvant_risk = calculate_adjuvant_online_risk(
        age, tumor_size_cm, lymph_nodes_positive, grade, 
        er_status, her2_status
    )
    
    # Get risk factors
    risk_factors = get_risk_factors(
        age, tumor_size_cm, lymph_nodes_positive, grade,
        er_status, pr_status, her2_status
    )
    
    # Combine into result dictionary
    return {
        '5_year_risk': risk_5yr * 100,  # Convert to percentage
        '10_year_risk': risk_10yr * 100,  # Convert to percentage
        'npi_score': npi_score,
        'npi_category': _get_npi_category(npi_score),
        'adjuvant_risk': adjuvant_risk,
        'risk_factors': risk_factors
    }

def calculate_npi_score(
    tumor_size_cm: float,
    lymph_nodes_positive: int,
    grade: int
) -> float:
    """
    Calculate Nottingham Prognostic Index (NPI)
    
    Args:
        tumor_size_cm: Tumor size in cm
        lymph_nodes_positive: Number of positive lymph nodes
        grade: Tumor grade (1-3)
        
    Returns:
        NPI score
    """
    # NPI = (0.2 × tumor size in cm) + lymph node stage + grade
    # Lymph node stage: 1 (0 nodes), 2 (1-3 nodes), 3 (4+ nodes)
    
    if lymph_nodes_positive == 0:
        node_stage = 1
    elif lymph_nodes_positive <= 3:
        node_stage = 2
    else:
        node_stage = 3
    
    return (0.2 * tumor_size_cm) + node_stage + grade

def _get_npi_category(npi_score: float) -> str:
    """Get NPI prognostic category"""
    if npi_score <= 3.4:
        return "Good"
    elif npi_score <= 5.4:
        return "Moderate"
    else:
        return "Poor"

def calculate_adjuvant_online_risk(
    age: int, 
    tumor_size_cm: float, 
    lymph_nodes_positive: int,
    grade: int,
    er_status: str,
    her2_status: str
) -> Dict[str, float]:
    """
    Calculate risk using a simplified version of Adjuvant! Online
    
    Args:
        age: Patient age
        tumor_size_cm: Tumor size in cm
        lymph_nodes_positive: Number of positive lymph nodes
        grade: Tumor grade (1-3)
        er_status: Estrogen receptor status ('positive' or 'negative')
        her2_status: HER2 status ('positive' or 'negative')
        
    Returns:
        Dictionary with risk estimates
    """
    # Base mortality risk
    base_mortality = 0.1  # 10% 10-year mortality
    
    # Adjust for tumor size
    if tumor_size_cm <= 1:
        size_factor = 0.7
    elif tumor_size_cm <= 2:
        size_factor = 1.0
    elif tumor_size_cm <= 5:
        size_factor = 1.3
    else:
        size_factor = 1.6
    
    # Adjust for positive nodes
    if lymph_nodes_positive == 0:
        node_factor = 1.0
    elif lymph_nodes_positive <= 3:
        node_factor = 2.0
    elif lymph_nodes_positive <= 9:
        node_factor = 3.0
    else:
        node_factor = 4.0
    
    # Adjust for grade
    grade_factor = {1: 0.7, 2: 1.0, 3: 1.5}.get(grade, 1.0)
    
    # Adjust for ER status
    er_factor = 1.5 if er_status == 'negative' else 1.0
    
    # Adjust for HER2 status
    her2_factor = 1.5 if her2_status == 'positive' else 1.0
    
    # Adjust for age
    if age < 40:
        age_factor = 1.5
    elif age < 50:
        age_factor = 1.2
    elif age < 70:
        age_factor = 1.0
    else:
        age_factor = 0.8
    
    # Calculate mortality risk
    mortality_risk = base_mortality * size_factor * node_factor * grade_factor * er_factor * her2_factor * age_factor
    mortality_risk = min(0.99, mortality_risk)
    
    # Calculate recurrence risk (typically higher than mortality)
    recurrence_risk = min(0.99, mortality_risk * 1.5)
    
    return {
        'mortality_risk': mortality_risk * 100,  # Convert to percentage
        'recurrence_risk': recurrence_risk * 100  # Convert to percentage
    }

def get_risk_factors(
    age: int, 
    tumor_size_cm: float, 
    lymph_nodes_positive: int,
    grade: int,
    er_status: str,
    pr_status: str,
    her2_status: str
) -> List[Dict[str, str]]:
    """
    Generate list of risk factors and their impact
    
    Args:
        age: Patient age
        tumor_size_cm: Tumor size in cm
        lymph_nodes_positive: Number of positive lymph nodes
        grade: Tumor grade (1-3)
        er_status: Estrogen receptor status
        pr_status: Progesterone receptor status
        her2_status: HER2 status
        
    Returns:
        List of risk factors with impact levels
    """
    risk_factors = []
    
    # Age factor
    if age < 40:
        risk_factors.append({
            'factor': 'Young age (<40)',
            'impact': 'High risk',
            'description': 'Younger patients often have more aggressive disease.'
        })
    elif age > 70:
        risk_factors.append({
            'factor': 'Older age (>70)',
            'impact': 'Lower risk',
            'description': 'Older patients often have less aggressive disease but may have comorbidities.'
        })
    
    # Tumor size
    if tumor_size_cm <= 1:
        risk_factors.append({
            'factor': 'Small tumor size (≤1cm)',
            'impact': 'Lower risk',
            'description': 'Small tumors are associated with better outcomes.'
        })
    elif tumor_size_cm > 5:
        risk_factors.append({
            'factor': 'Large tumor size (>5cm)',
            'impact': 'High risk',
            'description': 'Large tumors are associated with worse outcomes.'
        })
    
    # Lymph nodes
    if lymph_nodes_positive == 0:
        risk_factors.append({
            'factor': 'Node negative',
            'impact': 'Lower risk',
            'description': 'No cancer found in lymph nodes, indicating less spread.'
        })
    elif lymph_nodes_positive > 3:
        risk_factors.append({
            'factor': 'Multiple positive nodes (>3)',
            'impact': 'High risk',
            'description': 'Cancer found in multiple lymph nodes, indicating more spread.'
        })
    
    # Grade
    if grade == 3:
        risk_factors.append({
            'factor': 'High grade (Grade 3)',
            'impact': 'High risk',
            'description': 'Poorly differentiated cells, indicating more aggressive disease.'
        })
    elif grade == 1:
        risk_factors.append({
            'factor': 'Low grade (Grade 1)',
            'impact': 'Lower risk',
            'description': 'Well-differentiated cells, indicating less aggressive disease.'
        })
    
    # Receptor status
    if er_status == 'negative' and pr_status == 'negative':
        risk_factors.append({
            'factor': 'ER/PR negative',
            'impact': 'High risk',
            'description': 'Hormone receptor negative cancers are often more aggressive.'
        })
    elif er_status == 'positive' and pr_status == 'positive':
        risk_factors.append({
            'factor': 'ER/PR positive',
            'impact': 'Lower risk',
            'description': 'Hormone receptor positive cancers often respond well to hormone therapy.'
        })
    
    # HER2 status
    if her2_status == 'positive':
        risk_factors.append({
            'factor': 'HER2 positive',
            'impact': 'Moderate risk',
            'description': 'HER2 positive cancers can be aggressive but often respond well to targeted therapy.'
        })
    
    return risk_factors 
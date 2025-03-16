"""
Treatment recommendation models for the Cancer Digital Twin application.
These models generate personalized treatment recommendations based on 
patient characteristics, biomarker status, and clinical guidelines.
"""

from typing import Dict, List, Optional, Tuple, Union, Any
import math
import logging

def generate_treatment_recommendations(
    patient_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate personalized treatment recommendations based on patient features.
    
    Args:
        patient_data: Dictionary containing patient information
        
    Returns:
        Dictionary with recommended treatments and rationale
    """
    # Extract patient features
    age = patient_data.get('age', 60)
    tumor_size = patient_data.get('tumor_size', 20)  # mm
    nodes_positive = patient_data.get('nodes_positive', 0)
    grade = patient_data.get('grade', 2)
    er_status = patient_data.get('er_status', 'positive')
    pr_status = patient_data.get('pr_status', 'positive')
    her2_status = patient_data.get('her2_status', 'negative')
    molecular_subtype = patient_data.get('molecular_subtype', 'unknown')
    
    # Get NCCN guideline treatments
    nccn_treatments = get_nccn_guideline_treatments(
        molecular_subtype, tumor_size, nodes_positive, grade
    )
    
    # Initialize recommendations
    recommended_treatments = []
    
    # Add surgical options
    if tumor_size <= 30:  # Tumors <= 3cm may be eligible for breast conservation
        recommended_treatments.append({
            'treatment_type': 'surgery',
            'regimen': 'Breast Conserving Surgery',
            'duration_months': 1,
            'rationale': 'Tumor size and clinical presentation are suitable for breast conservation.'
        })
    
    recommended_treatments.append({
        'treatment_type': 'surgery',
        'regimen': 'Mastectomy',
        'duration_months': 1,
        'rationale': 'Alternative surgical approach with lower local recurrence risk.'
    })
    
    # Add radiation therapy if breast conservation is planned
    if tumor_size <= 30:
        recommended_treatments.append({
            'treatment_type': 'radiation',
            'regimen': 'Whole Breast Radiation',
            'duration_months': 1.5,  # 6 weeks
            'rationale': 'Standard adjuvant therapy after breast conserving surgery.'
        })
    
    # Add systemic therapy based on subtype and stage
    # Hormone positive disease
    if er_status == 'positive' or pr_status == 'positive':
        recommended_treatments.append({
            'treatment_type': 'hormone_therapy',
            'regimen': 'Tamoxifen' if age < 50 else 'Aromatase Inhibitor',
            'duration_months': 60,  # 5 years
            'rationale': 'Hormone receptor positive disease benefits from endocrine therapy.'
        })
    
    # Check for chemotherapy indications
    chemo_indicated = False
    chemo_rationale = []
    
    if nodes_positive > 0:
        chemo_indicated = True
        chemo_rationale.append('Positive lymph nodes')
    
    if grade == 3:
        chemo_indicated = True
        chemo_rationale.append('High grade disease')
    
    if tumor_size > 20:
        chemo_indicated = True
        chemo_rationale.append('Tumor size > 2cm')
    
    if er_status == 'negative' and pr_status == 'negative':
        chemo_indicated = True
        chemo_rationale.append('Triple negative disease')
    
    if her2_status == 'positive':
        chemo_indicated = True
        chemo_rationale.append('HER2 positive disease')
    
    if molecular_subtype in ['Luminal B', 'HER2 Enriched', 'Triple Negative', 'Luminal B HER2+']:
        chemo_indicated = True
        chemo_rationale.append(f'{molecular_subtype} molecular subtype')
    
    # Add chemotherapy if indicated
    if chemo_indicated:
        chemo_regimen = 'TC' if nodes_positive == 0 else 'AC-T'
        
        recommended_treatments.append({
            'treatment_type': 'chemotherapy',
            'regimen': chemo_regimen,
            'duration_months': 3 if nodes_positive == 0 else 6,
            'rationale': 'Chemotherapy indicated due to: ' + ', '.join(chemo_rationale)
        })
    
    # Add targeted therapy for HER2+ disease
    if her2_status == 'positive':
        recommended_treatments.append({
            'treatment_type': 'targeted_therapy',
            'regimen': 'Trastuzumab',
            'duration_months': 12,
            'rationale': 'HER2 targeted therapy improves outcomes in HER2 positive disease.'
        })
    
    # Check for contraindications
    final_recommendations = []
    for treatment in recommended_treatments:
        contraindications = check_treatment_contraindications(treatment, patient_data)
        
        if not contraindications:
            final_recommendations.append(treatment)
        else:
            # You can handle contraindications here, e.g., adding them to the response
            # or modifying treatments as needed
            pass
    
    return {
        'recommended_treatments': final_recommendations,
        'nccn_guideline_treatments': nccn_treatments,
        'patient_factors': {
            'age': age,
            'tumor_size': tumor_size,
            'nodes_positive': nodes_positive,
            'grade': grade,
            'er_status': er_status,
            'pr_status': pr_status,
            'her2_status': her2_status,
            'molecular_subtype': molecular_subtype
        }
    }

def get_nccn_guideline_treatments(
    molecular_subtype: str,
    tumor_size: float,
    nodes_positive: int,
    grade: int
) -> List[Dict[str, str]]:
    """
    Get NCCN guideline-based treatment recommendations
    
    Args:
        molecular_subtype: Cancer molecular subtype
        tumor_size: Tumor size in mm
        nodes_positive: Number of positive lymph nodes
        grade: Tumor grade
        
    Returns:
        List of NCCN guideline treatments
    """
    treatments = []
    
    # Early-stage disease (T1-2, N0)
    if tumor_size <= 50 and nodes_positive == 0:
        if molecular_subtype in ['Luminal A', 'Luminal B HER2-']:
            treatments.append({
                'type': 'Endocrine Therapy',
                'regimen': 'Tamoxifen or Aromatase Inhibitor',
                'duration': '5-10 years',
                'priority': 'Standard of care'
            })
            
            if grade >= 2 or tumor_size > 20 or molecular_subtype == 'Luminal B HER2-':
                treatments.append({
                    'type': 'Chemotherapy',
                    'regimen': 'TC, AC, or CMF',
                    'duration': '3-6 months',
                    'priority': 'Consider'
                })
                
        elif molecular_subtype in ['Luminal B HER2+', 'HER2 Enriched']:
            treatments.append({
                'type': 'Chemotherapy + HER2-targeted therapy',
                'regimen': 'AC-TH or TCH',
                'duration': '12 months of HER2-therapy',
                'priority': 'Standard of care'
            })
            
            if molecular_subtype == 'Luminal B HER2+':
                treatments.append({
                    'type': 'Endocrine Therapy',
                    'regimen': 'Tamoxifen or Aromatase Inhibitor',
                    'duration': '5-10 years',
                    'priority': 'Standard of care'
                })
                
        elif molecular_subtype == 'Triple Negative':
            treatments.append({
                'type': 'Chemotherapy',
                'regimen': 'AC-T or TC',
                'duration': '3-6 months',
                'priority': 'Standard of care'
            })
    
    # Node-positive or larger tumors
    else:
        if molecular_subtype in ['Luminal A', 'Luminal B HER2-']:
            treatments.append({
                'type': 'Chemotherapy',
                'regimen': 'AC-T or TC',
                'duration': '4-6 months',
                'priority': 'Standard of care'
            })
            
            treatments.append({
                'type': 'Endocrine Therapy',
                'regimen': 'Tamoxifen or Aromatase Inhibitor',
                'duration': '5-10 years',
                'priority': 'Standard of care'
            })
                
        elif molecular_subtype in ['Luminal B HER2+', 'HER2 Enriched']:
            treatments.append({
                'type': 'Chemotherapy + HER2-targeted therapy',
                'regimen': 'AC-TH or TCH',
                'duration': '12 months of HER2-therapy',
                'priority': 'Standard of care'
            })
            
            if molecular_subtype == 'Luminal B HER2+':
                treatments.append({
                    'type': 'Endocrine Therapy',
                    'regimen': 'Tamoxifen or Aromatase Inhibitor',
                    'duration': '5-10 years',
                    'priority': 'Standard of care'
                })
                
        elif molecular_subtype == 'Triple Negative':
            treatments.append({
                'type': 'Chemotherapy',
                'regimen': 'AC-T',
                'duration': '6 months',
                'priority': 'Standard of care'
            })
    
    return treatments

def check_treatment_contraindications(
    treatment: Dict[str, str],
    patient_data: Dict[str, Any]
) -> List[str]:
    """
    Check for contraindications to specific treatments
    
    Args:
        treatment: Treatment plan
        patient_data: Patient features
        
    Returns:
        List of contraindications, empty if none
    """
    contraindications = []
    
    # Extract patient features
    age = patient_data.get('age', 60)
    
    # Contraindications vary by treatment type
    treatment_type = treatment.get('treatment_type', '')
    
    if treatment_type == 'chemotherapy':
        # Example contraindications
        if age > 80:
            contraindications.append("Age > 80 years may increase risk of chemotherapy toxicity")
    
    elif treatment_type == 'hormone_therapy':
        regimen = treatment.get('regimen', '')
        if regimen == 'Tamoxifen' and age > 55:
            contraindications.append("Aromatase inhibitors preferred over tamoxifen in postmenopausal women")
    
    return contraindications 
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, validator

from backend.core.digital_twin.biomarker import BiomarkerStatus

class PatientDigitalTwin(BaseModel):
    patient_id: str
    age: int
    tumor_size_cm: float
    lymph_nodes_positive: int
    grade: int  # 1, 2, or 3
    biomarker_status: BiomarkerStatus
    metastasis: bool = False
    comorbidities: List[str] = []
    
    # Additional clinical data
    treatments_history: List[Dict] = []
    imaging_references: Dict[str, str] = {}  # References to imaging data files
    genomic_data: Optional[Dict] = None
    
    # Cached prediction results
    _risk_predictions: Dict = {}
    _treatment_predictions: Dict = {}
    _progression_predictions: Dict = {}
    
    @validator('grade')
    def validate_grade(cls, v):
        if v not in [1, 2, 3]:
            raise ValueError('Grade must be 1, 2, or 3')
        return v
    
    def calculate_baseline_risk(self) -> float:
        """Calculate baseline recurrence risk using a simplified model"""
        # This would be replaced with more sophisticated models like Oncotype DX, MammaPrint, etc.
        base_risk = 0.0
        
        # Age factor (simplified)
        if self.age < 40:
            base_risk += 0.10
        elif self.age < 50:
            base_risk += 0.05
            
        # Tumor size factor (simplified)
        base_risk += min(0.3, self.tumor_size_cm * 0.05)
        
        # Lymph node factor (simplified)
        base_risk += min(0.4, self.lymph_nodes_positive * 0.08)
        
        # Grade factor
        if self.grade == 3:
            base_risk += 0.15
        elif self.grade == 2:
            base_risk += 0.07
            
        # Biomarker factor (simplified)
        if not (self.biomarker_status.er_status or self.biomarker_status.pr_status):
            base_risk += 0.1
        if self.biomarker_status.her2_status:
            base_risk += 0.05
            
        # Metastasis factor
        if self.metastasis:
            base_risk += 0.3
            
        # Ensure risk is between 0 and 1
        return min(0.95, base_risk)
    
    def simulate_treatment_response(self, treatment_plan: Dict) -> Dict:
        """Simulate the response to a given treatment plan"""
        # Validate treatment plan contains required fields
        required_fields = ['treatment_type', 'duration_weeks', 'dosage']
        for field in required_fields:
            if field not in treatment_plan:
                raise ValueError(f"Treatment plan missing required field: {field}")
        
        treatment_type = treatment_plan['treatment_type']
        molecular_subtype = self.biomarker_status.get_molecular_subtype()
        
        # Get base efficacy for the treatment type and molecular subtype
        efficacy = self._get_treatment_base_efficacy(treatment_type, molecular_subtype)
        
        # Adjust for patient factors
        if self.age > 70:
            efficacy *= 0.9  # Reduced efficacy in elderly patients
        
        if self.grade == 3:
            efficacy *= 0.85  # Aggressive tumors may be less responsive
            
        # Adjust for metastasis
        if self.metastasis:
            efficacy *= 0.7  # Metastatic disease harder to treat
            
        # Calculate side effect probability
        side_effects = self._calculate_side_effects(treatment_type)
        
        # Calculate tumor size reduction (simplified model)
        initial_size = self.tumor_size_cm
        expected_size_reduction = initial_size * efficacy
        predicted_size = max(0, initial_size - expected_size_reduction)
        
        return {
            'efficacy': efficacy,
            'side_effects': side_effects,
            'predicted_tumor_size': predicted_size,
            'tumor_size_reduction_percent': (initial_size - predicted_size) / initial_size * 100 if initial_size > 0 else 0
        }
    
    def _get_treatment_base_efficacy(self, treatment_type: str, molecular_subtype: str) -> float:
        """Get base efficacy for treatment type and molecular subtype"""
        # This would be replaced with data-driven models
        efficacy_matrix = {
            'chemotherapy': {
                'Triple Negative': 0.65,
                'HER2 Enriched': 0.60,
                'Luminal A': 0.50,
                'Luminal B HER2-': 0.55,
                'Luminal B HER2+': 0.60
            },
            'hormone_therapy': {
                'Triple Negative': 0.05,
                'HER2 Enriched': 0.10,
                'Luminal A': 0.75,
                'Luminal B HER2-': 0.65,
                'Luminal B HER2+': 0.60
            },
            'targeted_therapy': {
                'Triple Negative': 0.30,
                'HER2 Enriched': 0.80,
                'Luminal A': 0.40,
                'Luminal B HER2-': 0.45,
                'Luminal B HER2+': 0.75
            },
            'surgery': {
                'Triple Negative': 0.85,
                'HER2 Enriched': 0.85,
                'Luminal A': 0.90,
                'Luminal B HER2-': 0.85,
                'Luminal B HER2+': 0.85
            },
            'radiation': {
                'Triple Negative': 0.70,
                'HER2 Enriched': 0.70,
                'Luminal A': 0.75,
                'Luminal B HER2-': 0.72,
                'Luminal B HER2+': 0.72
            }
        }
        
        if treatment_type not in efficacy_matrix:
            raise ValueError(f"Unknown treatment type: {treatment_type}")
            
        return efficacy_matrix[treatment_type].get(molecular_subtype, 0.5)
    
    def _calculate_side_effects(self, treatment_type: str) -> Dict[str, float]:
        """Calculate probability of different side effects"""
        # Base side effect probabilities by treatment
        side_effects = {
            'chemotherapy': {
                'nausea': 0.7, 
                'hair_loss': 0.9, 
                'fatigue': 0.8, 
                'neutropenia': 0.4
            },
            'hormone_therapy': {
                'hot_flashes': 0.6, 
                'joint_pain': 0.4, 
                'mood_changes': 0.3
            },
            'targeted_therapy': {
                'skin_rash': 0.5, 
                'diarrhea': 0.3, 
                'heart_problems': 0.1
            },
            'surgery': {
                'infection': 0.1, 
                'lymphedema': 0.2, 
                'pain': 0.5
            },
            'radiation': {
                'skin_changes': 0.8, 
                'fatigue': 0.6, 
                'local_pain': 0.5
            }
        }
        
        base_effects = side_effects.get(treatment_type, {'unknown': 0.1})
        
        # Adjust for age
        age_factor = 1.0 + max(0, (self.age - 50) / 100)
        
        # Apply age factor to each side effect
        return {effect: min(0.99, prob * age_factor) for effect, prob in base_effects.items()}
    
    def project_disease_progression(self, months: int = 12, treatment_plan: Optional[Dict] = None) -> Dict:
        """Project disease progression over time"""
        # Start with current state
        current_size = self.tumor_size_cm
        current_risk = self.calculate_baseline_risk()
        
        # Apply treatment effect if provided
        if treatment_plan:
            treatment_response = self.simulate_treatment_response(treatment_plan)
            initial_reduction = treatment_response['tumor_size_reduction_percent'] / 100
            current_size = current_size * (1 - initial_reduction)
            
        # Model growth over time (simplified)
        # In reality this would use much more sophisticated models
        monthly_progression = []
        
        # Different growth rates based on molecular subtype and grade
        growth_rate = 0.05  # 5% per month base rate
        
        # Adjust for biomarker status
        if not (self.biomarker_status.er_status or self.biomarker_status.pr_status):
            growth_rate *= 1.5  # Faster growth for hormone-negative
            
        # Adjust for grade
        if self.grade == 3:
            growth_rate *= 1.3
        elif self.grade == 1:
            growth_rate *= 0.7
            
        # Generate monthly projections
        for month in range(1, months + 1):
            # Apply growth rate (exponential growth model)
            if treatment_plan and month <= treatment_plan.get('duration_weeks', 0) / 4:
                # During active treatment, growth is suppressed
                current_size *= (1 + growth_rate * 0.2)
            else:
                current_size *= (1 + growth_rate)
            
            # Calculate survival probability (simplified)
            survival_prob = max(0, 1 - (current_risk * (1 + month/24)))
            
            monthly_progression.append({
                'month': month,
                'tumor_size_cm': round(current_size, 2),
                'survival_probability': round(survival_prob, 2)
            })
            
        return {
            'monthly_progression': monthly_progression,
            'final_tumor_size': round(current_size, 2),
            'final_survival_probability': round(max(0, 1 - (current_risk * (1 + months/24))), 2)
        }

    def recommend_treatments(self) -> List[Dict]:
        """Recommend personalized treatment plans"""
        molecular_subtype = self.biomarker_status.get_molecular_subtype()
        treatments = []
        
        # Surgery recommendation
        if self.tumor_size_cm >= 1.0:
            treatments.append({
                'treatment_type': 'surgery',
                'name': 'Surgical Resection',
                'recommendation_strength': 'Strong',
                'efficacy_estimate': self._get_treatment_base_efficacy('surgery', molecular_subtype),
                'rationale': 'Tumor size indicates surgical intervention',
                'recommended_duration': 1  # Weeks
            })
        
        # Chemotherapy recommendation
        chemo_indicated = (self.grade >= 2 or self.lymph_nodes_positive > 0 or 
                          molecular_subtype == 'Triple Negative' or 
                          molecular_subtype == 'HER2 Enriched')
        
        if chemo_indicated:
            treatments.append({
                'treatment_type': 'chemotherapy',
                'name': 'Adjuvant Chemotherapy',
                'recommendation_strength': 'Strong' if self.grade == 3 else 'Moderate',
                'efficacy_estimate': self._get_treatment_base_efficacy('chemotherapy', molecular_subtype),
                'rationale': f"Indicated for {molecular_subtype} with grade {self.grade}",
                'recommended_duration': 12  # Weeks
            })
        
        # Hormone therapy recommendation
        if self.biomarker_status.er_status or self.biomarker_status.pr_status:
            treatments.append({
                'treatment_type': 'hormone_therapy',
                'name': 'Hormone Therapy',
                'recommendation_strength': 'Strong',
                'efficacy_estimate': self._get_treatment_base_efficacy('hormone_therapy', molecular_subtype),
                'rationale': 'Hormone receptor positive status',
                'recommended_duration': 52  # Weeks (often years in practice)
            })
        
        # Targeted therapy recommendation
        if self.biomarker_status.her2_status:
            treatments.append({
                'treatment_type': 'targeted_therapy',
                'name': 'HER2-Targeted Therapy',
                'recommendation_strength': 'Strong',
                'efficacy_estimate': self._get_treatment_base_efficacy('targeted_therapy', molecular_subtype),
                'rationale': 'HER2 positive status',
                'recommended_duration': 52  # Weeks
            })
        
        # Radiation recommendation
        if self.tumor_size_cm >= 5.0 or self.lymph_nodes_positive > 0:
            treatments.append({
                'treatment_type': 'radiation',
                'name': 'Radiation Therapy',
                'recommendation_strength': 'Strong' if self.lymph_nodes_positive > 3 else 'Moderate',
                'efficacy_estimate': self._get_treatment_base_efficacy('radiation', molecular_subtype),
                'rationale': f"Indicated for tumor size {self.tumor_size_cm}cm with {self.lymph_nodes_positive} positive nodes",
                'recommended_duration': 6  # Weeks
            })
            
        return treatments 
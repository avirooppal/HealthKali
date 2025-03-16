"""
Fallback implementations of core functions in case the actual modules are not available
"""

import random
import math
from datetime import datetime

# ... [existing fallback functions] ...

class MockOutcomePrediction:
    """Mock implementation of the OutcomePrediction class"""
    
    def predict_survival(self, patient_data, years=5):
        """Mock survival prediction"""
        survival_curve = []
        cumulative_survival = 1.0
        yearly_survival = 0.95  # 95% annual survival rate
        
        for year in range(1, years + 1):
            cumulative_survival *= yearly_survival
            survival_curve.append({
                'year': year,
                'survival_probability': round(cumulative_survival, 3)
            })
        
        return {
            'prediction_type': 'survival',
            'patient_risk_category': 'Intermediate Risk',
            'overall_5yr_survival': round(cumulative_survival, 2),
            'survival_curve': survival_curve,
            'timestamp': datetime.now().isoformat()
        }
    
    def predict_recurrence(self, patient_data, years=5):
        """Mock recurrence prediction"""
        return {
            'prediction_type': 'recurrence',
            'total_recurrence_5yr': 0.15,
            'recurrence_breakdown': {
                'local_recurrence': 0.05,
                'regional_recurrence': 0.03,
                'distant_metastasis': 0.07
            },
            'recurrence_category': 'Intermediate Risk',
            'timestamp': datetime.now().isoformat()
        }
    
    def predict_treatment_response(self, patient_data, treatment_plan):
        """Mock treatment response prediction"""
        return {
            'prediction_type': 'treatment_response',
            'overall_response_probability': 0.75,
            'treatment_specific_responses': {
                'chemotherapy': 0.65,
                'endocrine': 0.70
            },
            'efficacy_category': 'Good',
            'timestamp': datetime.now().isoformat()
        }

class MockCancerSimulation:
    """Mock implementation of the CancerSimulation class"""
    
    def simulate_disease_course(self, patient_data, treatment_plan=None, months=60, num_simulations=10):
        """Mock disease course simulation"""
        return {
            'simulation_type': 'disease_course',
            'total_months': months,
            'num_simulations': num_simulations,
            'state_probabilities': {
                'NED': 0.75,
                'Local Recurrence': 0.05,
                'Regional Recurrence': 0.05,
                'Distant Metastasis': 0.10,
                'Death': 0.05
            },
            'state_probability_trajectory': [
                {'month': 0, 'NED': 1.0, 'Local Recurrence': 0.0, 'Regional Recurrence': 0.0, 'Distant Metastasis': 0.0, 'Death': 0.0},
                {'month': 60, 'NED': 0.75, 'Local Recurrence': 0.05, 'Regional Recurrence': 0.05, 'Distant Metastasis': 0.10, 'Death': 0.05}
            ],
            'timestamp': datetime.now().isoformat()
        }
    
    def simulate_treatment_scenario(self, patient_data, scenarios, months=60):
        """Mock treatment scenario simulation"""
        results = {}
        
        for scenario in scenarios:
            scenario_name = scenario.get('name', f"Scenario {len(results) + 1}")
            
            results[scenario_name] = {
                'ned_at_5yr': 0.75,
                'recurrence_at_5yr': 0.20,
                'mortality_at_5yr': 0.05
            }
        
        return {
            'simulation_type': 'treatment_comparison',
            'months_simulated': months,
            'scenarios': results,
            'optimal_scenario': next(iter(results.keys())) if results else None,
            'timestamp': datetime.now().isoformat()
        }
    
    def simulate_molecular_subtypes(self, patient_data, months=60):
        """Mock molecular subtype simulation"""
        subtypes = ["Luminal A", "Luminal B", "HER2-enriched", "Triple Negative"]
        results = {}
        
        for subtype in subtypes:
            results[subtype] = {
                'ned_at_5yr': 0.75 if subtype == "Luminal A" else 0.65 if subtype == "Luminal B" else 0.55 if subtype == "HER2-enriched" else 0.50,
                'recurrence_at_5yr': 0.20 if subtype == "Luminal A" else 0.25 if subtype == "Luminal B" else 0.35 if subtype == "HER2-enriched" else 0.40,
                'mortality_at_5yr': 0.05 if subtype == "Luminal A" else 0.10 if subtype == "Luminal B" else 0.10 if subtype == "HER2-enriched" else 0.10
            }
        
        return {
            'simulation_type': 'molecular_subtype_comparison',
            'months_simulated': months,
            'subtype_outcomes': results,
            'patient_actual_subtype': patient_data.get('molecular_subtype', 'Unknown'),
            'timestamp': datetime.now().isoformat()
        }
"""
Test script for Cancer Digital Twin core functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.utils.config import Config
from backend.core.utils.helpers import setup_logging, validate_patient_data
from backend.core.risk_models import calculate_baseline_risk
from backend.core.treatment import simulate_treatment_response
from backend.core.progression.models import ProgressionSimulator

def test_patient_workflow():
    # Initialize configuration and logging
    config = Config('config/default.yaml')
    setup_logging(config.get('logging.file'))
    
    # Test patient data
    patient_data = {
        'age': 55,
        'tumor_size': 25,  # mm
        'grade': 2,
        'nodes_positive': 1,
        'er_status': 'positive',
        'pr_status': 'positive',
        'her2_status': 'negative',
        'molecular_subtype': 'Luminal A'
    }
    
    # Validate patient data
    is_valid, error = validate_patient_data(patient_data)
    print(f"Patient data validation: {'Success' if is_valid else f'Failed - {error}'}")
    
    if is_valid:
        # Calculate baseline risk
        risk_assessment = calculate_baseline_risk(patient_data)
        print("\nRisk Assessment:")
        print(f"5-year risk: {risk_assessment['5_year_risk']:.2f}%")
        print(f"10-year risk: {risk_assessment['10_year_risk']:.2f}%")
        
        # Simulate treatment response
        treatment_plan = {
            'treatment_type': 'chemotherapy',
            'regimen': 'AC-T',
            'duration_months': 6
        }
        
        response = simulate_treatment_response(patient_data, treatment_plan)
        print("\nTreatment Response Simulation:")
        print(f"Response probability: {response['response_probability']:.2f}")
        print(f"Side effects risk: {response['side_effects_risk']:.2f}")
        
        # Simulate disease progression
        simulator = ProgressionSimulator()
        progression = simulator.simulate_progression(
            patient_data,
            months=60,
            n_simulations=100
        )
        
        print("\nDisease Progression Simulation:")
        for state, prob in progression.items():
            print(f"{state}: {prob:.2f}")

if __name__ == "__main__":
    test_patient_workflow() 
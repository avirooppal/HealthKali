"""
Test client for Cancer Digital Twin API
"""

import requests
import json

def test_api():
    base_url = "http://localhost:8000"
    
    # Test patient data
    patient_data = {
        'age': 55,
        'tumor_size': 25,
        'grade': 2,
        'nodes_positive': 1,
        'er_status': 'positive',
        'pr_status': 'positive',
        'her2_status': 'negative',
        'molecular_subtype': 'Luminal A'
    }
    
    # Test treatment plan
    treatment_plan = {
        'treatment_type': 'chemotherapy',
        'regimen': 'AC-T',
        'duration_months': 6
    }
    
    # Test risk assessment
    print("Testing risk assessment...")
    response = requests.post(f"{base_url}/risk-assessment", json=patient_data)
    print(json.dumps(response.json(), indent=2))
    
    # Test treatment simulation
    print("\nTesting treatment simulation...")
    response = requests.post(
        f"{base_url}/treatment-simulation",
        json={'patient': patient_data, 'treatment': treatment_plan}
    )
    print(json.dumps(response.json(), indent=2))
    
    # Test disease progression
    print("\nTesting disease progression...")
    response = requests.post(
        f"{base_url}/disease-progression",
        json={'patient': patient_data, 'months': 60, 'simulations': 100}
    )
    print(json.dumps(response.json(), indent=2))
    
    # Test treatment recommendations
    print("\nTesting treatment recommendations...")
    response = requests.post(
        f"{base_url}/treatment-recommendations",
        json=patient_data
    )
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    test_api() 
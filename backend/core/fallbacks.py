"""
Fallback functions for generating mock data when actual models are not available.
These are used to ensure the API can always return reasonable responses.
"""

import random
import math
from typing import Dict, List, Any, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def mock_patient_risk_level(patient_data: Dict[str, Any]) -> float:
    """Calculate a mock risk level (0-1) based on patient data"""
    risk = 0.0
    
    # Age-based risk (higher for very young or older patients)
    age = patient_data.get('age', 50)
    if age < 40:
        risk += 0.1  # Younger patients often have more aggressive disease
    elif age > 65:
        risk += 0.15  # Older patients have higher baseline risk
        
    # Tumor characteristics
    tumor_size = patient_data.get('tumor_size', 20)
    if tumor_size > 30:
        risk += 0.2
    elif tumor_size > 20:
        risk += 0.1
        
    # Grade-based risk
    grade = patient_data.get('grade', 2)
    if grade == 3:
        risk += 0.2
    elif grade == 2:
        risk += 0.1
        
    # Lymph node involvement
    nodes_positive = patient_data.get('nodes_positive', 0)
    if nodes_positive > 3:
        risk += 0.3
    elif nodes_positive > 0:
        risk += 0.2
        
    # Biomarker status
    er_status = patient_data.get('er_status', 'positive')
    her2_status = patient_data.get('her2_status', 'negative')
    
    if er_status == 'negative':
        risk += 0.15
    if her2_status == 'positive':
        risk += 0.1
        
    # Cap and normalize risk
    return min(0.9, risk)

def generate_mock_survival_prediction(patient_data: Dict[str, Any], years: int = 5) -> Dict[str, Any]:
    """Generate mock survival prediction data"""
    logger.info("Generating mock survival prediction")
    
    # Calculate a mock risk level
    base_risk = mock_patient_risk_level(patient_data)
    
    # Calculate 5-year survival probability
    survival_5yr = 1.0 - base_risk
    
    # Generate survival curve
    survival_curve = []
    for year in range(1, years + 1):
        # Compound annual survival risk
        annual_risk = base_risk / 5.0
        
        # Survival follows a somewhat non-linear curve
        time_factor = math.log(year + 1) / math.log(years + 1)
        year_survival = math.exp(-annual_risk * year * (1 + time_factor))
        
        # Add some randomness
        year_survival = max(0.1, min(1.0, year_survival * (1 + random.uniform(-0.02, 0.02))))
        
        survival_curve.append({
            "year": year,
            "survival_probability": round(year_survival, 4)
        })
    
    # Generate confidence intervals
    lower_ci = []
    upper_ci = []
    for point in survival_curve:
        year_survival = point["survival_probability"]
        ci_width = 0.05 + 0.02 * math.sqrt(point["year"])  # CI gets wider over time
        
        lower_val = max(0.01, year_survival - ci_width)
        upper_val = min(1.0, year_survival + ci_width)
        
        lower_ci.append({
            "year": point["year"],
            "survival_probability": round(lower_val, 4)
        })
        
        upper_ci.append({
            "year": point["year"],
            "survival_probability": round(upper_val, 4)
        })
    
    # Get risk modifiers
    modifiers = {
        "age": 1.0,
        "grade": 1.0,
        "nodes": 1.0,
        "size": 1.0,
        "er": 1.0,
        "her2": 1.0
    }
    
    age = patient_data.get('age', 50)
    if age > 65:
        modifiers["age"] = 0.9
    elif age < 40:
        modifiers["age"] = 0.95
    else:
        modifiers["age"] = 1.05
        
    grade = patient_data.get('grade', 2)
    if grade == 3:
        modifiers["grade"] = 0.85
    elif grade == 1:
        modifiers["grade"] = 1.15
        
    nodes_positive = patient_data.get('nodes_positive', 0)
    if nodes_positive > 0:
        modifiers["nodes"] = 0.8
    else:
        modifiers["nodes"] = 1.15
        
    tumor_size = patient_data.get('tumor_size', 20)
    if tumor_size > 30:
        modifiers["size"] = 0.85
    elif tumor_size < 10:
        modifiers["size"] = 1.1
        
    er_status = patient_data.get('er_status', 'positive')
    if er_status == 'positive':
        modifiers["er"] = 1.2
    else:
        modifiers["er"] = 0.75
        
    her2_status = patient_data.get('her2_status', 'negative')
    if her2_status == 'positive':
        modifiers["her2"] = 0.95
        
    # Determine risk category
    risk_category = "High Risk"
    if survival_5yr > 0.9:
        risk_category = "Low Risk"
    elif survival_5yr > 0.8:
        risk_category = "Intermediate Risk"
    
    return {
        "patient_risk_category": risk_category,
        "overall_5yr_survival": round(survival_5yr, 4),
        "survival_curve": survival_curve,
        "lower_ci": lower_ci,
        "upper_ci": upper_ci,
        "modifiers": modifiers
    }

def generate_mock_recurrence_prediction(patient_data: Dict[str, Any], years: int = 5) -> Dict[str, Any]:
    """Generate mock recurrence prediction data"""
    logger.info("Generating mock recurrence prediction")
    
    # Calculate a mock risk level
    base_risk = mock_patient_risk_level(patient_data)
    
    # Calculate 5-year recurrence probability (inverse of survival)
    recurrence_5yr = base_risk * 0.9  # Small adjustment as not all deaths are due to recurrence
    
    # Distribution of recurrence by type
    # Usually more local than regional, and more regional than distant, but some variance
    local_fraction = 0.4 + random.uniform(-0.1, 0.1)
    regional_fraction = 0.3 + random.uniform(-0.1, 0.1)
    distant_fraction = 1.0 - local_fraction - regional_fraction
    
    # Adjust fractions based on nodes positive (more nodes = more distant risk)
    nodes_positive = patient_data.get('nodes_positive', 0)
    if nodes_positive > 0:
        distant_adjustment = min(0.2, nodes_positive * 0.05)
        local_fraction -= distant_adjustment / 2
        regional_fraction -= distant_adjustment / 2
        distant_fraction += distant_adjustment
    
    # Calculate type-specific recurrence rates
    local_recurrence = recurrence_5yr * local_fraction
    regional_recurrence = recurrence_5yr * regional_fraction
    distant_metastasis = recurrence_5yr * distant_fraction
    
    # Generate recurrence curves over time
    def generate_recurrence_curve(recurrence_type, total_rate):
        curve = []
        # Cumulative rate increases over time
        # Different curve shapes for different recurrence types
        for year in range(1, years + 1):
            if recurrence_type == 'local':
                # Local tends to be more uniform
                year_rate = total_rate * (year / years) * (1 + random.uniform(-0.1, 0.1))
            elif recurrence_type == 'regional':
                # Regional peaks slightly later
                year_rate = total_rate * (year / years) ** 1.1 * (1 + random.uniform(-0.1, 0.1))
            else:  # distant
                # Distant can have later peaks
                year_rate = total_rate * (year / years) ** 1.2 * (1 + random.uniform(-0.1, 0.1))
            
            curve.append({
                "year": year,
                "recurrence_probability": round(min(year_rate, total_rate), 4)
            })
        return curve
    
    recurrence_curves = {
        "local": generate_recurrence_curve('local', local_recurrence),
        "regional": generate_recurrence_curve('regional', regional_recurrence),
        "distant": generate_recurrence_curve('distant', distant_metastasis)
    }
    
    # Determine recurrence category
    recurrence_category = "High Risk"
    if recurrence_5yr < 0.1:
        recurrence_category = "Low Risk"
    elif recurrence_5yr < 0.2:
        recurrence_category = "Intermediate Risk"
    
    return {
        "recurrence_category": recurrence_category,
        "total_recurrence_5yr": round(recurrence_5yr, 4),
        "recurrence_breakdown": {
            "local_recurrence": round(local_recurrence, 4),
            "regional_recurrence": round(regional_recurrence, 4),
            "distant_metastasis": round(distant_metastasis, 4)
        },
        "recurrence_curves": recurrence_curves
    }

def generate_mock_treatment_response(patient_data: Dict[str, Any], treatment_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate mock treatment response prediction data"""
    logger.info("Generating mock treatment response prediction")
    
    treatments = treatment_data.get('treatments', [])
    
    # Base response rate
    base_response = 0.7  # Most cancer treatments have some effect
    
    # Treatment specific responses
    treatment_responses = {}
    side_effects = {}
    
    for treatment in treatments:
        response_rate = base_response
        
        # Adjust based on treatment type and patient characteristics
        if treatment == 'surgery':
            # Surgery has high local control
            response_rate = 0.9
            
            # Adjustments
            tumor_size = patient_data.get('tumor_size', 20)
            if tumor_size > 50:  # Very large tumors
                response_rate *= 0.8
                
            # Side effects
            side_effects['surgery'] = {
                'pain': 0.7 + random.uniform(-0.1, 0.1),
                'infection': 0.05 + random.uniform(-0.02, 0.05),
                'seroma': 0.2 + random.uniform(-0.05, 0.1),
                'scarring': 0.9 + random.uniform(-0.05, 0.05),
                'lymphedema': min(0.5, (patient_data.get('nodes_positive', 0) * 0.1))
            }
                
        elif treatment == 'chemotherapy':
            # Chemo effectiveness varies by molecular subtype
            response_rate = 0.65
            
            # More effective in high grade tumors
            if patient_data.get('grade', 2) == 3:
                response_rate += 0.1
            
            # Less effective in ER+ disease
            if patient_data.get('er_status', 'positive') == 'positive':
                response_rate -= 0.1
                
            # More effective in HER2+ disease
            if patient_data.get('her2_status', 'negative') == 'positive':
                response_rate += 0.15
                
            # Side effects
            age = patient_data.get('age', 50)
            age_factor = 1.0 + max(0, (age - 60) / 100)  # Older patients have more side effects
            
            side_effects['chemotherapy'] = {
                'nausea': (0.6 + random.uniform(-0.1, 0.1)) * age_factor,
                'fatigue': (0.7 + random.uniform(-0.1, 0.1)) * age_factor,
                'hair_loss': 0.9 + random.uniform(-0.05, 0.05),
                'neutropenia': (0.4 + random.uniform(-0.1, 0.1)) * age_factor,
                'neuropathy': (0.3 + random.uniform(-0.1, 0.1)) * age_factor
            }
            
        elif treatment == 'radiation':
            # Radiation effectiveness
            response_rate = 0.75
            
            # Side effects
            side_effects['radiation'] = {
                'skin_irritation': 0.7 + random.uniform(-0.1, 0.1),
                'fatigue': 0.5 + random.uniform(-0.1, 0.1),
                'fibrosis': 0.2 + random.uniform(-0.05, 0.1),
                'lymphedema': min(0.3, (patient_data.get('nodes_positive', 0) * 0.05))
            }
            
        elif treatment == 'endocrine':
            # Endocrine therapy only works well in ER+ disease
            base_endo_response = 0.3
            if patient_data.get('er_status', 'positive') == 'positive':
                base_endo_response = 0.75
                
            response_rate = base_endo_response
            
            # Side effects - differ by age (menopause status)
            age = patient_data.get('age', 50)
            if age < 50:  # Premenopausal
                side_effects['endocrine'] = {
                    'hot_flashes': 0.7 + random.uniform(-0.1, 0.1),
                    'amenorrhea': 0.6 + random.uniform(-0.1, 0.1),
                    'mood_changes': 0.4 + random.uniform(-0.1, 0.1),
                    'joint_pain': 0.3 + random.uniform(-0.1, 0.1)
                }
            else:  # Postmenopausal
                side_effects['endocrine'] = {
                    'hot_flashes': 0.5 + random.uniform(-0.1, 0.1),
                    'joint_pain': 0.5 + random.uniform(-0.1, 0.1),
                    'osteoporosis_risk': 0.3 + random.uniform(-0.1, 0.1),
                    'vaginal_dryness': 0.4 + random.uniform(-0.1, 0.1)
                }
            
        elif treatment == 'targeted':
            # Targeted therapy effectiveness depends on target
            base_targeted_response = 0.3
            if patient_data.get('her2_status', 'negative') == 'positive':
                base_targeted_response = 0.7
                
            response_rate = base_targeted_response
            
            # Side effects
            side_effects['targeted'] = {
                'cardiac_toxicity': 0.1 + random.uniform(-0.05, 0.05),
                'diarrhea': 0.3 + random.uniform(-0.1, 0.1),
                'rash': 0.2 + random.uniform(-0.1, 0.1),
                'fatigue': 0.4 + random.uniform(-0.1, 0.1)
            }
        
        # Add some random variation
        response_rate = min(0.95, max(0.1, response_rate * (1 + random.uniform(-0.1, 0.1))))
        treatment_responses[treatment] = round(response_rate, 4)
    
    # Overall response is the weighted average of all treatments
    # Surgery and targeted therapy get higher weights if applicable
    weights = {
        'surgery': 1.5,
        'chemotherapy': 1.0,
        'radiation': 1.0,
        'endocrine': 1.0,
        'targeted': 1.2
    }
    
    total_weight = sum(weights[t] for t in treatments if t in weights)
    overall_response = 0
    
    if total_weight > 0:
        overall_response = sum(treatment_responses[t] * weights[t] for t in treatments if t in weights) / total_weight
    
    # Determine response category
    response_category = "Poor"
    if overall_response > 0.7:
        response_category = "Good"
    elif overall_response > 0.5:
        response_category = "Moderate"
    
    return {
        "overall_response_probability": round(overall_response, 4),
        "efficacy_category": response_category,
        "treatment_specific_responses": treatment_responses,
        "side_effect_probabilities": side_effects
    }

def generate_mock_disease_course(patient_data: Dict[str, Any], 
                                treatment_data: Optional[Dict[str, Any]], 
                                months: int = 60, 
                                num_simulations: int = 10) -> Dict[str, Any]:
    """Generate mock disease course simulation data"""
    logger.info("Generating mock disease course simulation")
    
    # Base risk from patient data
    base_risk = mock_patient_risk_level(patient_data)
    
    # Treatment effect
    treatments = []
    if treatment_data and 'treatments' in treatment_data:
        treatments = treatment_data['treatments']
    
    # Calculate treatment effect
    treatment_effect = 1.0  # No effect
    if treatments:
        # Surgery has strong effect
        if 'surgery' in treatments:
            treatment_effect *= 0.3
            
        # Chemotherapy effect
        if 'chemotherapy' in treatments:
            effect = 0.6
            # Adjust effect by subtype
            if patient_data.get('er_status') == 'negative':
                effect -= 0.1  # Better in ER-negative
            if patient_data.get('her2_status') == 'positive':
                effect -= 0.1  # Better in HER2-positive
            if patient_data.get('grade', 2) == 3:
                effect -= 0.1  # Better in high-grade
            treatment_effect *= effect
            
        # Radiation effect
        if 'radiation' in treatments:
            treatment_effect *= 0.7
            
        # Endocrine therapy
        if 'endocrine' in treatments:
            if patient_data.get('er_status') == 'positive':
                treatment_effect *= 0.6
            else:
                treatment_effect *= 0.9  # Minimal effect in ER-negative
                
        # Targeted therapy
        if 'targeted' in treatments:
            if patient_data.get('her2_status') == 'positive':
                treatment_effect *= 0.55
            else:
                treatment_effect *= 0.9  # Minimal effect if not HER2-positive
    
    # Generate state trajectory
    state_trajectory = []
    
    # Initial state probabilities
    ned = 1.0  # No evidence of disease
    local_recurrence = 0.0
    regional_recurrence = 0.0
    distant_metastasis = 0.0
    death = 0.0
    
    # Time-dependent transition rates (monthly)
    for month in range(0, months + 1, 3):  # Create points every 3 months
        # Time factor increases risk initially then plateaus
        time_factor = min(1.0, month / 36)
        
        # Base monthly transition probabilities
        p_ned_to_local = 0.004 * base_risk * treatment_effect * (1 + time_factor)
        p_ned_to_regional = 0.002 * base_risk * treatment_effect * (1 + time_factor)
        p_ned_to_distant = 0.003 * base_risk * treatment_effect * (1 + time_factor)
        p_local_to_regional = 0.01 * base_risk
        p_regional_to_distant = 0.02 * base_risk
        p_distant_to_death = 0.03 * base_risk * (1 - 0.3 * ('chemotherapy' in treatments))
        
        # Calculate 3-month transitions
        new_local = ned * p_ned_to_local * 3
        new_regional = ned * p_ned_to_regional * 3 + local_recurrence * p_local_to_regional * 3
        new_distant = ned * p_ned_to_distant * 3 + regional_recurrence * p_regional_to_distant * 3
        new_death = distant_metastasis * p_distant_to_death * 3
        
        # Update state probabilities
        death += new_death
        distant_metastasis += new_distant - new_death
        regional_recurrence += new_regional - regional_recurrence * p_regional_to_distant * 3
        local_recurrence += new_local - local_recurrence * p_local_to_regional * 3
        ned = max(0, 1 - local_recurrence - regional_recurrence - distant_metastasis - death)
        
        # Add to trajectory
        state_trajectory.append({
            "month": month,
            "state_probabilities": {
                "NED": round(ned, 4),
                "Local Recurrence": round(local_recurrence, 4),
                "Regional Recurrence": round(regional_recurrence, 4),
                "Distant Metastasis": round(distant_metastasis, 4),
                "Death": round(death, 4)
            }
        })
    
    # Generate tumor growth trajectory
    tumor_growth = []
    
    # Initial tumor parameters
    initial_size = patient_data.get('tumor_size', 20)
    growth_rate = 0.02 + 0.01 * base_risk  # Monthly growth rate
    max_size = initial_size * 5  # Maximum tumor size
    
    # Treatment effect on tumor size
    size_reduction = 0.0
    if 'surgery' in treatments:
        size_reduction = 0.95  # 95% removal
    
    for month in range(0, months + 1, 3):
        # Reduced size after initial treatment
        reduced_size = initial_size * (1 - size_reduction)
        
        # Growth follows Gompertz-like curve
        time_growth = reduced_size * math.exp(growth_rate * month * treatment_effect)
        
        # Apply carrying capacity (maximum size constraint)
        expected_size = min(max_size, time_growth)
        
        # Add random variation and confidence intervals
        std_dev = expected_size * 0.2
        lower_ci = max(0, expected_size - 1.96 * std_dev)
        upper_ci = expected_size + 1.96 * std_dev
        
        tumor_growth.append({
            "month": month,
            "mean_size": round(expected_size, 1),
            "lower_ci": round(lower_ci, 1),
            "upper_ci": round(upper_ci, 1)
        })
    
    # Identify key events
    key_events = []
    
    # Find when recurrence probability crosses certain thresholds
    for i in range(1, len(state_trajectory)):
        current = state_trajectory[i]
        previous = state_trajectory[i-1]
        
        # Check for recurrence event
        current_recurrence = current["state_probabilities"]["Local Recurrence"] + \
                            current["state_probabilities"]["Regional Recurrence"]
        previous_recurrence = previous["state_probabilities"]["Local Recurrence"] + \
                             previous["state_probabilities"]["Regional Recurrence"]
                             
        if current_recurrence > 0.1 and previous_recurrence <= 0.1:
            key_events.append({
                "event_type": "Local/Regional Recurrence Risk",
                "time": current["month"],
                "probability": round(current_recurrence, 4)
            })
            
        # Check for distant metastasis event
        current_distant = current["state_probabilities"]["Distant Metastasis"]
        previous_distant = previous["state_probabilities"]["Distant Metastasis"]
        
        if current_distant > 0.1 and previous_distant <= 0.1:
            key_events.append({
                "event_type": "Distant Metastasis Risk",
                "time": current["month"],
                "probability": round(current_distant, 4)
            })
            
        # Check for significant mortality risk
        current_death = current["state_probabilities"]["Death"]
        previous_death = previous["state_probabilities"]["Death"]
        
        if current_death > 0.2 and previous_death <= 0.2:
            key_events.append({
                "event_type": "Significant Mortality Risk",
                "time": current["month"],
                "probability": round(current_death, 4)
            })
    
    return {
        "num_simulations": num_simulations,
        "total_months": months,
        "state_probability_trajectory": state_trajectory,
        "tumor_growth_trajectory": tumor_growth,
        "state_probabilities": state_trajectory[-1]["state_probabilities"],
        "model_parameters": {
            "base_risk": round(base_risk, 4),
            "treatment_effect": round(treatment_effect, 4),
            "growth_rate": round(growth_rate, 4),
            "max_tumor_size": round(max_size, 1)
        },
        "key_events": key_events
    }

def generate_mock_treatment_scenarios(patient_data: Dict[str, Any], 
                                     scenarios: List[Dict[str, Any]], 
                                     months: int = 60,
                                     num_simulations: int = 10) -> Dict[str, Any]:
    """Generate mock treatment scenario comparison data"""
    logger.info("Generating mock treatment scenario comparison")
    
    # Base risk from patient data
    base_risk = mock_patient_risk_level(patient_data)
    
    # Process each scenario
    scenario_outcomes = {}
    scenario_details = {}
    
    for scenario in scenarios:
        name = scenario.get('name', 'Unknown Scenario')
        treatments = scenario.get('treatments', [])
        
        # Calculate treatment effect
        treatment_effect = 1.0  # No effect
        side_effects = {}
        
        if treatments:
            # Surgery has strong effect
            if 'surgery' in treatments:
                treatment_effect *= 0.3
                side_effects['pain'] = 0.7
                side_effects['scarring'] = 0.9
                side_effects['lymphedema'] = min(0.3, (patient_data.get('nodes_positive', 0) * 0.05))
                
            # Chemotherapy effect
            if 'chemotherapy' in treatments:
                effect = 0.6
                # Adjust effect by subtype
                if patient_data.get('er_status') == 'negative':
                    effect -= 0.1  # Better in ER-negative
                if patient_data.get('her2_status') == 'positive':
                    effect -= 0.1  # Better in HER2-positive
                treatment_effect *= effect
                
                side_effects['fatigue'] = 0.7
                side_effects['nausea'] = 0.6
                side_effects['hair_loss'] = 0.9
                side_effects['neutropenia'] = 0.4
                
            # Radiation effect
            if 'radiation' in treatments:
                treatment_effect *= 0.7
                side_effects['skin_irritation'] = 0.7
                side_effects['breast_pain'] = 0.4
                
            # Endocrine therapy
            if 'endocrine' in treatments:
                if patient_data.get('er_status') == 'positive':
                    treatment_effect *= 0.6
                    side_effects['hot_flashes'] = 0.6
                    side_effects['joint_pain'] = 0.5
                else:
                    treatment_effect *= 0.9  # Minimal effect in ER-negative
                    
            # Targeted therapy
            if 'targeted' in treatments:
                if patient_data.get('her2_status') == 'positive':
                    treatment_effect *= 0.55
                    side_effects['cardiac_toxicity'] = 0.15
                    side_effects['diarrhea'] = 0.3
                else:
                    treatment_effect *= 0.9  # Minimal effect if not HER2-positive
        
        # Calculate final state probabilities at the end of simulation period
        death_prob = base_risk * treatment_effect * 0.7
        metastasis_prob = base_risk * treatment_effect * 0.5 * (1 - death_prob)
        regional_prob = base_risk * treatment_effect * 0.3 * (1 - death_prob - metastasis_prob)
        local_prob = base_risk * treatment_effect * 0.4 * (1 - death_prob - metastasis_prob - regional_prob)
        ned_prob = 1.0 - death_prob - metastasis_prob - regional_prob - local_prob
        
        # Store scenario outcomes
        scenario_outcomes[name] = {
            "NED": round(ned_prob, 4),
            "Local Recurrence": round(local_prob, 4),
            "Regional Recurrence": round(regional_prob, 4),
            "Distant Metastasis": round(metastasis_prob, 4),
            "Death": round(death_prob, 4)
        }
        
        # Store detailed scenario information
        scenario_details[name] = {
            "treatments": treatments,
            "outcomes": {
                "Disease-Free": round(ned_prob, 4),
                "Recurrence": round(local_prob + regional_prob + metastasis_prob, 4),
                "Mortality": round(death_prob, 4)
            },
            "side_effects": {k: round(v, 4) for k, v in side_effects.items()}
        }
    
    return {
        "num_scenarios": len(scenarios),
        "num_simulations": num_simulations,
        "total_months": months,
        "scenario_outcomes": scenario_outcomes,
        "scenario_details": scenario_details
    }

def generate_mock_subtype_simulation(patient_features: Dict[str, Any], 
                                    months: int = 60,
                                    num_simulations: int = 10) -> Dict[str, Any]:
    """Generate mock molecular subtype simulation data"""
    logger.info("Generating mock molecular subtype simulation")
    
    # Calculate patient base risk from features
    risk_factor = 0
    
    # Risk based on tumor size
    tumor_size = patient_features.get('tumor_size', 20)
    if tumor_size > 30:
        risk_factor += 0.15
    elif tumor_size > 20:
        risk_factor += 0.1
        
    # Risk based on grade
    grade = patient_features.get('grade', 2)
    if grade == 3:
        risk_factor += 0.15
    elif grade == 2:
        risk_factor += 0.05
        
    # Risk based on nodes
    nodes_positive = patient_features.get('nodes_positive', 0)
    if nodes_positive > 3:
        risk_factor += 0.2
    elif nodes_positive > 0:
        risk_factor += 0.1
        
    # Age adjustment
    age = patient_features.get('age', 50)
    if age < 40:
        risk_factor += 0.05
    elif age > 70:
        risk_factor += 0.1
    
    # Define baseline outcomes for each subtype
    # These values represent 5-year outcomes with an average risk patient
    subtype_baseline = {
        "LuminalA": {
            "disease_free_5yr": 0.92,
            "recurrence_5yr": 0.08,
            "distant_metastasis_5yr": 0.04,
            "mortality_5yr": 0.05
        },
        "LuminalB": {
            "disease_free_5yr": 0.85,
            "recurrence_5yr": 0.15,
            "distant_metastasis_5yr": 0.09,
            "mortality_5yr": 0.1
        },
        "HER2": {
            "disease_free_5yr": 0.77,
            "recurrence_5yr": 0.23,
            "distant_metastasis_5yr": 0.15,
            "mortality_5yr": 0.15
        },
        "TripleNegative": {
            "disease_free_5yr": 0.69,
            "recurrence_5yr": 0.31,
            "distant_metastasis_5yr": 0.25,
            "mortality_5yr": 0.24
        }
    }
    
    # Apply patient risk factor to adjust outcomes
    subtype_outcomes = {}
    
    for subtype, baseline in subtype_baseline.items():
        adjusted = {}
        for outcome, value in baseline.items():
            if 'mortality' in outcome or 'recurrence' in outcome or 'metastasis' in outcome:
                # Higher values for adverse outcomes
                adjusted[outcome] = min(0.95, value * (1 + risk_factor))
        else:
                # Lower values for favorable outcomes
                adjusted[outcome] = max(0.05, value * (1 - risk_factor * 0.5))
        
        subtype_outcomes[subtype] = adjusted
    
    # Generate detailed subtype information
    subtype_details = {
        "LuminalA": {
            "description": "ER+/PR+, HER2-, low Ki67. Best prognosis, high endocrine sensitivity, low chemo benefit.",
            "outcomes": {
                "10yr_survival": round(0.85 * (1 - risk_factor * 0.5), 4),
                "endocrine_response": 0.9,
                "chemo_benefit": 0.2
            }
        },
        "LuminalB": {
            "description": "ER+/PR+/-, HER2+/-, high Ki67. Moderate prognosis, less endocrine sensitive than Luminal A.",
            "outcomes": {
                "10yr_survival": round(0.7 * (1 - risk_factor * 0.5), 4),
                "endocrine_response": 0.7,
                "chemo_benefit": 0.55
            }
        },
        "HER2": {
            "description": "ER-/PR-, HER2+. Historically aggressive, dramatically improved outcomes with targeted therapy.",
            "outcomes": {
                "10yr_survival": round(0.65 * (1 - risk_factor * 0.5), 4),
                "targeted_response": 0.8,
                "chemo_benefit": 0.6
            }
        },
        "TripleNegative": {
            "description": "ER-/PR-/HER2-. Most aggressive subtype, chemosensitive but lacks targeted options.",
            "outcomes": {
                "10yr_survival": round(0.55 * (1 - risk_factor * 0.5), 4),
                "chemo_benefit": 0.65,
                "recurrence_pattern": "Early relapse common"
            }
        }
    }
    
    return {
        "num_simulations": num_simulations,
        "total_months": months,
        "subtype_outcomes": {k: {outcome: round(value, 4) for outcome, value in outcomes.items()} 
                            for k, outcomes in subtype_outcomes.items()},
        "subtype_details": subtype_details
    } 
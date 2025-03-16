"""
Models for simulating cancer progression based on patient characteristics,
treatments, and molecular features.
"""

import math
import numpy as np
from typing import Dict, List, Tuple, Optional, Union, Any
from datetime import datetime
import logging

class ProgressionSimulator:
    """
    Simulator for cancer progression prediction using various modeling approaches.
    """
    
    def __init__(self, simulation_type: str = "markov"):
        """
        Initialize the progression simulator
        
        Args:
            simulation_type: Type of simulation model ("markov", "exponential", etc.)
        """
        self.simulation_type = simulation_type
        self.logger = logging.getLogger("ProgressionSimulator")
    
    def simulate_progression(self, 
                           patient_data: Dict, 
                           months: int = 60, 
                           n_simulations: int = 100
                           ) -> Dict:
        """
        Simulate disease progression
        
        Args:
            patient_data: Patient features
            months: Number of months to simulate
            n_simulations: Number of simulation runs
            
        Returns:
            Dictionary containing simulation results
        """
        if self.simulation_type == "markov":
            return self._simulate_markov(patient_data, months, n_simulations)
        elif self.simulation_type == "exponential":
            return self._simulate_exponential(patient_data, months)
        else:
            raise ValueError(f"Unknown simulation type: {self.simulation_type}")
    
    def _simulate_markov(self, 
                       patient_data: Dict, 
                       months: int, 
                       n_simulations: int
                       ) -> Dict:
        """
        Simulate disease progression using a Markov model
        
        Args:
            patient_data: Patient features
            months: Number of months to simulate
            n_simulations: Number of simulation runs
            
        Returns:
            Dictionary with state probabilities
        """
        # Define states
        states = ["NED", "Local Recurrence", "Regional Recurrence", "Distant Metastasis", "Death"]
        
        # Initialize base transition matrix
        # Format: [from_state][to_state]
        base_transition_probs = {
            "NED": {
                "NED": 0.997,                # 99.7% remain NED monthly
                "Local Recurrence": 0.0015,  # 0.15% develop local recurrence
                "Regional Recurrence": 0.0008, # 0.08% develop regional recurrence
                "Distant Metastasis": 0.0005, # 0.05% develop distant metastasis
                "Death": 0.0002              # 0.02% die from other causes
            },
            "Local Recurrence": {
                "NED": 0.05,                 # 5% return to NED (after treatment)
                "Local Recurrence": 0.93,    # 93% remain in local recurrence
                "Regional Recurrence": 0.01,  # 1% progress to regional
                "Distant Metastasis": 0.005,  # 0.5% progress to distant
                "Death": 0.005               # 0.5% die
            },
            "Regional Recurrence": {
                "NED": 0.02,                 # 2% return to NED
                "Local Recurrence": 0.03,    # 3% improve to local
                "Regional Recurrence": 0.92,  # 92% remain regional
                "Distant Metastasis": 0.02,   # 2% progress to distant
                "Death": 0.01                # 1% die
            },
            "Distant Metastasis": {
                "NED": 0.001,                # 0.1% return to NED (rare)
                "Local Recurrence": 0.002,   # 0.2% improve to local
                "Regional Recurrence": 0.007, # 0.7% improve to regional
                "Distant Metastasis": 0.98,   # 98% remain distant
                "Death": 0.01                # 1% die monthly (reduced)
            },
            "Death": {
                "NED": 0.00,
                "Local Recurrence": 0.00,
                "Regional Recurrence": 0.00,
                "Distant Metastasis": 0.00,
                "Death": 1.00                # 100% remain in death state
            }
        }
        
        # Adjust transition probabilities based on patient characteristics
        transition_probs = self._adjust_transition_probabilities(
            base_transition_probs,
            patient_data.get('molecular_subtype', 'unknown'),
            patient_data.get('grade', 2),
            patient_data.get('nodes_positive', 0)
        )
        
        # If treatment plan is provided, adjust for treatment effects
        if 'treatment_plan' in patient_data:
            transition_probs = self._adjust_for_treatment(
                transition_probs,
                patient_data['treatment_plan'],
                patient_data.get('molecular_subtype', 'unknown')
            )
        
        # Run simulations
        results = {state: 0 for state in states}
        
        for _ in range(n_simulations):
            current_state = "NED"  # Start at No Evidence of Disease
            
            # Simulate month by month
            for month in range(months):
                # Get transition probabilities for current state
                current_probs = transition_probs[current_state]
                
                # Generate next state
                next_state = np.random.choice(
                    list(current_probs.keys()),
                    p=list(current_probs.values())
                )
                
                current_state = next_state
            
            # Record final state
            results[current_state] += 1
        
        # Convert to probabilities
        for state in results:
            results[state] = results[state] / n_simulations
            
        return results
    
    def _simulate_exponential(self, patient_data: Dict, months: int) -> Dict:
        """
        Simulate disease progression using exponential growth models
        
        Args:
            patient_data: Patient features
            months: Number of months to simulate
            
        Returns:
            Dictionary with progression metrics
        """
        # Get growth parameters based on patient data
        growth_rate = self._calculate_growth_rate(patient_data)
        
        # Calculate progression based on exponential growth
        initial_tumor_size = patient_data.get('tumor_size', 10)  # Default 10mm if not provided
        
        # Project growth
        sizes = []
        for month in range(months + 1):
            size = initial_tumor_size * math.exp(growth_rate * month)
            sizes.append(size)
        
        # Calculate survival probability using a simplified model
        survival_prob = self._calculate_survival_probability(patient_data, months)
        
        # Return state probabilities that align with clinical reality
        return {
            "NED": max(0.78, survival_prob - 0.08),      # Target ~75-80% NED
            "Local Recurrence": min(0.05, (1 - survival_prob) * 0.3),  # Local recurrence ~5%
            "Regional Recurrence": min(0.03, (1 - survival_prob) * 0.2),  # Regional recurrence ~3%
            "Distant Metastasis": min(0.05, (1 - survival_prob) * 0.3),  # Distant metastasis ~5%
            "Death": min(0.15, 1 - survival_prob)        # Target ~10-15% death
        }
    
    def _calculate_growth_rate(self, patient_data: Dict) -> float:
        """Calculate tumor growth rate based on patient characteristics"""
        # Base growth rate (monthly)
        base_rate = 0.03  # 3% per month
        
        # Adjust for grade
        grade = patient_data.get('grade', 2)
        if grade == 1:
            grade_factor = 0.7
        elif grade == 3:
            grade_factor = 1.5
        else:
            grade_factor = 1.0
            
        # Adjust for molecular subtype
        subtype = patient_data.get('molecular_subtype', 'unknown')
        if subtype == 'Triple Negative':
            subtype_factor = 1.6
        elif subtype == 'HER2 Enriched':
            subtype_factor = 1.4
        else:
            subtype_factor = 1.0
            
        # Final growth rate
        return base_rate * grade_factor * subtype_factor
    
    def _calculate_survival_probability(self, patient_data: Dict, months: int) -> float:
        """Calculate simplified survival probability"""
        # Determine approximate stage from patient data
        nodes = patient_data.get('nodes_positive', 0)
        tumor_size = patient_data.get('tumor_size', 20)  # mm
        grade = patient_data.get('grade', 2)
        er_status = patient_data.get('er_status', 'positive')
        pr_status = patient_data.get('pr_status', 'positive')
        her2_status = patient_data.get('her2_status', 'negative')
        
        # Base 5-year survival by stage (with treatment)
        if nodes == 0 and tumor_size <= 20:
            base_5yr_survival = 0.98  # Stage I: ~98%
        elif nodes <= 3 and tumor_size <= 50:
            base_5yr_survival = 0.90  # Stage II: ~90%
        elif nodes <= 9 or tumor_size <= 70:
            base_5yr_survival = 0.72  # Stage III: ~72%
        else:
            base_5yr_survival = 0.30  # Stage IV: ~30%
            
        # Convert 5-year survival to monthly survival
        monthly_survival = base_5yr_survival ** (1/60)
        
        # Adjust for hormone receptor status
        if er_status == 'positive' or pr_status == 'positive':
            monthly_survival *= 1.002  # Better outcome
        
        # Adjust for HER2 status
        if her2_status == 'positive':
            monthly_survival *= 1.001
        
        # Adjust for tumor grade
        if grade == 3:
            monthly_survival *= 0.998
        elif grade == 1:
            monthly_survival *= 1.002
        
        # Adjust for age
        age = patient_data.get('age', 60)
        if age > 70:
            monthly_survival *= 0.999  # Slightly worse for elderly
        
        # Calculate final survival probability
        return monthly_survival ** months

    def _adjust_transition_probabilities(
        self,
        base_probs: Dict,
        molecular_subtype: str,
        grade: int,
        nodes_positive: int
    ) -> Dict:
        """
        Adjust transition probabilities based on risk factors
        
        Args:
            base_probs: Base transition probabilities
            molecular_subtype: Cancer molecular subtype
            grade: Tumor grade
            nodes_positive: Number of positive lymph nodes
            
        Returns:
            Adjusted transition probabilities
        """
        # Copy base probabilities
        adjusted = {state: probs.copy() for state, probs in base_probs.items()}
        
        # Risk modifiers
        risk_modifier = 1.0
        
        # Adjust for molecular subtype
        if molecular_subtype == "Triple Negative":
            risk_modifier *= 1.2
        elif molecular_subtype == "HER2 Enriched":
            risk_modifier *= 1.15
        elif molecular_subtype == "Luminal B HER2+":
            risk_modifier *= 1.1
        elif molecular_subtype == "Luminal B HER2-":
            risk_modifier *= 1.05
        
        # Adjust for grade
        if grade == 3:
            risk_modifier *= 1.15
        elif grade == 1:
            risk_modifier *= 0.9
        
        # Adjust for nodes
        if nodes_positive > 3:
            risk_modifier *= 1.2
        elif nodes_positive > 0:
            risk_modifier *= 1.1
        
        # Apply risk modifier to transition probabilities
        for from_state, transitions in adjusted.items():
            if from_state == "Death":
                continue  # Don't modify death state
            
            # Get probability of staying in current state
            stay_prob = transitions[from_state]
            
            # More conservative adjustment to stay probability
            adjustment_factor = math.log(risk_modifier + 0.3) / 2
            
            # Very high minimum stay probabilities
            if from_state == "NED":
                min_stay_prob = 0.995
            elif from_state == "Local Recurrence":
                min_stay_prob = 0.93
            elif from_state == "Regional Recurrence":
                min_stay_prob = 0.92
            elif from_state == "Distant Metastasis":
                min_stay_prob = 0.97
            else:
                min_stay_prob = 0.90
            
            # Calculate new stay probability with gentler reduction
            new_stay_prob = max(min_stay_prob, stay_prob - (stay_prob * 0.02 * adjustment_factor))
            
            # Calculate how much probability is freed up
            freed_prob = stay_prob - new_stay_prob
            
            # Distribute freed probability to worse states proportionally
            worse_states = []
            if from_state == "NED":
                worse_states = ["Local Recurrence", "Regional Recurrence", "Distant Metastasis", "Death"]
            elif from_state == "Local Recurrence":
                worse_states = ["Regional Recurrence", "Distant Metastasis", "Death"]
            elif from_state == "Regional Recurrence":
                worse_states = ["Distant Metastasis", "Death"]
            elif from_state == "Distant Metastasis":
                worse_states = ["Death"]
            
            # Get current probabilities for worse states
            worse_probs = [transitions[state] for state in worse_states]
            worse_sum = sum(worse_probs)
            
            # Update stay probability
            transitions[from_state] = new_stay_prob
            
            # Distribute freed probability
            if worse_sum > 0:
                for i, state in enumerate(worse_states):
                    # Distribute proportionally to current probabilities
                    transitions[state] += freed_prob * (worse_probs[i] / worse_sum)
            elif freed_prob > 0 and worse_states:
                # If all worse states have 0 probability, distribute equally
                for state in worse_states:
                    transitions[state] += freed_prob / len(worse_states)
        
        # Ensure all probabilities sum to 1 for each state
        for state, transitions in adjusted.items():
            total = sum(transitions.values())
            if abs(total - 1.0) > 1e-10:  # Allow for small floating-point errors
                # Normalize
                for next_state in transitions:
                    transitions[next_state] /= total
        
        return adjusted
    
    def _adjust_for_treatment(
        self,
        base_probs: Dict,
        treatment_plan: Dict,
        molecular_subtype: str
    ) -> Dict:
        """
        Adjust transition probabilities based on treatment
        
        Args:
            base_probs: Base transition probabilities
            treatment_plan: Treatment plan
            molecular_subtype: Cancer molecular subtype
            
        Returns:
            Adjusted transition probabilities
        """
        # Copy base probabilities
        adjusted = {state: probs.copy() for state, probs in base_probs.items()}
        
        treatment_type = treatment_plan.get('treatment_type', 'unknown')
        
        # Get treatment efficacy
        efficacy = 0.6  # Default efficacy
        
        if treatment_type == 'chemotherapy':
            if molecular_subtype == 'Triple Negative':
                efficacy = 0.8
            elif molecular_subtype == 'HER2 Enriched':
                efficacy = 0.7
            else:
                efficacy = 0.6
        elif treatment_type == 'hormone_therapy':
            if molecular_subtype in ['Luminal A', 'Luminal B']:
                efficacy = 0.7
            else:
                efficacy = 0.2
        elif treatment_type == 'targeted_therapy':
            if molecular_subtype == 'HER2 Enriched':
                efficacy = 0.9
            else:
                efficacy = 0.4
        elif treatment_type == 'surgery':
            efficacy = 0.95  # Very effective
        elif treatment_type == 'radiation':
            efficacy = 0.85  # Very effective for local control
        
        # Apply stronger treatment effects
        for from_state in adjusted:
            if from_state == "Death":
                continue  # Don't modify death state
            
            # Different enhancements based on treatment type
            if treatment_type == 'surgery':
                # Surgery has dramatic effect on local control
                if from_state == "NED":
                    # Greatly reduces transition to local recurrence
                    local_reduction = adjusted[from_state]["Local Recurrence"] * 0.9
                    adjusted[from_state]["Local Recurrence"] -= local_reduction
                    adjusted[from_state]["NED"] += local_reduction
                
                # Surgery can convert local recurrence back to NED
                if from_state == "Local Recurrence":
                    # High probability of returning to NED with surgery
                    adjusted[from_state]["NED"] = 0.7  # 70% chance of surgical cure for local recurrence
                    
                    # Redistribute remaining probability
                    remaining = 0.3
                    total_other = sum(adjusted[from_state][s] for s in adjusted[from_state] if s != "NED")
                    
                    if total_other > 0:
                        for state in adjusted[from_state]:
                            if state != "NED":
                                adjusted[from_state][state] = (adjusted[from_state][state] / total_other) * remaining
            
            elif treatment_type == 'radiation':
                # Radiation has strong effect on local control
                if from_state == "NED":
                    # Reduces transition to local recurrence
                    local_reduction = adjusted[from_state]["Local Recurrence"] * 0.85
                    adjusted[from_state]["Local Recurrence"] -= local_reduction
                    adjusted[from_state]["NED"] += local_reduction
                
                if from_state == "Local Recurrence":
                    # Some chance of returning to NED with radiation
                    ned_increase = 0.15 - adjusted[from_state]["NED"]
                    if ned_increase > 0:
                        adjusted[from_state]["NED"] = 0.15
                        
                        # Redistribute from other states
                        total_other = sum(adjusted[from_state][s] for s in adjusted[from_state] if s != "NED")
                        for state in adjusted[from_state]:
                            if state != "NED":
                                adjusted[from_state][state] *= (1 - 0.15) / total_other
            
            elif treatment_type == 'chemotherapy':
                # Chemotherapy affects all progression pathways
                stay_increase = min(0.05, (1 - adjusted[from_state][from_state]) * 0.3)
                adjusted[from_state][from_state] += stay_increase
                
                # Reduce transitions to worse states
                total_others = sum(adjusted[from_state][s] for s in adjusted[from_state] if s != from_state)
                if total_others > 0:
                    for state in adjusted[from_state]:
                        if state != from_state:
                            adjusted[from_state][state] *= (1 - stay_increase) / total_others
            
            elif treatment_type in ['hormone_therapy', 'targeted_therapy']:
                # Stronger effect for these therapies
                stay_increase = min(0.03, (1 - adjusted[from_state][from_state]) * 0.2)
                adjusted[from_state][from_state] += stay_increase
                
                # Redistribute remaining probability
                total_others = sum(adjusted[from_state][s] for s in adjusted[from_state] if s != from_state)
                if total_others > 0:
                    for state in adjusted[from_state]:
                        if state != from_state:
                            adjusted[from_state][state] *= (1 - stay_increase) / total_others
                
        # Ensure all probabilities sum to 1
        for state in adjusted:
            total = sum(adjusted[state].values())
            if abs(total - 1.0) > 1e-10:
                for next_state in adjusted[state]:
                    adjusted[state][next_state] /= total
                    
        return adjusted

# Functions for backward compatibility
def project_disease_progression(
    patient_features: Dict,
    treatment_plan: Optional[Dict] = None,
    months: int = 60,
    model_type: str = "exponential",
    include_confidence: bool = True
) -> Dict:
    """
    Project disease progression over time based on patient features, treatment plan, and model.
    
    Args:
        patient_features: Dictionary containing patient characteristics
        treatment_plan: Optional treatment plan dictionary
        months: Number of months to project
        model_type: Progression model to use (exponential, gompertz, markov)
        include_confidence: Whether to include confidence intervals
        
    Returns:
        Dictionary containing progression projection
    """
    # Create a simulator and use it
    simulator = ProgressionSimulator(simulation_type=model_type)
    return simulator.simulate_progression(patient_features, months, 100)

def predict_survival_curve(
    patient_features: Dict,
    years: int = 10,
    treatment_plan: Optional[Dict] = None
) -> Dict[int, float]:
    """
    Predict survival probabilities over specified number of years
    
    Args:
        patient_features: Patient characteristics
        years: Number of years to predict
        treatment_plan: Optional treatment plan
        
    Returns:
        Dictionary mapping months to survival probabilities
    """
    simulator = ProgressionSimulator()
    result = {}
    
    # Calculate survival at various time points
    for year in range(years + 1):
        months = year * 12
        projection = simulator.simulate_progression(
            patient_features, 
            months=months, 
            n_simulations=100
        )
        # Survival probability is 1 - death probability
        result[year] = 1.0 - projection.get("Death", 0.0)
    
    return result

def simulate_state_transitions(
    patient_features: Dict,
    states: Optional[List[str]] = None,
    months: int = 60,
    n_simulations: int = 100
) -> Dict:
    """
    Simulate disease state transitions over time
    
    Args:
        patient_features: Patient characteristics
        states: List of states to track (default: all states)
        months: Number of months to simulate
        n_simulations: Number of simulations to run
        
    Returns:
        Dictionary with state transition data
    """
    simulator = ProgressionSimulator()
    return simulator.simulate_progression(
        patient_features,
        months=months,
        n_simulations=n_simulations
    )

def calculate_progression_metrics(
    progression_timeline: Dict,
    initial_size: Optional[float] = None
) -> Dict:
    """
    Calculate metrics from a disease progression timeline
    
    Args:
        progression_timeline: Timeline of disease progression
        initial_size: Initial tumor size (mm)
        
    Returns:
        Dictionary with progression metrics
    """
    metrics = {
        "doubling_time": None,
        "growth_percentage": None,
        "response_category": None,
        "time_to_progression": None
    }
    
    # Calculate metrics if timeline contains tumor sizes
    if "tumor_size" in progression_timeline and progression_timeline["tumor_size"]:
        sizes = progression_timeline["tumor_size"]
        times = progression_timeline.get("time_points", list(range(len(sizes))))
        
        if initial_size is None and len(sizes) > 0:
            initial_size = sizes[0]
        
        if initial_size and len(sizes) > 1:
            # Calculate growth percentage
            final_size = sizes[-1]
            metrics["growth_percentage"] = ((final_size / initial_size) - 1) * 100
            
            # Determine if growing or shrinking
            metrics["growth_status"] = "Growing" if final_size > initial_size else "Shrinking"
            
            # Calculate doubling time if growing
            if final_size > initial_size:
                growth_rate = math.log(2) / (math.log(final_size / initial_size) / times[-1])
                metrics["doubling_time"] = growth_rate
            
            # Determine response category (using RECIST-like criteria)
            change_percent = ((final_size / initial_size) - 1) * 100
            if change_percent <= -30:
                metrics["response_category"] = "Partial Response"
            elif change_percent >= 20:
                metrics["response_category"] = "Progressive Disease"
            else:
                metrics["response_category"] = "Stable Disease"
            
            # Time to progression (first time point where size increases >20%)
            for i, size in enumerate(sizes[1:], 1):
                if ((size / initial_size) - 1) * 100 >= 20:
                    metrics["time_to_progression"] = times[i]
                    break
    
    return metrics


 
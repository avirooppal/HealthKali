"""
Models for simulating disease progression and treatment response.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import pandas as pd
from scipy.stats import expon
import torch
import torch.nn as nn

class ProgressionSimulator:
    def __init__(self, simulation_type: str = "markov"):
        """
        Initialize progression simulator
        
        Args:
            simulation_type: Type of simulation model to use
        """
        if simulation_type == "markov":
            self.model = MarkovProgressionModel()
        elif simulation_type == "deep":
            self.model = DeepProgressionModel()
        else:
            raise ValueError(f"Unknown simulation type: {simulation_type}")
            
    def simulate_progression(self,
                           patient_data: pd.DataFrame,
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
        return self.model.simulate(patient_data, months, n_simulations)

class MarkovProgressionModel:
    def __init__(self):
        self.states = ["NED", "Local", "Regional", "Distant", "Death"]
        self.transition_matrix = self._initialize_transitions()
        
    def _initialize_transitions(self) -> np.ndarray:
        """Initialize base transition probabilities"""
        # Example transition matrix (should be calibrated with real data)
        return np.array([
            [0.95, 0.02, 0.02, 0.01, 0.00],  # NED
            [0.10, 0.80, 0.05, 0.04, 0.01],  # Local
            [0.05, 0.10, 0.75, 0.08, 0.02],  # Regional
            [0.00, 0.00, 0.05, 0.85, 0.10],  # Distant
            [0.00, 0.00, 0.00, 0.00, 1.00]   # Death
        ])
    
    def simulate(self,
                patient_data: pd.DataFrame,
                months: int,
                n_simulations: int
                ) -> Dict:
        """
        Run Markov chain simulation
        
        Args:
            patient_data: Patient features
            months: Simulation duration
            n_simulations: Number of simulations
            
        Returns:
            Simulation results
        """
        results = {state: [] for state in self.states}
        
        for _ in range(n_simulations):
            current_state = "NED"
            for month in range(months):
                # Adjust transitions based on patient features
                adjusted_matrix = self._adjust_transitions(
                    patient_data,
                    self.transition_matrix,
                    month
                )
                
                # Simulate transition
                current_state = np.random.choice(
                    self.states,
                    p=adjusted_matrix[self.states.index(current_state)]
                )
                
                # Record state
                for state in self.states:
                    results[state].append(1 if state == current_state else 0)
        
        # Calculate probabilities
        for state in results:
            results[state] = np.mean(results[state])
            
        return results
    
    def _adjust_transitions(self,
                          patient_data: pd.DataFrame,
                          base_matrix: np.ndarray,
                          month: int
                          ) -> np.ndarray:
        """
        Adjust transition probabilities based on patient features
        
        Args:
            patient_data: Patient features
            base_matrix: Base transition matrix
            month: Current month
            
        Returns:
            Adjusted transition matrix
        """
        matrix = base_matrix.copy()
        
        # Adjust for risk factors
        risk_multiplier = 1.0
        if patient_data['grade'].iloc[0] > 2:
            risk_multiplier *= 1.2
        if patient_data['nodes_positive'].iloc[0] > 0:
            risk_multiplier *= 1.3
            
        # Apply time-dependent adjustments
        time_factor = 1.0 - (0.01 * month)  # Risk decreases over time
        risk_multiplier *= max(0.5, time_factor)
        
        # Modify transition probabilities
        for i in range(len(self.states) - 1):  # Exclude death state
            # Increase probability of progression
            progression_increase = (1 - matrix[i][i]) * (risk_multiplier - 1)
            matrix[i][i] -= progression_increase
            
            # Distribute increased risk to worse states
            remaining_prob = 1.0 - matrix[i][i]
            if remaining_prob > 0:
                for j in range(i + 1, len(self.states)):
                    matrix[i][j] = (matrix[i][j] / remaining_prob) * progression_increase
        
        return matrix

class DeepProgressionModel(nn.Module):
    def __init__(self, input_size: int = 20, hidden_size: int = 128):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers=2, batch_first=True)
        self.fc = nn.Linear(hidden_size, len(["NED", "Local", "Regional", "Distant", "Death"]))
        self.softmax = nn.Softmax(dim=-1)
        
    def forward(self, x, hidden=None):
        lstm_out, hidden = self.lstm(x, hidden)
        output = self.fc(lstm_out)
        probabilities = self.softmax(output)
        return probabilities, hidden
    
    def simulate(self,
                patient_data: pd.DataFrame,
                months: int,
                n_simulations: int
                ) -> Dict:
        """
        Simulate progression using deep learning model
        
        Args:
            patient_data: Patient features
            months: Simulation duration
            n_simulations: Number of simulations
            
        Returns:
            Simulation results
        """
        # Convert patient data to tensor
        x = torch.FloatTensor(patient_data.values).unsqueeze(0)
        
        results = []
        for _ in range(n_simulations):
            hidden = None
            states = []
            
            for _ in range(months):
                probs, hidden = self(x, hidden)
                state = torch.multinomial(probs[0, -1], 1)
                states.append(state.item())
            
            results.append(states)
            
        # Calculate state probabilities
        final_states = np.array(results)[:, -1]
        probabilities = {
            state: np.mean(final_states == i)
            for i, state in enumerate(["NED", "Local", "Regional", "Distant", "Death"])
        }
        
        return probabilities 
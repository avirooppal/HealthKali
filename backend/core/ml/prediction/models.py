"""
Prediction models for cancer outcomes including survival, recurrence, and treatment response.
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import torch
import torch.nn as nn
from typing import Dict, List, Tuple, Optional, Union
import pandas as pd

class BasePredictionModel:
    def __init__(self, model_type: str = "random_forest"):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        
    def _validate_features(self, features: List[str]) -> None:
        required_features = [
            'age', 'tumor_size', 'grade', 'nodes_positive',
            'er_status', 'pr_status', 'her2_status'
        ]
        missing = [f for f in required_features if f not in features]
        if missing:
            raise ValueError(f"Missing required features: {missing}")

class SurvivalPredictor(BasePredictionModel):
    def __init__(self, model_type: str = "random_forest"):
        super().__init__(model_type)
        if model_type == "random_forest":
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
        elif model_type == "neural_network":
            self.model = SurvivalNN()
    
    def predict(self, 
                patient_data: pd.DataFrame, 
                time_points: List[int] = [12, 24, 60]
                ) -> Dict[str, float]:
        """
        Predict survival probabilities at specified time points
        
        Args:
            patient_data: DataFrame with patient features
            time_points: List of months for prediction
            
        Returns:
            Dictionary of survival probabilities at each time point
        """
        X = self.scaler.transform(patient_data)
        predictions = {}
        
        for months in time_points:
            if self.model_type == "random_forest":
                prob = self.model.predict_proba(X)[:, 1]
            else:
                prob = self.model(torch.FloatTensor(X))
                
            predictions[f"{months}_month"] = float(prob[0])
            
        return predictions

class RecurrencePredictor(BasePredictionModel):
    def __init__(self, model_type: str = "random_forest"):
        super().__init__(model_type)
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
    
    def predict_recurrence_risk(self, 
                              patient_data: pd.DataFrame
                              ) -> Dict[str, Union[float, str]]:
        """
        Predict recurrence risk and categorize it
        
        Args:
            patient_data: DataFrame with patient features
            
        Returns:
            Dictionary with risk probability and category
        """
        X = self.scaler.transform(patient_data)
        prob = self.model.predict_proba(X)[0][1]
        
        # Categorize risk
        if prob < 0.1:
            category = "Low"
        elif prob < 0.2:
            category = "Intermediate"
        else:
            category = "High"
            
        return {
            "recurrence_probability": float(prob),
            "risk_category": category
        }

class TreatmentResponsePredictor(BasePredictionModel):
    def __init__(self, model_type: str = "random_forest"):
        super().__init__(model_type)
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
    
    def predict_response(self,
                        patient_data: pd.DataFrame,
                        treatment_type: str
                        ) -> Dict[str, Union[float, str]]:
        """
        Predict probability of response to specific treatment
        
        Args:
            patient_data: DataFrame with patient features
            treatment_type: Type of treatment
            
        Returns:
            Dictionary with response probabilities and recommendation
        """
        X = self.scaler.transform(patient_data)
        response_prob = self.model.predict_proba(X)[0][1]
        
        # Generate recommendation
        if response_prob > 0.7:
            recommendation = "Strongly Recommended"
        elif response_prob > 0.5:
            recommendation = "Consider Treatment"
        else:
            recommendation = "Consider Alternatives"
            
        return {
            "response_probability": float(response_prob),
            "recommendation": recommendation,
            "treatment_type": treatment_type
        }

class SurvivalNN(nn.Module):
    def __init__(self, input_size: int = 20, hidden_size: int = 64):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size // 2, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        return self.network(x) 
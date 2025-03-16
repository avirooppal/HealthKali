"""
Data processing utilities for ML model training.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from typing import Tuple, List, Dict, Optional
from sklearn.model_selection import train_test_split

class DataProcessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = []
        self.target_column = None
        
    def prepare_training_data(self,
                            data: pd.DataFrame,
                            target: str,
                            features: Optional[List[str]] = None,
                            test_size: float = 0.2
                            ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Prepare data for model training
        
        Args:
            data: Input DataFrame
            target: Target column name
            features: List of feature columns
            test_size: Proportion of test set
            
        Returns:
            X_train, X_test, y_train, y_test
        """
        # Select features
        if features is None:
            features = [col for col in data.columns if col != target]
        
        self.feature_columns = features
        self.target_column = target
        
        # Extract features and target
        X = data[features]
        y = data[target]
        
        # Encode categorical variables
        X = self._encode_categorical(X)
        
        # Scale features
        X = self.scaler.fit_transform(X)
        
        # Split data
        return train_test_split(X, y, test_size=test_size, random_state=42)
    
    def prepare_survival_data(self,
                            data: pd.DataFrame,
                            time_column: str,
                            event_column: str,
                            features: Optional[List[str]] = None
                            ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Prepare data for survival analysis
        
        Args:
            data: Input DataFrame
            time_column: Name of time column
            event_column: Name of event indicator column
            features: List of feature columns
            
        Returns:
            X, time, event
        """
        if features is None:
            features = [col for col in data.columns 
                       if col not in [time_column, event_column]]
        
        X = data[features]
        time = data[time_column]
        event = data[event_column]
        
        # Encode categorical variables
        X = self._encode_categorical(X)
        
        # Scale features
        X = self.scaler.fit_transform(X)
        
        return X, time.values, event.values
    
    def _encode_categorical(self, data: pd.DataFrame) -> pd.DataFrame:
        """Encode categorical variables"""
        data = data.copy()
        for column in data.select_dtypes(include=['object']).columns:
            if column not in self.label_encoders:
                self.label_encoders[column] = LabelEncoder()
            data[column] = self.label_encoders[column].fit_transform(data[column])
        return data
    
    def transform_new_data(self, data: pd.DataFrame) -> np.ndarray:
        """
        Transform new data using fitted preprocessors
        
        Args:
            data: Input DataFrame
            
        Returns:
            Transformed features
        """
        data = data[self.feature_columns].copy()
        
        # Encode categorical variables
        for column, encoder in self.label_encoders.items():
            if column in data.columns:
                data[column] = encoder.transform(data[column])
        
        # Scale features
        return self.scaler.transform(data) 
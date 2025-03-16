"""
Model training utilities and workflows.
"""

from sklearn.model_selection import GridSearchCV
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    roc_auc_score, mean_squared_error
)
import numpy as np
from typing import Dict, Any, Optional, List
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
import pandas as pd
from .data_processor import DataProcessor

class ModelTrainer:
    def __init__(self, model_type: str, model_params: Optional[Dict] = None):
        """
        Initialize model trainer
        
        Args:
            model_type: Type of model to train
            model_params: Model parameters
        """
        self.model_type = model_type
        self.model_params = model_params or {}
        self.model = None
        self.data_processor = DataProcessor()
        
    def train(self,
             data: pd.DataFrame,
             target: str,
             features: Optional[List[str]] = None,
             validation_split: float = 0.2
             ) -> Dict[str, float]:
        """
        Train model and evaluate performance
        
        Args:
            data: Training data
            target: Target column name
            features: Feature columns
            validation_split: Validation set proportion
            
        Returns:
            Dictionary of performance metrics
        """
        # Prepare data
        X_train, X_val, y_train, y_val = self.data_processor.prepare_training_data(
            data, target, features, validation_split
        )
        
        if self.model_type == "neural_network":
            return self._train_neural_network(X_train, X_val, y_train, y_val)
        else:
            return self._train_sklearn_model(X_train, X_val, y_train, y_val)
    
    def _train_sklearn_model(self,
                           X_train: np.ndarray,
                           X_val: np.ndarray,
                           y_train: np.ndarray,
                           y_val: np.ndarray
                           ) -> Dict[str, float]:
        """Train scikit-learn model"""
        from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
        
        # Initialize model
        if self.model_type == "random_forest_classifier":
            self.model = RandomForestClassifier(**self.model_params)
        elif self.model_type == "random_forest_regressor":
            self.model = RandomForestRegressor(**self.model_params)
        
        # Train model
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_val)
        metrics = self._calculate_metrics(y_val, y_pred)
        
        return metrics
    
    def _train_neural_network(self,
                            X_train: np.ndarray,
                            X_val: np.ndarray,
                            y_train: np.ndarray,
                            y_val: np.ndarray
                            ) -> Dict[str, float]:
        """Train neural network model"""
        # Convert to tensors
        X_train = torch.FloatTensor(X_train)
        y_train = torch.FloatTensor(y_train)
        X_val = torch.FloatTensor(X_val)
        y_val = torch.FloatTensor(y_val)
        
        # Create data loaders
        train_dataset = TensorDataset(X_train, y_train)
        train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
        
        # Initialize model
        input_size = X_train.shape[1]
        self.model = self._create_neural_network(input_size)
        
        # Training parameters
        criterion = nn.BCEWithLogitsLoss()
        optimizer = torch.optim.Adam(self.model.parameters())
        
        # Training loop
        for epoch in range(100):
            self.model.train()
            for batch_X, batch_y in train_loader:
                optimizer.zero_grad()
                outputs = self.model(batch_X)
                loss = criterion(outputs, batch_y.unsqueeze(1))
                loss.backward()
                optimizer.step()
        
        # Evaluate
        self.model.eval()
        with torch.no_grad():
            y_pred = self.model(X_val)
            y_pred = torch.sigmoid(y_pred).numpy()
        
        metrics = self._calculate_metrics(y_val.numpy(), y_pred)
        
        return metrics
    
    def _create_neural_network(self, input_size: int) -> nn.Module:
        """Create neural network architecture"""
        return nn.Sequential(
            nn.Linear(input_size, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, 1)
        )
    
    def _calculate_metrics(self,
                         y_true: np.ndarray,
                         y_pred: np.ndarray
                         ) -> Dict[str, float]:
        """Calculate performance metrics"""
        metrics = {}
        
        if self.model_type.endswith('classifier'):
            metrics['accuracy'] = accuracy_score(y_true, y_pred)
            metrics['precision'] = precision_score(y_true, y_pred)
            metrics['recall'] = recall_score(y_true, y_pred)
            metrics['auc_roc'] = roc_auc_score(y_true, y_pred)
        else:
            metrics['mse'] = mean_squared_error(y_true, y_pred)
            metrics['rmse'] = np.sqrt(metrics['mse'])
        
        return metrics
    
    def save_model(self, path: str) -> None:
        """Save trained model"""
        if self.model_type == "neural_network":
            torch.save(self.model.state_dict(), path)
        else:
            import joblib
            joblib.dump(self.model, path)
    
    def load_model(self, path: str) -> None:
        """Load trained model"""
        if self.model_type == "neural_network":
            self.model.load_state_dict(torch.load(path))
        else:
            import joblib
            self.model = joblib.load(path) 
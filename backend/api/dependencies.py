from typing import Optional
import os
from functools import lru_cache

from backend.ml.simulation.progression_model import ProgressionModel
from backend.utils.config import settings

@lru_cache()
def get_progression_model() -> ProgressionModel:
    """
    Create or load a progression model.
    Uses caching to avoid reloading the model for each request.
    
    Returns:
        ProgressionModel: An initialized progression model
    """
    model_path = None
    
    # Check if a pre-trained model exists
    if os.path.exists(settings.MODEL_PATH):
        model_path = settings.MODEL_PATH
        
    return ProgressionModel(model_path=model_path)

@lru_cache()
def get_risk_model():
    """
    Create or load a risk assessment model.
    
    Returns:
        A risk assessment model
    """
    # This would be implemented to load the risk model
    # For now just return None as we use the simplified risk model
    return None

@lru_cache()
def get_treatment_model():
    """
    Create or load a treatment response model.
    
    Returns:
        A treatment response model
    """
    # This would be implemented to load the treatment model
    # For now just return None as we use the simplified model
    return None 
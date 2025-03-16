"""
Helper functions for the Cancer Digital Twin application.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Union, Any
import pandas as pd
import logging
from pathlib import Path
import json
from datetime import datetime
import torch
from scipy import stats

def validate_patient_data(data: Dict) -> Tuple[bool, Optional[str]]:
    """
    Validate patient data format and required fields
    
    Args:
        data: Patient data dictionary
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = [
        'age', 'tumor_size', 'grade', 'nodes_positive',
        'er_status', 'pr_status', 'her2_status'
    ]
    
    missing = [field for field in required_fields if field not in data]
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"
    
    # Validate data types and ranges
    try:
        if not (0 <= float(data['age']) <= 120):
            return False, "Age must be between 0 and 120"
        
        if not (0 <= float(data['tumor_size']) <= 1000):
            return False, "Tumor size must be between 0 and 1000 mm"
        
        if data['grade'] not in [1, 2, 3]:
            return False, "Grade must be 1, 2, or 3"
        
        if not (0 <= int(data['nodes_positive']) <= 100):
            return False, "Number of positive nodes must be between 0 and 100"
        
        for status in ['er_status', 'pr_status', 'her2_status']:
            if data[status] not in ['positive', 'negative']:
                return False, f"{status} must be 'positive' or 'negative'"
                
    except (ValueError, TypeError):
        return False, "Invalid data type in fields"
    
    return True, None

def calculate_confidence_interval(
    values: np.ndarray,
    confidence: float = 0.95
) -> Tuple[float, float]:
    """
    Calculate confidence interval for a set of values
    
    Args:
        values: Array of values
        confidence: Confidence level (default 0.95)
        
    Returns:
        Tuple of (lower_bound, upper_bound)
    """
    mean = np.mean(values)
    std_err = stats.sem(values)
    ci = stats.t.interval(confidence, len(values)-1, mean, std_err)
    return ci[0], ci[1]

def format_prediction_output(
    predictions: Dict,
    include_confidence: bool = True,
    confidence_level: float = 0.95
) -> Dict:
    """
    Format model predictions with confidence intervals
    
    Args:
        predictions: Raw prediction dictionary
        include_confidence: Whether to include confidence intervals
        confidence_level: Confidence level for intervals
        
    Returns:
        Formatted prediction dictionary
    """
    formatted = {}
    
    for key, value in predictions.items():
        if isinstance(value, np.ndarray):
            if include_confidence:
                ci_low, ci_high = calculate_confidence_interval(
                    value, confidence_level
                )
                formatted[key] = {
                    'value': float(np.mean(value)),
                    'confidence_interval': {
                        'lower': float(ci_low),
                        'upper': float(ci_high),
                        'level': confidence_level
                    }
                }
            else:
                formatted[key] = float(np.mean(value))
        else:
            formatted[key] = value
    
    formatted['timestamp'] = datetime.now().isoformat()
    return formatted

def load_model_weights(
    model: Union[torch.nn.Module, object],
    weights_path: Union[str, Path],
    device: str = 'cpu'
) -> None:
    """
    Load model weights from file
    
    Args:
        model: Model instance
        weights_path: Path to weights file
        device: Device to load weights on
    """
    weights_path = Path(weights_path)
    if not weights_path.exists():
        raise FileNotFoundError(f"Weights file not found: {weights_path}")
    
    try:
        if isinstance(model, torch.nn.Module):
            state_dict = torch.load(weights_path, map_location=device)
            model.load_state_dict(state_dict)
        else:
            import joblib
            loaded_model = joblib.load(weights_path)
            # Copy attributes from loaded model
            for key, value in loaded_model.__dict__.items():
                setattr(model, key, value)
    except Exception as e:
        raise RuntimeError(f"Error loading model weights: {str(e)}")

def setup_logging(
    log_path: Union[str, Path],
    level: str = 'INFO',
    format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
) -> None:
    """
    Setup logging configuration
    
    Args:
        log_path: Path to log file
        level: Logging level
        format: Log message format
    """
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format,
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()
        ]
    )
    
    # Set library logging levels
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    logging.info(f"Logging initialized: {log_path}")

def cache_result(
    key: str,
    value: Any,
    cache_dir: Union[str, Path],
    ttl: int = 3600
) -> None:
    """
    Cache result to file
    
    Args:
        key: Cache key
        value: Value to cache
        cache_dir: Cache directory
        ttl: Time to live in seconds
    """
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    cache_file = cache_dir / f"{key}.json"
    cache_data = {
        'value': value,
        'timestamp': datetime.now().timestamp(),
        'ttl': ttl
    }
    
    with open(cache_file, 'w') as f:
        json.dump(cache_data, f)

def get_cached_result(
    key: str,
    cache_dir: Union[str, Path]
) -> Optional[Any]:
    """
    Get cached result if valid
    
    Args:
        key: Cache key
        cache_dir: Cache directory
        
    Returns:
        Cached value if valid, None otherwise
    """
    cache_file = Path(cache_dir) / f"{key}.json"
    
    if not cache_file.exists():
        return None
    
    try:
        with open(cache_file, 'r') as f:
            cache_data = json.load(f)
            
        # Check if cache is expired
        age = datetime.now().timestamp() - cache_data['timestamp']
        if age > cache_data['ttl']:
            return None
            
        return cache_data['value']
    except Exception:
        return None 
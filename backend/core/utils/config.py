"""
Configuration management for the Cancer Digital Twin application.
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
import logging

class Config:
    """Configuration manager for the application."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path or os.getenv(
            'CANCER_TWIN_CONFIG',
            'config/default.yaml'
        )
        self.config: Dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> None:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            logging.warning(f"Config file not found at {self.config_path}. Using defaults.")
            self._set_defaults()

    def _set_defaults(self) -> None:
        """Set default configuration values"""
        self.config = {
            'data': {
                'base_path': 'data/',
                'tcga_path': 'data/tcga/',
                'metabric_path': 'data/metabric/',
                'wisconsin_path': 'data/wisconsin/',
                'cache_dir': 'cache/'
            },
            'models': {
                'weights_dir': 'models/weights/',
                'cache_predictions': True,
                'prediction_cache_ttl': 3600,  # 1 hour
                'default_confidence_level': 0.95
            },
            'api': {
                'host': 'localhost',
                'port': 8000,
                'debug': False,
                'workers': 4,
                'timeout': 30
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'file': 'logs/cancer_twin.log'
            },
            'security': {
                'api_key_required': True,
                'token_expiry': 3600,  # 1 hour
                'max_requests_per_minute': 100
            },
            'simulation': {
                'default_iterations': 1000,
                'max_iterations': 10000,
                'time_horizon_months': 60
            },
            'treatment': {
                'max_combinations': 5,
                'include_experimental': False
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value
        
        Args:
            key: Configuration key (dot notation supported)
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        try:
            value = self.config
            for k in key.split('.'):
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value
        
        Args:
            key: Configuration key (dot notation supported)
            value: Value to set
        """
        keys = key.split('.')
        current = self.config
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
            
        current[keys[-1]] = value

    def save(self) -> None:
        """Save current configuration to file"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)

    def validate(self) -> bool:
        """
        Validate configuration
        
        Returns:
            True if configuration is valid
        """
        required_keys = [
            'data.base_path',
            'models.weights_dir',
            'logging.level',
            'api.host',
            'api.port'
        ]
        
        for key in required_keys:
            if not self.get(key):
                logging.error(f"Missing required configuration key: {key}")
                return False
        
        return True

    def get_path(self, key: str) -> Path:
        """
        Get path from configuration
        
        Args:
            key: Configuration key for path
            
        Returns:
            Path object
        """
        path = self.get(key)
        if not path:
            raise ValueError(f"Path not found in configuration: {key}")
        return Path(path) 
"""
Preprocessing modules for different cancer datasets
"""

from .metabric import MetabricPreprocessor
from .tcga import TCGAPreprocessor
from .wisconsin import WisconsinPreprocessor

__all__ = ['MetabricPreprocessor', 'TCGAPreprocessor', 'WisconsinPreprocessor'] 
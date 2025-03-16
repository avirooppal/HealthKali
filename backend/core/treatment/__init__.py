"""
Treatment module for the Cancer Digital Twin application.
This module provides functionality for simulating treatment responses
and generating personalized treatment recommendations.
"""

from backend.core.treatment.simulation import (
    simulate_treatment_response,
    simulate_treatment_sequence,
    calculate_side_effects
)

from backend.core.treatment.recommendations import (
    generate_treatment_recommendations,
    get_nccn_guideline_treatments,
    check_treatment_contraindications
)

__all__ = [
    'simulate_treatment_response',
    'simulate_treatment_sequence',
    'calculate_side_effects',
    'generate_treatment_recommendations',
    'get_nccn_guideline_treatments',
    'check_treatment_contraindications'
] 
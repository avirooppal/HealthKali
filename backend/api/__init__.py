"""
API module for the Cancer Digital Twin application.
This module provides the REST API endpoints for interacting with digital twins.
"""

from fastapi import APIRouter

# Create the main API router
api_router = APIRouter()

# Import routes to register them with the router
from backend.api.routes import router as twin_router

# Include the twin router
api_router.include_router(twin_router, prefix="")

__version__ = "1.0.0"
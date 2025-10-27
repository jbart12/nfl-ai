"""
API Router - Aggregates all endpoint routers
"""
from fastapi import APIRouter
from app.api.endpoints import predictions

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    predictions.router,
    prefix="/predictions",
    tags=["predictions"]
)

# You can add more routers here as you build them:
# api_router.include_router(players.router, prefix="/players", tags=["players"])
# api_router.include_router(data_sync.router, prefix="/data-sync", tags=["data-sync"])

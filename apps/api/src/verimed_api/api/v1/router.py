"""API v1 router aggregator."""

from fastapi import APIRouter

from verimed_api.api.v1.endpoints import auth, evidence, feedback, health, verify

api_v1_router = APIRouter()
api_v1_router.include_router(auth.router)
api_v1_router.include_router(health.router)
api_v1_router.include_router(verify.router)
api_v1_router.include_router(evidence.router)
api_v1_router.include_router(feedback.router)

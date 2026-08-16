from fastapi import APIRouter
from app.api.campaigns import router as campaigns_router
from app.api.leads import router as leads_router
from app.api.discovery import router as discovery_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(campaigns_router)
api_router.include_router(leads_router)
api_router.include_router(discovery_router)

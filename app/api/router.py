from fastapi import APIRouter
from app.api.campaigns import router as campaigns_router
from app.api.leads import router as leads_router
from app.api.discovery import router as discovery_router
from app.api.audit import router as audit_router
from app.api.qualification import router as qualification_router
from app.api.research import router as research_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(campaigns_router)
api_router.include_router(leads_router)
api_router.include_router(discovery_router)
api_router.include_router(audit_router)
api_router.include_router(qualification_router)
api_router.include_router(research_router)

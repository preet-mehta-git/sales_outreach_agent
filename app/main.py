from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.api.router import api_router
from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables & seed data on startup
    init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Restaurant & Cafe Prospecting Engine REST API",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(api_router)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "environment": settings.ENV,
        "outreach_mode": settings.OUTREACH_MODE
    }

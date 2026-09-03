import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.db.init_db import init_db
from app.api.auth import router as auth_router
from app.api.screenings import router as screenings_router
from app.api.documents import router as documents_router
from app.api.reviews import router as reviews_router
from app.api.audit import router as audit_router
from app.api.watchlist import router as watchlist_router
from app.api.dashboard import router as dashboard_router
from app.api.settings import router as settings_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables and seed baseline data on startup
    init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="Fake Identity & Document Screening System (SIH 2026 Problem Statement 26188)",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads directory for static document previews
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/static/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include Routers under /api
app.include_router(auth_router, prefix="/api")
app.include_router(screenings_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(reviews_router, prefix="/api")
app.include_router(audit_router, prefix="/api")
app.include_router(watchlist_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(settings_router, prefix="/api")


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "environment": settings.APP_ENV,
    }


@app.get("/")
def root():
    return {
        "system": settings.APP_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }

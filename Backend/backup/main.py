"""
Main FastAPI application entry point with enhanced security features
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import logging
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.api_v1.api import api_router
from app.core.database import engine, Base
from app.core.exceptions import CustomHTTPException

# Security middleware imports
from app.core.security_middleware import (
    SecurityMiddleware,
    SecurityHeadersMiddleware,
    InputValidationMiddleware
)
from app.core.ssl_config import setup_ssl_for_development


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting up Resumify API...")

    # Create database tables
    Base.metadata.create_all(bind=engine)

    # Create upload directory
    os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)

    yield

    # Shutdown
    logger.info("Shutting down Resumify API...")


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add security middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(InputValidationMiddleware)
app.add_middleware(SecurityMiddleware, max_request_size=10*1024*1024)  # 10MB limit

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# DEBUG: Add a simple test endpoint
from app.core.database import get_db
from app.services.auth_service import AuthService

@app.get("/debug-users")
async def debug_users():
    """Simple debug endpoint to check users"""
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        users = AuthService.get_users(db)
        users_data = []
        for user in users:
            users_data.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": str(user.role),
                "is_active": user.is_active
            })
        return {"users": users_data, "total": len(users_data)}
    finally:
        db.close()

# Serve uploaded files
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_FOLDER), name="uploads")


# Global exception handler
@app.exception_handler(CustomHTTPException)
async def custom_http_exception_handler(request: Request, exc: CustomHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error_code": exc.error_code}
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Resumify API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
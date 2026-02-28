from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from config import settings
from database import engine, Base
from utils.cloudinary import init_cloudinary

# --------------- Rate Limiter ---------------
limiter = Limiter(key_func=get_remote_address, default_limits=["50/minute"])

# Import ALL models so that Base.metadata knows about every table.
import models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("🚀 Starting ManFei SPA Backend...")
    print(f"📦 Database: {settings.DATABASE_URL.split('@')[-1]}")  # Hide credentials
    print(f"🔐 LINE Channel ID: {settings.LINE_CHANNEL_ID[:10]}...")
    print(f"🌐 Frontend URL: {settings.FRONTEND_URL}")
    
    # Initialize Cloudinary
    init_cloudinary()
    
    yield
    
    # Shutdown
    print("👋 Shutting down ManFei SPA Backend...")


app = FastAPI(
    title="ManFei SPA API",
    description="Backend API for ManFei Spa Business Web Application",
    version="1.0.0",
    lifespan=lifespan
)

# --------------- Rate Limiter middleware ---------------
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --------------- CORS ---------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)

# Import routers
from routers import auth_router, admin_router, staff_router, public_router
from routers import upload_router

# Include routers
app.include_router(auth_router.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(admin_router.router, prefix="/api/admin", tags=["Admin"])
app.include_router(upload_router.router, prefix="/api/admin", tags=["Upload"])
app.include_router(staff_router.router, prefix="/api/staff", tags=["Staff"])
app.include_router(public_router.router, prefix="/api/public", tags=["Public"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "ManFei SPA API",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "health": "/api/health",
            "auth": "/api/auth",
            "admin": "/api/admin",
            "staff": "/api/staff",
            "public": "/api/public"
        }
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "manfei-spa-backend",
        "timestamp": "2026-02-15"
    }

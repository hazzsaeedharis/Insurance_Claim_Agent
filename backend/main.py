"""
ClaimAI Pro - AI-Powered Insurance Claims Processing Platform
Main FastAPI application entry point

Features:
- Multi-provider AI (OpenAI, Google Gemini, Anthropic)
- Automated claim processing
- Real-time fraud detection
- Intelligent document analysis
- Automated decision making
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv

from config import settings
from claims import router as claims_router
from ai import router as ai_router
from dashboard import router as dashboard_router

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="ClaimAI Pro API",
    description="🚀 AI-Powered Insurance Claims Processing Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(claims_router, prefix="/api/claims", tags=["Claims"])
app.include_router(ai_router, prefix="/api/ai", tags=["AI Processing"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("🚀 ClaimAI Pro Backend Started!")
    print(f"📊 Demo Mode: {settings.DEMO_MODE}")
    print(f"🤖 AI Provider: {settings.DEFAULT_AI_PROVIDER}")
    print(f"📡 API Docs: http://{settings.API_HOST}:{settings.API_PORT}/docs")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "🚀 ClaimAI Pro API - AI-Powered Insurance Claims Processing",
        "version": "1.0.0",
        "status": "operational",
        "demo_mode": settings.DEMO_MODE,
        "ai_provider": settings.DEFAULT_AI_PROVIDER,
        "features": [
            "Multi-provider AI processing",
            "Automated fraud detection", 
            "Intelligent document analysis",
            "Real-time claim processing",
            "Automated decision making"
        ],
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "ai_demo": "/api/ai/demo"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "demo_mode": settings.DEMO_MODE,
        "ai_providers_available": {
            "openai": bool(settings.OPENAI_API_KEY),
            "google": bool(settings.GOOGLE_API_KEY),
            "anthropic": bool(settings.ANTHROPIC_API_KEY)
        },
        "database_connected": True  # Would check actual DB connection
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url)
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
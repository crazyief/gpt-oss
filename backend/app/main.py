"""
GPT-OSS Backend API
Main FastAPI application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import Dict

# Create FastAPI app instance
app = FastAPI(
    title="GPT-OSS LightRAG Assistant",
    description="Local AI Knowledge Assistant with LightRAG for cybersecurity document analysis",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint - API status"""
    return {
        "message": "GPT-OSS API is running",
        "status": "operational",
        "stage": "Stage 1 - Foundation",
        "version": "0.1.0"
    }


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint for Docker and monitoring"""
    return {
        "status": "healthy",
        "service": "gpt-oss-backend"
    }


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("🚀 GPT-OSS Backend starting...")
    print("📍 Stage 1: Foundation - Initializing basic services")

    # Create necessary directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("rag_data", exist_ok=True)

    print("✅ Backend ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("👋 GPT-OSS Backend shutting down...")
"""
Simplified AI Lead Generation Platform for Railway
FastAPI Backend with basic functionality
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import os

# Import routes
from routes.google_oauth_routes import router as google_oauth_router
from routes.google_sheets_routes import router as google_sheets_router
# from routes.makecom_routes import router as makecom_router
# from routes.ai_chat_routes import router as ai_chat_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Lead Generation Platform",
    description="Automated lead discovery, research, and outreach generation",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(google_oauth_router)
app.include_router(google_sheets_router)
# app.include_router(makecom_router)
# app.include_router(ai_chat_router)

# Mount static files (React app)
if os.path.exists("/app/frontend/dist"):
    app.mount("/assets", StaticFiles(directory="/app/frontend/dist/assets"), name="assets")
    app.mount("/static", StaticFiles(directory="/app/frontend/dist"), name="static")

@app.get("/")
async def root():
    """Root endpoint - serve React app"""
    if os.path.exists("/app/frontend/dist/index.html"):
        return FileResponse("/app/frontend/dist/index.html")
    else:
        return {
            "message": "AI Lead Generation Platform API", 
            "version": "2.0.0",
            "status": "running"
        }

# Catch-all route for React Router (must be last)
@app.get("/{path:path}")
async def serve_react_app(path: str):
    """Serve React app for all non-API routes"""
    if not path.startswith("api") and os.path.exists("/app/frontend/dist/index.html"):
        return FileResponse("/app/frontend/dist/index.html")
    else:
        return {"detail": "Not Found"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "timestamp": datetime.utcnow().isoformat(),
        "service": "AI Lead Generation Platform"
    }

@app.post("/jobs/")
async def create_job(job_data: dict):
    """Create a new lead generation job"""
    try:
        job_id = str(uuid.uuid4())
        logger.info(f"Creating job {job_id} with prompt: {job_data.get('prompt', 'N/A')}")
        
        return {
            "id": job_id,
            "prompt": job_data.get("prompt", ""),
            "target_count": job_data.get("target_count", 10),
            "quality_threshold": job_data.get("quality_threshold", 0.8),
            "status": "created",
            "created_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error creating job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    """Get job status"""
    return {
        "id": job_id,
        "status": "processing",
        "created_at": datetime.utcnow().isoformat(),
        "message": "Job is being processed"
    }

@app.get("/jobs/")
async def list_jobs():
    """List all jobs"""
    return {
        "jobs": [],
        "total": 0,
        "message": "No jobs found"
    }

@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify the API is working"""
    return {
        "message": "API is working!",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": "production"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

#!/usr/bin/env python3
"""
Simple FastAPI server for local testing
Basic endpoints without complex dependencies
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Optional
import uuid

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Lead Generation Platform",
    description="Local testing server",
    version="1.0.0"
)

# Simple data models
class JobCreate(BaseModel):
    prompt: str
    target_count: int = 25
    quality_threshold: float = 0.8

class JobResponse(BaseModel):
    id: str
    prompt: str
    status: str
    target_count: int
    quality_threshold: float
    created_at: datetime

# In-memory storage for testing
jobs_db = {}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Lead Generation Platform",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }

@app.post("/jobs", response_model=JobResponse)
async def create_job(job_data: JobCreate):
    """Create a new lead generation job"""
    try:
        job_id = str(uuid.uuid4())
        
        job = JobResponse(
            id=job_id,
            prompt=job_data.prompt,
            status="pending",
            target_count=job_data.target_count,
            quality_threshold=job_data.quality_threshold,
            created_at=datetime.utcnow()
        )
        
        # Store in memory
        jobs_db[job_id] = job.dict()
        
        logger.info(f"Created job {job_id}: {job_data.prompt[:50]}...")
        return job
        
    except Exception as e:
        logger.error(f"Error creating job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: str):
    """Get job details"""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_data = jobs_db[job_id]
    return JobResponse(**job_data)

@app.get("/jobs", response_model=List[JobResponse])
async def list_jobs():
    """List all jobs"""
    jobs = []
    for job_data in jobs_db.values():
        jobs.append(JobResponse(**job_data))
    
    return jobs

@app.get("/test")
async def test_endpoint():
    """Test endpoint for basic functionality"""
    return {
        "message": "Test endpoint working",
        "timestamp": datetime.utcnow(),
        "jobs_count": len(jobs_db)
    }

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting AI Lead Generation Platform (Local Testing)")
    logger.info("📖 API Documentation: http://localhost:8000/docs")
    logger.info("🔍 Health Check: http://localhost:8000/health")
    logger.info("🧪 Test Endpoint: http://localhost:8000/test")
    
    uvicorn.run(
        "simple_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

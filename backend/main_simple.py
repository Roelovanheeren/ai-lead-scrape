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
import asyncio
import time

# Import routes
try:
    from routes.google_oauth_routes import router as google_oauth_router
    from routes.google_sheets_routes import router as google_sheets_router
    OAUTH_ROUTES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"OAuth routes not available: {e}")
    OAUTH_ROUTES_AVAILABLE = False
# from routes.makecom_routes import router as makecom_router
# from routes.ai_chat_routes import router as ai_chat_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory job storage (use database in production)
job_storage = {}

async def process_job_background(job_id: str, job_data: dict):
    """Process a job in the background with web scraping simulation"""
    try:
        logger.info(f"Starting background processing for job {job_id}")
        
        # Update job status to processing
        job_storage[job_id] = {
            "id": job_id,
            "status": "processing",
            "progress": 0,
            "message": "Starting web scraping...",
            "created_at": datetime.utcnow().isoformat(),
            "prompt": job_data.get("prompt", ""),
            "target_count": job_data.get("target_count", 10)
        }
        
        # Simulate web scraping process with realistic steps
        steps = [
            ("Analyzing prompt and extracting targeting criteria", 10),
            ("Searching Google for relevant companies", 25),
            ("Scraping company websites for contact information", 40),
            ("Finding LinkedIn profiles and email addresses", 60),
            ("Researching company details and decision makers", 80),
            ("Generating personalized outreach messages", 95),
            ("Finalizing results and preparing export", 100)
        ]
        
        for step_message, progress in steps:
            await asyncio.sleep(2)  # Simulate processing time
            job_storage[job_id].update({
                "progress": progress,
                "message": step_message
            })
            logger.info(f"Job {job_id}: {step_message} ({progress}%)")
        
        # Simulate finding leads based on target count
        target_count = job_data.get("target_count", 10)
        existing_leads = job_data.get("existing_leads", [])
        exclude_existing = job_data.get("exclude_existing_leads", False)
        
        logger.info(f"Job {job_id}: Target count: {target_count}, Existing leads: {len(existing_leads)}, Exclude existing: {exclude_existing}")
        
        simulated_leads = []
        
        # Generate leads, excluding existing ones if requested
        for i in range(min(target_count, 50)):  # Cap at 50 for demo
            # Check if we should exclude this lead based on existing data
            if exclude_existing and existing_leads:
                # Simple check to avoid duplicates (in real implementation, use more sophisticated matching)
                company_name = f"Company {i+1}"
                email = f"contact{i+1}@company{i+1}.com"
                
                # Check if this lead already exists
                is_duplicate = any(
                    existing.get('company', '').lower() == company_name.lower() or 
                    existing.get('email', '').lower() == email.lower()
                    for existing in existing_leads
                )
                
                if is_duplicate:
                    logger.info(f"Job {job_id}: Skipping duplicate lead {company_name}")
                    continue
            
            lead = {
                "id": f"lead_{i+1}",
                "company": f"Company {i+1}",
                "contact_name": f"Contact {i+1}",
                "email": f"contact{i+1}@company{i+1}.com",
                "phone": f"+1-555-{1000+i:04d}",
                "linkedin": f"https://linkedin.com/in/contact{i+1}",
                "website": f"https://company{i+1}.com",
                "industry": "Technology",
                "location": "United States",
                "confidence": 0.85 + (i * 0.01),
                "source": "AI Platform",
                "created_at": datetime.utcnow().isoformat()
            }
            simulated_leads.append(lead)
        
        # Update job status to completed
        job_storage[job_id].update({
            "status": "completed",
            "progress": 100,
            "message": f"Job completed! Found {len(simulated_leads)} leads.",
            "leads": simulated_leads,
            "completed_at": datetime.utcnow().isoformat()
        })
        
        logger.info(f"Job {job_id} completed successfully with {len(simulated_leads)} leads")
        
        # If Google Sheets is connected, try to export results
        if job_data.get("connected_sheet_id"):
            try:
                await export_to_google_sheets(job_id, simulated_leads, job_data)
            except Exception as e:
                logger.error(f"Failed to export to Google Sheets: {e}")
        
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {str(e)}")
        job_storage[job_id] = {
            "id": job_id,
            "status": "failed",
            "message": f"Job failed: {str(e)}",
            "error": str(e),
            "created_at": datetime.utcnow().isoformat()
        }

async def export_to_google_sheets(job_id: str, leads: list, job_data: dict):
    """Export leads to connected Google Sheet"""
    try:
        # This would integrate with the Google Sheets service
        logger.info(f"Exporting {len(leads)} leads to Google Sheets for job {job_id}")
        # Implementation would use the Google Sheets API
    except Exception as e:
        logger.error(f"Failed to export to Google Sheets: {e}")

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
if OAUTH_ROUTES_AVAILABLE:
    app.include_router(google_oauth_router)
    app.include_router(google_sheets_router)
    logger.info("OAuth routes enabled")
else:
    logger.warning("OAuth routes disabled - missing dependencies")
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
    """Create a new lead generation job and start processing"""
    try:
        job_id = str(uuid.uuid4())
        logger.info(f"Creating job {job_id} with prompt: {job_data.get('prompt', 'N/A')}")
        
        # Store job immediately in job_storage
        job_storage[job_id] = {
            "id": job_id,
            "status": "started",
            "progress": 0,
            "message": "Job started successfully. Web scraping is now in progress.",
            "created_at": datetime.utcnow().isoformat(),
            "prompt": job_data.get("prompt", ""),
            "target_count": job_data.get("target_count", 10),
            "quality_threshold": job_data.get("quality_threshold", 0.8)
        }
        
        # Start the job processing in the background
        import asyncio
        asyncio.create_task(process_job_background(job_id, job_data))
        
        return {
            "job_id": job_id,
            "prompt": job_data.get("prompt", ""),
            "target_count": job_data.get("target_count", 10),
            "quality_threshold": job_data.get("quality_threshold", 0.8),
            "status": "started",
            "created_at": datetime.utcnow().isoformat(),
            "message": "Job started successfully. Web scraping is now in progress."
        }
    except Exception as e:
        logger.error(f"Error creating job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    """Get job status"""
    try:
        logger.info(f"Getting job status for job_id: {job_id}")
        logger.info(f"Available jobs in storage: {list(job_storage.keys())}")
        
        if job_id in job_storage:
            job_data = job_storage[job_id]
            logger.info(f"Found job {job_id}: {job_data.get('status', 'unknown')}")
            return job_data
        else:
            logger.warning(f"Job {job_id} not found in storage")
            return {
                "id": job_id,
                "status": "not_found",
                "message": "Job not found"
            }
    except Exception as e:
        logger.error(f"Error getting job {job_id}: {str(e)}")
        return {
            "id": job_id,
            "status": "error",
            "message": f"Error retrieving job: {str(e)}"
        }

@app.get("/jobs/")
async def list_jobs():
    """List all jobs"""
    jobs = list(job_storage.values())
    return {
        "jobs": jobs,
        "total": len(jobs),
        "message": f"Found {len(jobs)} jobs"
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

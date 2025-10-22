"""
Enhanced AI-Driven Lead Generation Platform
FastAPI backend aligned with the simplified service layer.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import logging
from typing import List, Optional
from datetime import datetime

from .models.schemas import (
    JobCreate,
    JobResponse,
    CompanyResponse,
    ContactResponse,
    OutreachContentResponse,
)
from .services.job_orchestrator import JobOrchestrator
from .services.company_discovery import CompanyDiscoveryService
from .services.contact_identification import ContactIdentificationService
from .services.research_engine import ResearchEngine
from .services.outreach_generator import OutreachGenerator

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
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize services (share the orchestrator's dependencies)
job_orchestrator = JobOrchestrator()
company_discovery = job_orchestrator.company_discovery
contact_identification = job_orchestrator.contact_identification
research_engine = job_orchestrator.research_engine
outreach_generator = job_orchestrator.outreach_generator

@app.get("/")
async def root():
    return {"message": "AI Lead Generation Platform API", "version": "2.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Job Management Endpoints
@app.post("/jobs", response_model=JobResponse)
async def create_job(job_data: JobCreate, background_tasks: BackgroundTasks):
    """Create a new lead generation job"""
    try:
        job = await job_orchestrator.create_job(job_data)
        
        # Start background processing
        background_tasks.add_task(job_orchestrator.process_job, job.id)
        
        return job
    except Exception as e:
        logger.error(f"Error creating job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: str):
    """Get job status and details"""
    job = await job_orchestrator.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.get("/jobs", response_model=List[JobResponse])
async def list_jobs(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
):
    """List jobs with optional filtering"""
    jobs = await job_orchestrator.list_jobs(status, limit, offset)
    return jobs

@app.post("/jobs/{job_id}/cancel")
async def cancel_job(job_id: str):
    """Cancel a running job"""
    success = await job_orchestrator.cancel_job(job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Job not found or cannot be cancelled")
    return {"message": "Job cancelled successfully"}

# Company Discovery Endpoints
@app.get("/jobs/{job_id}/companies", response_model=List[CompanyResponse])
async def get_companies(
    job_id: str,
    limit: int = 100,
    offset: int = 0,
):
    """Get companies discovered for a job"""
    companies = await company_discovery.get_companies(job_id, limit, offset)
    return companies

@app.post("/jobs/{job_id}/companies/{company_id}/refresh")
async def refresh_company_data(
    job_id: str,
    company_id: str,
    background_tasks: BackgroundTasks,
):
    """Refresh company data and research"""
    background_tasks.add_task(
        company_discovery.refresh_company_data, company_id
    )
    return {"message": "Company refresh initiated"}

# Contact Management Endpoints
@app.get("/companies/{company_id}/contacts", response_model=List[ContactResponse])
async def get_company_contacts(company_id: str):
    """Get contacts for a specific company"""
    contacts = await contact_identification.get_company_contacts(company_id)
    return contacts

@app.post("/companies/{company_id}/contacts/refresh")
async def refresh_contacts(
    company_id: str,
    background_tasks: BackgroundTasks,
):
    """Refresh contact data for a company"""
    background_tasks.add_task(
        contact_identification.refresh_company_contacts, company_id
    )
    return {"message": "Contact refresh initiated"}

# Research Endpoints
@app.get("/companies/{company_id}/profile")
async def get_company_profile(company_id: str):
    """Get detailed company research profile"""
    profile = await research_engine.get_company_profile(company_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Company profile not found")
    return profile

@app.post("/companies/{company_id}/research")
async def trigger_research(
    company_id: str,
    background_tasks: BackgroundTasks,
):
    """Trigger deep research for a company"""
    background_tasks.add_task(
        research_engine.research_company, company_id
    )
    return {"message": "Research initiated"}

# Outreach Endpoints
@app.get("/companies/{company_id}/outreach", response_model=List[OutreachContentResponse])
async def get_outreach_content(
    company_id: str,
    channel: Optional[str] = None,
):
    """Get outreach content for a company"""
    content = await outreach_generator.get_outreach_content(company_id, channel)
    return content

@app.post("/companies/{company_id}/outreach/generate")
async def generate_outreach(
    company_id: str,
    background_tasks: BackgroundTasks,
):
    """Generate outreach content for a company"""
    background_tasks.add_task(
        outreach_generator.generate_company_outreach, company_id
    )
    return {"message": "Outreach generation initiated"}

# Analytics and Monitoring
@app.get("/analytics/usage")
async def get_usage_analytics(
    days: int = 30,
):
    """Get API usage analytics"""
    analytics = await job_orchestrator.get_usage_analytics(days)
    return analytics

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

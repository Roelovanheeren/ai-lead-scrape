"""
Enhanced AI-Driven Lead Generation Platform
FastAPI Backend with comprehensive lead discovery, research, and outreach capabilities
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import asyncio
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid

from .database.connection import get_db
from .models.schemas import (
    JobCreate, JobResponse, CompanyResponse, ContactResponse,
    OutreachContentResponse, QAReviewRequest, JobStatus
)
from .services.job_orchestrator import JobOrchestrator
from .services.company_discovery import CompanyDiscoveryService
from .services.contact_identification import ContactIdentificationService
from .services.research_engine import ResearchEngine
from .services.outreach_generator import OutreachGenerator
from .services.quality_assurance import QualityAssuranceService
from .services.export_service import ExportService
from .integrations.apollo_client import ApolloClient
from .integrations.email_verification import EmailVerificationService
from .integrations.aimfox_client import AimfoxClient
from .integrations.ghl_client import GHLClient

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

# Initialize services
job_orchestrator = JobOrchestrator()
company_discovery = CompanyDiscoveryService()
contact_identification = ContactIdentificationService()
research_engine = ResearchEngine()
outreach_generator = OutreachGenerator()
qa_service = QualityAssuranceService()
export_service = ExportService()

# API Clients
apollo_client = ApolloClient()
email_verification = EmailVerificationService()
aimfox_client = AimfoxClient()
ghl_client = GHLClient()

@app.get("/")
async def root():
    return {"message": "AI Lead Generation Platform API", "version": "2.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Job Management Endpoints
@app.post("/jobs", response_model=JobResponse)
async def create_job(
    job_data: JobCreate,
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """Create a new lead generation job"""
    try:
        job = await job_orchestrator.create_job(db, job_data)
        
        # Start background processing
        background_tasks.add_task(job_orchestrator.process_job, job.id)
        
        return job
    except Exception as e:
        logger.error(f"Error creating job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, db = Depends(get_db)):
    """Get job status and details"""
    job = await job_orchestrator.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.get("/jobs", response_model=List[JobResponse])
async def list_jobs(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db = Depends(get_db)
):
    """List jobs with optional filtering"""
    jobs = await job_orchestrator.list_jobs(db, status, limit, offset)
    return jobs

@app.post("/jobs/{job_id}/cancel")
async def cancel_job(job_id: str, db = Depends(get_db)):
    """Cancel a running job"""
    success = await job_orchestrator.cancel_job(db, job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Job not found or cannot be cancelled")
    return {"message": "Job cancelled successfully"}

# Company Discovery Endpoints
@app.get("/jobs/{job_id}/companies", response_model=List[CompanyResponse])
async def get_companies(
    job_id: str,
    limit: int = 100,
    offset: int = 0,
    db = Depends(get_db)
):
    """Get companies discovered for a job"""
    companies = await company_discovery.get_companies(db, job_id, limit, offset)
    return companies

@app.post("/jobs/{job_id}/companies/{company_id}/refresh")
async def refresh_company_data(
    job_id: str,
    company_id: str,
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """Refresh company data and research"""
    background_tasks.add_task(
        company_discovery.refresh_company_data, db, company_id
    )
    return {"message": "Company refresh initiated"}

# Contact Management Endpoints
@app.get("/companies/{company_id}/contacts", response_model=List[ContactResponse])
async def get_company_contacts(
    company_id: str,
    db = Depends(get_db)
):
    """Get contacts for a specific company"""
    contacts = await contact_identification.get_company_contacts(db, company_id)
    return contacts

@app.post("/companies/{company_id}/contacts/refresh")
async def refresh_contacts(
    company_id: str,
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """Refresh contact data for a company"""
    background_tasks.add_task(
        contact_identification.refresh_company_contacts, db, company_id
    )
    return {"message": "Contact refresh initiated"}

# Research Endpoints
@app.get("/companies/{company_id}/profile")
async def get_company_profile(company_id: str, db = Depends(get_db)):
    """Get detailed company research profile"""
    profile = await research_engine.get_company_profile(db, company_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Company profile not found")
    return profile

@app.post("/companies/{company_id}/research")
async def trigger_research(
    company_id: str,
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """Trigger deep research for a company"""
    background_tasks.add_task(
        research_engine.research_company, db, company_id
    )
    return {"message": "Research initiated"}

# Outreach Endpoints
@app.get("/companies/{company_id}/outreach", response_model=List[OutreachContentResponse])
async def get_outreach_content(
    company_id: str,
    channel: Optional[str] = None,
    db = Depends(get_db)
):
    """Get outreach content for a company"""
    content = await outreach_generator.get_outreach_content(db, company_id, channel)
    return content

@app.post("/companies/{company_id}/outreach/generate")
async def generate_outreach(
    company_id: str,
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """Generate outreach content for a company"""
    background_tasks.add_task(
        outreach_generator.generate_company_outreach, db, company_id
    )
    return {"message": "Outreach generation initiated"}

@app.post("/outreach/{outreach_id}/approve")
async def approve_outreach(
    outreach_id: str,
    db = Depends(get_db)
):
    """Approve outreach content for sending"""
    success = await outreach_generator.approve_outreach(db, outreach_id)
    if not success:
        raise HTTPException(status_code=404, detail="Outreach content not found")
    return {"message": "Outreach approved"}

# Quality Assurance Endpoints
@app.get("/qa/pending")
async def get_pending_qa(db = Depends(get_db)):
    """Get items pending QA review"""
    pending = await qa_service.get_pending_reviews(db)
    return pending

@app.post("/qa/review")
async def submit_qa_review(
    review: QAReviewRequest,
    db = Depends(get_db)
):
    """Submit QA review for an item"""
    result = await qa_service.submit_review(db, review)
    return result

# Export and Delivery Endpoints
@app.post("/jobs/{job_id}/export/google-sheets")
async def export_to_google_sheets(
    job_id: str,
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """Export job results to Google Sheets"""
    background_tasks.add_task(
        export_service.export_to_google_sheets, db, job_id
    )
    return {"message": "Google Sheets export initiated"}

@app.post("/jobs/{job_id}/deliver/aimfox")
async def deliver_to_aimfox(
    job_id: str,
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """Deliver outreach content to Aimfox"""
    background_tasks.add_task(
        export_service.deliver_to_aimfox, db, job_id
    )
    return {"message": "Aimfox delivery initiated"}

@app.post("/jobs/{job_id}/deliver/ghl")
async def deliver_to_ghl(
    job_id: str,
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """Deliver contacts and research to GoHighLevel"""
    background_tasks.add_task(
        export_service.deliver_to_ghl, db, job_id
    )
    return {"message": "GHL delivery initiated"}

# Analytics and Monitoring
@app.get("/analytics/usage")
async def get_usage_analytics(
    days: int = 30,
    db = Depends(get_db)
):
    """Get API usage analytics"""
    analytics = await job_orchestrator.get_usage_analytics(db, days)
    return analytics

@app.get("/analytics/quality")
async def get_quality_metrics(
    days: int = 30,
    db = Depends(get_db)
):
    """Get quality assurance metrics"""
    metrics = await qa_service.get_quality_metrics(db, days)
    return metrics

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

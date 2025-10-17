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

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import real research functions
REAL_RESEARCH_AVAILABLE = False
try:
    from services.real_research import (
        extract_targeting_criteria,
        search_companies,
        research_company_deep,
        find_company_contacts,
        generate_personalized_outreach
    )
    REAL_RESEARCH_AVAILABLE = True
    logger.info("✅ Real research engine loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ Real research engine not available: {e}")
    logger.warning("⚠️ Using fallback simulation mode")
except Exception as e:
    logger.error(f"❌ Error loading real research engine: {e}")
    logger.warning("⚠️ Using fallback simulation mode")

# Fallback functions (always define these)
async def extract_targeting_criteria(prompt: str) -> Dict[str, Any]:
    return {"keywords": prompt.split()[:10], "industry": "Technology"}

async def search_companies(criteria: Dict[str, Any], target_count: int) -> List[Dict[str, Any]]:
    return []

async def research_company_deep(company: Dict[str, Any]) -> Dict[str, Any]:
    return company

async def find_company_contacts(company: Dict[str, Any]) -> List[Dict[str, Any]]:
    return []

async def generate_personalized_outreach(lead: Dict[str, Any]) -> Dict[str, Any]:
    return {"linkedin_message": "Hi! Let's connect.", "email_subject": "Partnership", "email_body": "Hi there!"}

# Import routes
try:
    from routes.google_oauth_routes import router as google_oauth_router
    OAUTH_ROUTES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"OAuth routes not available: {e}")
    OAUTH_ROUTES_AVAILABLE = False

try:
    from routes.google_sheets_routes import router as google_sheets_router
    SHEETS_ROUTES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Google Sheets routes not available: {e}")
    SHEETS_ROUTES_AVAILABLE = False
# from routes.makecom_routes import router as makecom_router
# from routes.ai_chat_routes import router as ai_chat_router

# In-memory job storage (use database in production)
job_storage = {}

async def process_job_background(job_id: str, job_data: dict):
    """Process a job in the background with REAL web scraping and research"""
    try:
        logger.info(f"="*80)
        logger.info(f"Starting REAL background processing for job {job_id}")
        logger.info(f"REAL_RESEARCH_AVAILABLE: {REAL_RESEARCH_AVAILABLE}")
        logger.info(f"Job data keys: {list(job_data.keys())}")
        logger.info(f"Prompt: {job_data.get('prompt', 'N/A')}")
        logger.info(f"Target count: {job_data.get('target_count', 'N/A')}")
        logger.info(f"="*80)
        
        # Update job status to processing
        job_storage[job_id] = {
            "id": job_id,
            "status": "processing",
            "progress": 0,
            "message": "Starting real web scraping and research...",
            "created_at": datetime.utcnow().isoformat(),
            "prompt": job_data.get("prompt", ""),
            "target_count": job_data.get("target_count", 10)
        }
        
        # Step 1: Extract targeting criteria from prompt
        job_storage[job_id].update({
            "progress": 10,
            "message": "Analyzing prompt and extracting targeting criteria..."
        })
        targeting_criteria = await extract_targeting_criteria(job_data.get("prompt", ""))
        logger.info(f"Job {job_id}: Extracted criteria: {targeting_criteria}")
        
        # Step 2: Search for companies using Google Custom Search
        job_storage[job_id].update({
            "progress": 25,
            "message": "Searching Google for relevant companies..."
        })
        
        logger.info(f"Job {job_id}: Real research available: {REAL_RESEARCH_AVAILABLE}")
        logger.info(f"Job {job_id}: Targeting criteria: {targeting_criteria}")
        logger.info(f"Job {job_id}: Target count: {job_data.get('target_count', 10)}")
        
        logger.info(f"Job {job_id}: 🔍 Calling search_companies() function...")
        try:
            companies = await search_companies(targeting_criteria, job_data.get("target_count", 10))
            logger.info(f"Job {job_id}: ✅ search_companies() returned {len(companies)} companies")
        except Exception as search_error:
            logger.error(f"Job {job_id}: ❌ search_companies() failed: {search_error}")
            import traceback
            logger.error(f"Job {job_id}: Traceback: {traceback.format_exc()}")
            companies = []
        
        if not companies:
            logger.warning(f"="*80)
            logger.warning(f"Job {job_id}: ⚠️ No companies found, falling back to simulation")
            logger.warning(f"Job {job_id}: This means Google Custom Search API is not working properly")
            google_key = os.getenv("GOOGLE_API_KEY")
            google_cse = os.getenv("GOOGLE_CSE_ID") or os.getenv("GOOGLE_SEARCH_ENGINE_ID")
            logger.warning(f"Job {job_id}: GOOGLE_API_KEY is {'SET (len={len(google_key)})' if google_key else 'NOT SET'}")
            logger.warning(f"Job {job_id}: GOOGLE_CSE_ID/GOOGLE_SEARCH_ENGINE_ID is {'SET (len={len(google_cse)})' if google_cse else 'NOT SET'}")
            if not google_key:
                logger.error(f"Job {job_id}: ❌ GOOGLE_API_KEY environment variable is missing!")
            if not google_cse:
                logger.error(f"Job {job_id}: ❌ GOOGLE_CSE_ID or GOOGLE_SEARCH_ENGINE_ID environment variable is missing!")
            
            # Check if real research module is loaded
            logger.warning(f"Job {job_id}: REAL_RESEARCH_AVAILABLE flag: {REAL_RESEARCH_AVAILABLE}")
            if not REAL_RESEARCH_AVAILABLE:
                logger.error(f"Job {job_id}: ❌ Real research module failed to load!")
                logger.error(f"Job {job_id}: Check if all dependencies are installed (aiohttp, openai, anthropic)")
            logger.warning(f"="*80)
            
            # Fallback to simulation if no companies found
            await _fallback_simulation(job_id, job_data)
            return
        
        # Step 3: Deep research on each company
        job_storage[job_id].update({
            "progress": 40,
            "message": f"Researching {len(companies)} companies in detail..."
        })
        
        researched_companies = []
        for i, company in enumerate(companies):
            try:
                # Update progress for each company
                progress = 40 + (i / len(companies)) * 30  # 40-70% for research
                job_storage[job_id].update({
                    "progress": int(progress),
                    "message": f"Researching {company.get('name', 'Unknown')}... ({i+1}/{len(companies)})"
                })
                
                # Deep research on company
                research_data = await research_company_deep(company)
                researched_companies.append(research_data)
                
                logger.info(f"Job {job_id}: Completed research for {company.get('name')}")
                
            except Exception as e:
                logger.error(f"Job {job_id}: Error researching {company.get('name')}: {e}")
                continue
        
        # Step 4: Find contacts for each company
        job_storage[job_id].update({
            "progress": 70,
            "message": "Finding contacts and decision makers..."
        })
        
        leads = []
        for i, company in enumerate(researched_companies):
            try:
                # Update progress for each company
                progress = 70 + (i / len(researched_companies)) * 15  # 70-85% for contacts
                job_storage[job_id].update({
                    "progress": int(progress),
                    "message": f"Finding contacts for {company.get('name', 'Unknown')}... ({i+1}/{len(researched_companies)})"
                })
                
                # Find contacts for this company
                company_contacts = await find_company_contacts(company)
                leads.extend(company_contacts)
                
                logger.info(f"Job {job_id}: Found {len(company_contacts)} contacts for {company.get('name')}")
                
            except Exception as e:
                logger.error(f"Job {job_id}: Error finding contacts for {company.get('name')}: {e}")
                continue
        
        # Step 5: Generate personalized outreach messages
        job_storage[job_id].update({
            "progress": 85,
            "message": "Generating personalized outreach messages..."
        })
        
        personalized_leads = []
        for i, lead in enumerate(leads):
            try:
                # Update progress for each lead
                progress = 85 + (i / len(leads)) * 10  # 85-95% for outreach
                job_storage[job_id].update({
                    "progress": int(progress),
                    "message": f"Generating outreach for {lead.get('contact_name', 'Unknown')}... ({i+1}/{len(leads)})"
                })
                
                # Generate personalized outreach
                outreach_messages = await generate_personalized_outreach(lead)
                lead.update(outreach_messages)
                personalized_leads.append(lead)
                
            except Exception as e:
                logger.error(f"Job {job_id}: Error generating outreach for {lead.get('contact_name')}: {e}")
                personalized_leads.append(lead)  # Add without outreach
        
        # Step 6: Finalize and export
        job_storage[job_id].update({
            "progress": 95,
            "message": "Finalizing results and preparing export..."
        })
        
        # Filter out existing leads if requested
        final_leads = personalized_leads
        if job_data.get("exclude_existing_leads", False) and job_data.get("existing_leads"):
            # Handle both list and dict formats for existing_leads
            existing_leads_data = job_data.get("existing_leads", [])
            existing_emails = set()
            
            for item in existing_leads_data:
                if isinstance(item, dict):
                    # If it's a dict, use .get()
                    email = item.get('email', '')
                    if email:
                        existing_emails.add(email.lower())
                elif isinstance(item, list) and len(item) > 0:
                    # If it's a list (raw sheet row), try to find email-like values
                    for value in item:
                        if isinstance(value, str) and '@' in value and '.' in value:
                            existing_emails.add(value.lower())
                            break
            
            logger.info(f"Job {job_id}: Found {len(existing_emails)} existing emails to exclude")
            final_leads = [lead for lead in personalized_leads if lead.get('email', '').lower() not in existing_emails]
            logger.info(f"Job {job_id}: Filtered out existing leads, {len(final_leads)} remaining")
        
        # Update job status to completed
        job_storage[job_id].update({
            "status": "completed",
            "progress": 100,
            "message": f"Job completed! Found {len(final_leads)} leads with personalized outreach.",
            "leads": final_leads,
            "completed_at": datetime.utcnow().isoformat()
        })
        
        logger.info(f"Job {job_id} completed successfully with {len(final_leads)} leads")
        
        # If Google Sheets is connected, try to export results
        if job_data.get("connected_sheet_id"):
            try:
                await export_to_google_sheets(job_id, final_leads, job_data)
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

async def _fallback_simulation(job_id: str, job_data: dict):
    """Fallback to simulation if real research fails"""
    logger.info(f"Job {job_id}: Using fallback simulation")
    logger.warning(f"Job {job_id}: REAL RESEARCH IS NOT WORKING - Using simulation mode")
    logger.warning(f"Job {job_id}: This means the system is not doing actual web scraping")
    logger.warning(f"Job {job_id}: Check API keys and dependencies for real research")
    
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
    
    # Generate mock leads
    target_count = job_data.get("target_count", 10)
    existing_leads = job_data.get("existing_leads", [])
    exclude_existing = job_data.get("exclude_existing_leads", False)
    
    # Parse existing leads to get emails (handle both dict and list formats)
    existing_emails = set()
    if exclude_existing and existing_leads:
        for item in existing_leads:
            if isinstance(item, dict):
                email = item.get('email', '')
                if email:
                    existing_emails.add(email.lower())
            elif isinstance(item, list) and len(item) > 0:
                # If it's a list, try to find email-like values
                for value in item:
                    if isinstance(value, str) and '@' in value and '.' in value:
                        existing_emails.add(value.lower())
                        break
    
    logger.info(f"Job {job_id}: Excluding {len(existing_emails)} existing emails from simulation")
    
    simulated_leads = []
    for i in range(min(target_count, 50)):
        company_name = f"Company {i+1}"
        email = f"contact{i+1}@company{i+1}.com"
        
        # Check if email already exists
        if email.lower() in existing_emails:
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
            "source": "AI Platform (Simulation)",
            "created_at": datetime.utcnow().isoformat(),
            "linkedin_message": "Hi! I'd love to connect and discuss how we can help your business grow.",
            "email_subject": "Partnership Opportunity",
            "email_body": "Hi there, I'd love to discuss a potential partnership opportunity."
        }
        simulated_leads.append(lead)
    
    job_storage[job_id].update({
        "status": "completed",
        "progress": 100,
        "message": f"Job completed! Found {len(simulated_leads)} leads (simulation mode).",
        "leads": simulated_leads,
        "completed_at": datetime.utcnow().isoformat()
    })

async def export_to_google_sheets(job_id: str, leads: list, job_data: dict):
    """Export leads to connected Google Sheet"""
    try:
        # This would integrate with the Google Sheets service
        logger.info(f"Exporting {len(leads)} leads to Google Sheets for job {job_id}")
        # Implementation would use the Google Sheets API
    except Exception as e:
        logger.error(f"Failed to export to Google Sheets: {e}")

logger.info("🔧 Creating FastAPI app...")
app = FastAPI(
    title="AI Lead Generation Platform",
    description="Automated lead discovery, research, and outreach generation",
    version="2.0.0"
)
logger.info("✅ FastAPI app created successfully")

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
    logger.info("OAuth routes enabled")
else:
    logger.warning("OAuth routes disabled - missing dependencies")

if SHEETS_ROUTES_AVAILABLE:
    app.include_router(google_sheets_router)
    logger.info("Google Sheets routes enabled")
else:
    logger.warning("Google Sheets routes disabled - missing dependencies")
# app.include_router(makecom_router)
# app.include_router(ai_chat_router)

# Mount static files (React app)
if os.path.exists("/app/frontend/dist"):
    app.mount("/assets", StaticFiles(directory="/app/frontend/dist/assets"), name="assets")
    app.mount("/static", StaticFiles(directory="/app/frontend/dist"), name="static")

from fastapi.responses import RedirectResponse

@app.get("/")
async def root():
    """Root endpoint: redirect to UI. Health remains at /health-check."""
    return RedirectResponse(url="/app", status_code=307)

@app.get("/app")
async def serve_react_app_root():
    """Serve the React app"""
    try:
        if os.path.exists("/app/frontend/dist/index.html"):
            return FileResponse("/app/frontend/dist/index.html")
        else:
            return {"error": "Frontend not found"}
    except Exception as e:
        logger.error(f"React app error: {e}")
        return {"error": str(e)}

@app.get("/app/{path:path}")
async def serve_react_app_paths(path: str):
    """Serve React app for any /app/* client routes"""
    try:
        if os.path.exists("/app/frontend/dist/index.html"):
            return FileResponse("/app/frontend/dist/index.html")
        else:
            return {"error": "Frontend not found"}
    except Exception as e:
        logger.error(f"React app error: {e}")
        return {"error": str(e)}

@app.get("/ping")
async def ping():
    """Simple ping endpoint for health checks"""
    return {"status": "ok", "message": "pong"}

@app.get("/healthz")
async def healthz():
    """Ultra-simple health endpoint that returns plain text"""
    return "OK"

@app.get("/health-check")
async def health_check_simple():
    """Simple health check endpoint for Railway"""
    # Ultra-simple response for Railway health check
    return {"status": "ok", "health": "healthy"}

@app.get("/api")
async def api_info():
    """API info endpoint"""
    google_api_key = os.getenv("GOOGLE_API_KEY")
    google_cse_id = os.getenv("GOOGLE_CSE_ID") or os.getenv("GOOGLE_SEARCH_ENGINE_ID")
    openai_key = os.getenv("OPENAI_API_KEY")
    claude_key = os.getenv("CLAUDE_API_KEY")
    
    return {
        "message": "AI Lead Generation Platform API", 
        "version": "2.0.0",
        "status": "running",
        "real_research_available": REAL_RESEARCH_AVAILABLE,
        "oauth_routes_available": OAUTH_ROUTES_AVAILABLE,
        "sheets_routes_available": SHEETS_ROUTES_AVAILABLE,
        "google_api_key": "SET" if google_api_key else "NOT SET",
        "google_cse_id": "SET" if google_cse_id else "NOT SET",
        "openai_key": "SET" if openai_key else "NOT SET",
        "claude_key": "SET" if claude_key else "NOT SET",
        "warning": "Web crawling requires GOOGLE_API_KEY and GOOGLE_CSE_ID (or GOOGLE_SEARCH_ENGINE_ID) to be set" if not (google_api_key and google_cse_id) else None
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        return {
            "status": "healthy", 
            "timestamp": datetime.utcnow().isoformat(),
            "service": "AI Lead Generation Platform",
            "real_research_available": REAL_RESEARCH_AVAILABLE,
            "oauth_routes_available": OAUTH_ROUTES_AVAILABLE,
            "sheets_routes_available": SHEETS_ROUTES_AVAILABLE
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@app.get("/debug/google-search")
async def debug_google_search(q: str, n: int = 5):
    """Debug endpoint to verify Google Custom Search live from the backend."""
    try:
        logger.info(f"🔍 Debug Google Search: q='{q}', n={n}")
        criteria = {"keywords": q.split(), "industry": ""}
        # Call the same search used by jobs
        results = await search_companies(criteria, n)
        logger.info(f"🔍 Debug Google Search returned {len(results)} results")
        return {
            "success": True,
            "count": len(results),
            "keys": {
                "google_api_key": "SET" if os.getenv("GOOGLE_API_KEY") else "NOT SET",
                "google_cse_id": "SET" if os.getenv("GOOGLE_CSE_ID") else "NOT SET",
            },
            "sample": results[: min(3, len(results))]
        }
    except Exception as e:
        logger.error(f"❌ Debug Google Search error: {e}")
        return {"success": False, "error": str(e)}

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
        
        logger.info(f"✅ Stored job {job_id} in job_storage")
        logger.info(f"✅ Job storage now contains: {list(job_storage.keys())}")
        logger.info(f"✅ Job data: {job_storage[job_id]}")
        
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
        logger.info(f"🔍 Getting job status for job_id: {job_id}")
        logger.info(f"🔍 Available jobs in storage: {list(job_storage.keys())}")
        logger.info(f"🔍 Total jobs in storage: {len(job_storage)}")
        
        if job_id in job_storage:
            job_data = job_storage[job_id]
            logger.info(f"✅ Found job {job_id}: {job_data.get('status', 'unknown')}")
            logger.info(f"✅ Job data: {job_data}")
            return job_data
        else:
            logger.warning(f"❌ Job {job_id} not found in storage")
            logger.warning(f"❌ Available job IDs: {list(job_storage.keys())}")
            return {
                "id": job_id,
                "status": "not_found",
                "message": "Job not found"
            }
    except Exception as e:
        logger.error(f"❌ Error getting job {job_id}: {str(e)}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
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
        "environment": "production",
        "real_research_available": REAL_RESEARCH_AVAILABLE,
        "oauth_routes_available": OAUTH_ROUTES_AVAILABLE,
        "sheets_routes_available": SHEETS_ROUTES_AVAILABLE
    }

# Remove global catch-all to avoid intercepting health checks and API

if __name__ == "__main__":
    logger.info("🚀 Starting AI Lead Generation Platform")
    logger.info(f"🔧 Real research available: {REAL_RESEARCH_AVAILABLE}")
    logger.info(f"🔧 OAuth routes available: {OAUTH_ROUTES_AVAILABLE}")
    logger.info(f"🔧 Google Sheets routes available: {SHEETS_ROUTES_AVAILABLE}")
    logger.info(f"🔧 Total routes: {len(app.routes)}")
    logger.info(f"🔧 Route paths: {[route.path for route in app.routes if hasattr(route, 'path')]}")
    logger.info("✅ App configuration complete!")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

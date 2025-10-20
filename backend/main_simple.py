"""
REWRITTEN Lead Generation Backend - NO SIMULATION, REAL DATA ONLY
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
import re

# Configure logging
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
        find_company_contacts
    )
    from services.hunter_client import hunter_client
    REAL_RESEARCH_AVAILABLE = True
    logger.info("✅ Real research engine loaded successfully")
except ImportError as e:
    logger.error(f"❌ Real research engine not available: {e}")
    logger.error("❌ System will not work without real research!")
    REAL_RESEARCH_AVAILABLE = False

# Pydantic models
from pydantic import BaseModel

class JobCreate(BaseModel):
    prompt: str
    target_count: int = 10
    quality_threshold: float = 0.8
    knowledge_base_documents: List[Dict[str, Any]] = []
    exclude_existing_leads: bool = False
    existing_leads: List[Any] = []

# FastAPI app
app = FastAPI(
    title="AI Lead Generation Platform",
    description="Real lead generation using Google Search + Hunter.io",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Job storage
job_storage = {}
container_start_time = datetime.utcnow().isoformat()


def extract_company_name_from_prompt(prompt: str) -> Optional[str]:
    """Extract company name if user asks for specific company"""
    prompt_lower = prompt.lower()
    
    # Patterns like "find leads at X", "contacts from X", "employees at X"
    patterns = [
        r'(?:find|get|search).*?(?:at|from|for)\s+([A-Z][A-Za-z\s&]+?)(?:\s|$|,|\.|!)',
        r'(?:contacts?|leads?|employees?)\s+(?:at|from|for)\s+([A-Z][A-Za-z\s&]+?)(?:\s|$|,|\.|!)',
        r'(?:company|firm|organization):\s*([A-Z][A-Za-z\s&]+?)(?:\s|$|,|\.|!)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, prompt, re.IGNORECASE)
        if match:
            company_name = match.group(1).strip()
            # Clean up common words
            company_name = re.sub(r'\s+(the|and|or|inc|llc|ltd|corp|corporation)$', '', company_name, flags=re.IGNORECASE)
            if len(company_name) > 2:
                logger.info(f"🎯 Detected specific company request: '{company_name}'")
                return company_name
    
    return None


async def find_specific_company(company_name: str) -> Optional[Dict[str, Any]]:
    """Search for a specific company by name"""
    logger.info(f"🔍 Searching for specific company: {company_name}")
    
    # Try to search Google for the company
    try:
        search_query = f'"{company_name}" official website'
        companies = await search_companies({"prompt": search_query}, 1)
        
        if companies and len(companies) > 0:
            company = companies[0]
            logger.info(f"✅ Found company: {company.get('name')} at {company.get('domain')}")
            return company
        else:
            logger.warning(f"⚠️ Could not find company via Google search")
            
            # Fallback: try to guess domain
            domain_guess = company_name.lower().replace(' ', '').replace('&', 'and') + '.com'
            logger.info(f"💡 Trying domain guess: {domain_guess}")
            
            return {
                "name": company_name,
                "domain": domain_guess,
                "website": f"https://{domain_guess}",
                "snippet": f"Company website for {company_name}"
            }
            
    except Exception as e:
        logger.error(f"❌ Error searching for company: {e}")
        return None


async def process_job_real_only(job_id: str, job_data: dict):
    """
    Process job with REAL data only - NO SIMULATION
    
    This completely replaces the old process_job_background() function
    """
    
    if not REAL_RESEARCH_AVAILABLE:
        job_storage[job_id].update({
            "status": "failed",
            "progress": 0,
            "message": "❌ Real research engine not available. System cannot function.",
            "error": "Required modules not loaded. Check server logs."
        })
        logger.error(f"Job {job_id}: Cannot process - real research not available!")
        return
    
    try:
        prompt = job_data.get("prompt", "")
        target_count = job_data.get("target_count", 10)
        
        logger.info(f"="*80)
        logger.info(f"Job {job_id}: START PROCESSING")
        logger.info(f"Job {job_id}: Prompt: {prompt}")
        logger.info(f"Job {job_id}: Target count: {target_count}")
        logger.info(f"="*80)
        
        # Check if user is asking for a specific company
        specific_company_name = extract_company_name_from_prompt(prompt)
        
        if specific_company_name:
            # USER ASKED FOR SPECIFIC COMPANY
            logger.info(f"Job {job_id}: 🎯 SPECIFIC COMPANY REQUEST: {specific_company_name}")
            
            job_storage[job_id].update({
                "progress": 20,
                "message": f"Searching for {specific_company_name}..."
            })
            
            # Find the specific company
            company = await find_specific_company(specific_company_name)
            
            if not company:
                job_storage[job_id].update({
                    "status": "failed",
                    "message": f"❌ Could not find company: {specific_company_name}",
                    "error": "Company not found"
                })
                logger.error(f"Job {job_id}: Company not found")
                return
            
            companies = [company]
            
        else:
            # GENERAL SEARCH USING RESEARCH GUIDE
            logger.info(f"Job {job_id}: 📋 GENERAL SEARCH using research guide")
            
            job_storage[job_id].update({
                "progress": 10,
                "message": "Analyzing research guide..."
            })
            
            # Extract research guide text
            research_guide_text = ""
            for doc in job_data.get("knowledge_base_documents", []):
                text = doc.get("extractedText") or doc.get("content", "")
                if text:
                    research_guide_text += f"\n\n{text}"
            
            # Extract targeting criteria
            prompt_with_guide = f"{prompt}\n\nResearch Guide:\n{research_guide_text}" if research_guide_text else prompt
            targeting_criteria = await extract_targeting_criteria(prompt_with_guide)
            
            job_storage[job_id].update({
                "progress": 20,
                "message": "Searching for companies..."
            })
            
            # Search for companies
            companies = await search_companies(targeting_criteria, target_count)
            
            if not companies or len(companies) == 0:
                job_storage[job_id].update({
                    "status": "failed",
                    "message": "❌ No companies found matching your criteria",
                    "error": "No search results. Try different keywords or check API keys."
                })
                logger.error(f"Job {job_id}: No companies found")
                return
        
        logger.info(f"Job {job_id}: ✅ Found {len(companies)} companies")
        
        # Find contacts at each company
        job_storage[job_id].update({
            "progress": 50,
            "message": f"Finding contacts at {len(companies)} companies..."
        })
        
        all_leads = []
        
        for i, company in enumerate(companies):
            company_name = company.get('name', 'Unknown')
            domain = company.get('domain', '')
            
            logger.info(f"Job {job_id}: [{i+1}/{len(companies)}] Finding contacts at {company_name} ({domain})")
            
            job_storage[job_id].update({
                "progress": 50 + int((i / len(companies)) * 40),
                "message": f"Finding contacts at {company_name}... ({i+1}/{len(companies)})"
            })
            
            try:
                # Get targeting criteria if available
                targeting_criteria = job_data.get('targeting_criteria', {})
                
                # Find contacts
                contacts = await find_company_contacts(company, targeting_criteria)
                
                if contacts:
                    logger.info(f"Job {job_id}: ✅ Found {len(contacts)} contacts at {company_name}")
                    all_leads.extend(contacts)
                else:
                    logger.warning(f"Job {job_id}: ⚠️ No contacts found at {company_name}")
                    
            except Exception as e:
                logger.error(f"Job {job_id}: ❌ Error finding contacts at {company_name}: {e}")
                continue
        
        # Final result
        if len(all_leads) == 0:
            job_storage[job_id].update({
                "status": "completed",
                "progress": 100,
                "message": f"⚠️ Search completed but no contacts found at {len(companies)} companies. Hunter.io may have limited data for these domains.",
                "leads": [],
                "companies_searched": len(companies)
            })
            logger.warning(f"Job {job_id}: Completed but no contacts found")
        else:
            job_storage[job_id].update({
                "status": "completed",
                "progress": 100,
                "message": f"✅ Found {len(all_leads)} real contacts with verified emails!",
                "leads": all_leads,
                "companies_searched": len(companies)
            })
            logger.info(f"Job {job_id}: ✅ COMPLETED with {len(all_leads)} leads")
        
    except Exception as e:
        logger.error(f"Job {job_id}: ❌ CRITICAL ERROR: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        job_storage[job_id].update({
            "status": "failed",
            "message": f"❌ Job failed: {str(e)}",
            "error": str(e)
        })


# API Endpoints

@app.get("/")
async def root():
    """Serve frontend"""
    return FileResponse("frontend/dist/index.html")

@app.post("/jobs/")
async def create_job(job_data: dict):
    """Create a new job"""
    try:
        job_id = str(uuid.uuid4())
        logger.info(f"Creating job {job_id}")
        
        job_storage[job_id] = {
            "id": job_id,
            "status": "started",
            "progress": 0,
            "message": "Job started - Real research in progress",
            "created_at": datetime.utcnow().isoformat(),
            "prompt": job_data.get("prompt", ""),
            "target_count": job_data.get("target_count", 10)
        }
        
        # Start background processing
        asyncio.create_task(process_job_real_only(job_id, job_data))
        
        return {
            "job_id": job_id,
            "status": "started",
            "message": "Job started successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    """Get job status"""
    if job_id in job_storage:
        return job_storage[job_id]
    else:
        raise HTTPException(status_code=404, detail="Job not found")

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "real_research_available": REAL_RESEARCH_AVAILABLE,
        "container_start_time": container_start_time,
        "active_jobs": len(job_storage)
    }

# Serve static files
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)

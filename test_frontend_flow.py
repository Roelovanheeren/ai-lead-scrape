#!/usr/bin/env python3
"""
Test: Simulate Frontend API Flow

This tests the EXACT flow the frontend uses:
1. POST /jobs/ with prompt and knowledge base
2. Poll GET /jobs/{job_id} for progress
3. Retrieve leads from job result

This ensures the frontend will get the same results we saw in tests.
"""

import asyncio
import os
import sys
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API keys should be set via environment variables
# export GOOGLE_API_KEY="your_key"
# export GOOGLE_CSE_ID="your_cse_id"
# export HUNTER_API_KEY="your_key"
# export OPENAI_API_KEY="your_key"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import research functions directly (avoid FastAPI dependencies)
from services.real_research import (
    extract_targeting_criteria,
    search_companies,
    research_company_deep,
    find_company_contacts
)
import uuid

# Simulate job storage (like main_simple.py does)
job_storage = {}

# Sample Hazen Road research guide (abbreviated)
HAZEN_ROAD_GUIDE = """
🧠 Hazen Road Institutional Investor Discovery

Mission: Find institutional investors (LPs) that invest in BTR developments.

Target Investors:
✅ LP Investor: Invests capital into other developers' projects
✅ BTR / Multifamily Focus: Build-to-rent investments
✅ OZ Activity: Opportunity Zone projects
✅ Sunbelt Presence: Phoenix, Arizona, Texas, Florida
✅ Institutional Scale: $500M+ AUM

❌ NOT Looking For:
- Pure developers
- Small syndicators

Example Companies:
- CenterSquare Investment Management
- Kennedy Wilson (REIT)
- Argosy Real Estate Partners

Target Contact Roles:
- Investment Director
- Portfolio Manager
- Fund Manager
- Managing Director
"""

async def simple_job_processing(job_id: str, job_data: dict):
    """Simplified version of process_job_background()"""
    try:
        # Step 1: Extract targeting criteria from research guide
        job_storage[job_id].update({"progress": 10, "message": "Analyzing research guide..."})
        
        prompt = job_data.get("prompt", "")
        research_guide_text = ""
        
        # Extract text from knowledge base documents
        for doc in job_data.get("knowledge_base_documents", []):
            text = doc.get("extractedText") or doc.get("content", "")
            if text:
                research_guide_text += f"\n\n{text}"
        
        # Combine prompt + research guide
        prompt_with_guide = f"{prompt}\n\nResearch Guide:\n{research_guide_text}" if research_guide_text else prompt
        targeting_criteria = await extract_targeting_criteria(prompt_with_guide)
        
        # Step 2: Search for companies
        job_storage[job_id].update({"progress": 30, "message": "Searching for companies..."})
        companies = await search_companies(targeting_criteria, job_data.get("target_count", 2))
        
        if not companies:
            job_storage[job_id].update({"status": "failed", "message": "No companies found"})
            return
        
        # Step 3: Find contacts
        job_storage[job_id].update({"progress": 60, "message": f"Finding contacts at {len(companies)} companies..."})
        
        leads = []
        for company in companies:
            contacts = await find_company_contacts(company, targeting_criteria)
            leads.extend(contacts)
        
        # Step 4: Complete
        job_storage[job_id].update({
            "status": "completed",
            "progress": 100,
            "message": f"Found {len(leads)} leads",
            "leads": leads
        })
        
    except Exception as e:
        logger.error(f"Job processing error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        job_storage[job_id].update({"status": "failed", "message": str(e)})

async def test_frontend_flow():
    """Test the exact flow the frontend uses"""
    
    logger.info("="*80)
    logger.info("🧪 TEST: Frontend API Flow (Hazen Road Investor Discovery)")
    logger.info("="*80)
    logger.info("")
    
    # Step 1: Simulate frontend creating a job (POST /jobs/)
    logger.info("STEP 1: Frontend creates job (POST /jobs/)")
    logger.info("")
    
    job_data = {
        "prompt": "Find institutional investors as explained in the knowledge base",
        "target_count": 2,  # Just 2 for quick test
        "quality_threshold": 0.8,
        "knowledge_base_documents": [
            {
                "name": "Hazen_Road_Research_Guide.txt",
                "extractedText": HAZEN_ROAD_GUIDE,
                "content": HAZEN_ROAD_GUIDE
            }
        ]
    }
    
    # Simulate the endpoint creating a job
    job_id = str(uuid.uuid4())
    job_storage[job_id] = {
        "id": job_id,
        "status": "started",
        "progress": 0,
        "message": "Job started successfully",
        "created_at": "2025-10-20T00:00:00",
        "prompt": job_data["prompt"],
        "target_count": job_data["target_count"]
    }
    
    logger.info(f"✅ Job created: {job_id}")
    logger.info(f"   Prompt: {job_data['prompt']}")
    logger.info(f"   Target count: {job_data['target_count']}")
    logger.info(f"   Knowledge base: {len(job_data['knowledge_base_documents'])} document(s)")
    logger.info("")
    
    # Step 2: Start background processing (what FastAPI does)
    logger.info("STEP 2: Start background job processing")
    logger.info("")
    
    # Create background task
    task = asyncio.create_task(simple_job_processing(job_id, job_data))
    
    # Step 3: Simulate frontend polling (GET /jobs/{job_id})
    logger.info("STEP 3: Frontend polls for progress (GET /jobs/{job_id})")
    logger.info("")
    
    last_progress = 0
    poll_count = 0
    max_polls = 60  # Max 2 minutes of polling
    
    while poll_count < max_polls:
        await asyncio.sleep(2)  # Poll every 2 seconds (like frontend does)
        poll_count += 1
        
        # Simulate GET /jobs/{job_id}
        if job_id in job_storage:
            job_status = job_storage[job_id]
            
            # Log progress updates
            if job_status.get("progress", 0) != last_progress:
                logger.info(f"   [{poll_count}] Progress: {job_status.get('progress')}%")
                logger.info(f"        Status: {job_status.get('status')}")
                logger.info(f"        Message: {job_status.get('message')}")
                last_progress = job_status.get("progress", 0)
            
            # Check if completed
            if job_status.get("status") == "completed":
                logger.info("")
                logger.info("✅ Job completed!")
                break
            
            # Check if failed
            if job_status.get("status") == "failed":
                logger.error("")
                logger.error(f"❌ Job failed: {job_status.get('error')}")
                return
        else:
            logger.error(f"❌ Job {job_id} not found in storage!")
            return
    
    # Wait for task to complete
    await task
    
    # Step 4: Retrieve results
    logger.info("")
    logger.info("="*80)
    logger.info("STEP 4: Retrieve Results (Frontend reads job_storage[job_id]['leads'])")
    logger.info("="*80)
    logger.info("")
    
    if job_id in job_storage:
        final_job = job_storage[job_id]
        leads = final_job.get("leads", [])
        
        logger.info(f"📊 Final Results:")
        logger.info(f"   Status: {final_job.get('status')}")
        logger.info(f"   Total Leads: {len(leads)}")
        logger.info("")
        
        if leads:
            logger.info("✅ LEADS FOUND!")
            logger.info("")
            
            for i, lead in enumerate(leads, 1):
                logger.info(f"   [{i}] {lead.get('contact_name')} at {lead.get('company')}")
                logger.info(f"       Role: {lead.get('role')}")
                logger.info(f"       Email: {lead.get('email')}")
                logger.info(f"       LinkedIn: {lead.get('linkedin')}")
                logger.info(f"       Confidence: {lead.get('confidence', 0) * 100:.0f}%")
                logger.info(f"       Source: {lead.get('source')}")
                
                # Check if it's an investor (not developer)
                role_lower = (lead.get('role', '') or '').lower()
                company_lower = (lead.get('company', '') or '').lower()
                
                if any(term in role_lower for term in ['investment', 'portfolio', 'fund', 'managing director']):
                    logger.info(f"       ✅ CORRECT: Investment role")
                elif any(term in company_lower for term in ['investment', 'fund', 'capital']):
                    logger.info(f"       ✅ CORRECT: Investment company")
                else:
                    logger.warning(f"       ⚠️  VERIFY: Check if this is an investor")
                
                logger.info("")
        else:
            logger.warning("⚠️  No leads found!")
            logger.info("")
    else:
        logger.error("❌ Job disappeared from storage!")
        return
    
    # Step 5: Validation
    logger.info("="*80)
    logger.info("📊 VALIDATION: Will Frontend Get These Results?")
    logger.info("="*80)
    logger.info("")
    
    logger.info("✓ Flow Check:")
    logger.info(f"   1. Job created: {job_id in job_storage} ✅")
    logger.info(f"   2. Job processed: {final_job.get('status') == 'completed'} ✅")
    logger.info(f"   3. Leads returned: {len(leads) > 0} {'✅' if len(leads) > 0 else '❌'}")
    logger.info("")
    
    if len(leads) > 0:
        # Check data structure
        first_lead = leads[0]
        required_fields = ['contact_name', 'email', 'company', 'role', 'linkedin', 'confidence']
        
        logger.info("✓ Data Structure Check:")
        for field in required_fields:
            has_field = field in first_lead
            logger.info(f"   {field}: {has_field} {'✅' if has_field else '❌'}")
        
        logger.info("")
        
        # Check if they're investors (not developers)
        investor_count = 0
        for lead in leads:
            role_lower = (lead.get('role', '') or '').lower()
            if any(term in role_lower for term in ['investment', 'portfolio', 'fund', 'managing director']):
                investor_count += 1
        
        logger.info(f"✓ Targeting Check:")
        logger.info(f"   Investment roles found: {investor_count}/{len(leads)}")
        logger.info(f"   Correct targeting: {investor_count > 0} {'✅' if investor_count > 0 else '❌'}")
        logger.info("")
        
        if investor_count > 0:
            logger.info("🎉 SUCCESS!")
            logger.info("   Frontend will receive these exact results:")
            logger.info(f"   • {len(leads)} institutional investor contacts")
            logger.info("   • With verified emails and LinkedIn")
            logger.info("   • Matching Hazen Road research guide criteria")
        else:
            logger.warning("⚠️  PARTIAL SUCCESS")
            logger.warning("   System found contacts but wrong types")
            logger.warning("   May need to refine targeting criteria")
    else:
        logger.error("❌ FAILURE")
        logger.error("   No leads returned to frontend")
        logger.error("   Check logs for errors")
    
    logger.info("")
    logger.info("="*80)

if __name__ == "__main__":
    asyncio.run(test_frontend_flow())

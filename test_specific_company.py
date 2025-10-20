#!/usr/bin/env python3
"""
Test: Specific Company Request

Tests the new "find leads at CenterSquare" functionality
"""

import asyncio
import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import the new main module
from main_simple import process_job_real_only, job_storage, extract_company_name_from_prompt
import uuid

async def test_specific_company():
    """Test asking for a specific company"""
    
    logger.info("="*80)
    logger.info("🧪 TEST: Specific Company Request (CenterSquare)")
    logger.info("="*80)
    logger.info("")
    
    # Test company name extraction
    test_prompts = [
        "Find leads at CenterSquare",
        "Get contacts from CenterSquare Investment Management",
        "Find employees at CenterSquare",
        "I need leads for CenterSquare"
    ]
    
    logger.info("STEP 1: Test Company Name Extraction")
    logger.info("")
    
    for prompt in test_prompts:
        extracted = extract_company_name_from_prompt(prompt)
        logger.info(f"   Prompt: '{prompt}'")
        logger.info(f"   Extracted: '{extracted}'")
        logger.info("")
    
    # Test actual job processing
    logger.info("="*80)
    logger.info("STEP 2: Process Job for CenterSquare")
    logger.info("="*80)
    logger.info("")
    
    job_data = {
        "prompt": "Find leads at CenterSquare Investment Management",
        "target_count": 10
    }
    
    job_id = str(uuid.uuid4())
    job_storage[job_id] = {
        "id": job_id,
        "status": "started",
        "progress": 0,
        "message": "Starting...",
        "prompt": job_data["prompt"]
    }
    
    # Process job
    await process_job_real_only(job_id, job_data)
    
    # Check results
    result = job_storage[job_id]
    
    logger.info("")
    logger.info("="*80)
    logger.info("📊 RESULTS")
    logger.info("="*80)
    logger.info("")
    logger.info(f"   Status: {result.get('status')}")
    logger.info(f"   Message: {result.get('message')}")
    logger.info(f"   Leads Found: {len(result.get('leads', []))}")
    logger.info("")
    
    leads = result.get('leads', [])
    if leads:
        logger.info("✅ SUCCESS! Found contacts:")
        logger.info("")
        for i, lead in enumerate(leads[:5], 1):
            logger.info(f"   [{i}] {lead.get('contact_name')}")
            logger.info(f"       Role: {lead.get('role')}")
            logger.info(f"       Email: {lead.get('email')}")
            logger.info(f"       Company: {lead.get('company')}")
            logger.info(f"       Confidence: {lead.get('confidence', 0) * 100:.0f}%")
            logger.info("")
    else:
        logger.warning("⚠️ No leads found")
        logger.info(f"   This means Hunter.io has no data for this domain")
    
    logger.info("="*80)

if __name__ == "__main__":
    asyncio.run(test_specific_company())

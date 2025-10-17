#!/usr/bin/env python3
"""
End-to-End Test: Full Lead Generation Flow
Tests if Google Search → Company Finding → Contact Finding actually works
"""

import os
import sys
import asyncio
import logging

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Set environment variables
os.environ['GOOGLE_API_KEY'] = 'AIzaSyBBhkKvctGs4ivVaquySztFmKXa7oQ3fjg'
os.environ['GOOGLE_CSE_ID'] = '404c0e0620566459a'
os.environ['HUNTER_API_KEY'] = '6017450d6d5a86d778f26bdd547ae883cf0e1280'

from services.real_research import (
    extract_targeting_criteria,
    search_companies,
    find_company_contacts
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_full_flow():
    """Test complete flow from prompt to contacts"""
    
    logger.info("=" * 80)
    logger.info("🧪 FULL END-TO-END LEAD GENERATION TEST")
    logger.info("=" * 80)
    logger.info("")
    
    # Test prompt for real estate development
    test_prompt = """
    Find real estate development companies that are actively developing 
    commercial or residential properties. Target VP of Development, 
    Project Managers, and Development Directors.
    """
    
    logger.info("📋 Test Prompt:")
    logger.info(test_prompt)
    logger.info("")
    
    # Step 1: Extract targeting criteria
    logger.info("=" * 80)
    logger.info("STEP 1: Extract Targeting Criteria")
    logger.info("=" * 80)
    
    criteria = await extract_targeting_criteria(test_prompt)
    logger.info(f"✅ Extracted criteria:")
    logger.info(f"   Industry: {criteria.get('industry')}")
    logger.info(f"   Keywords: {criteria.get('keywords')}")
    logger.info(f"   Target Roles: {criteria.get('target_roles', 'None specified')}")
    logger.info(f"   Search Queries: {criteria.get('search_queries', [])[:3]}")
    logger.info("")
    
    # Step 2: Search for companies
    logger.info("=" * 80)
    logger.info("STEP 2: Search for Companies (Google Custom Search)")
    logger.info("=" * 80)
    
    companies = await search_companies(criteria, target_count=3)
    
    if not companies:
        logger.error("❌ NO COMPANIES FOUND!")
        logger.error("Google Search is not returning any results!")
        logger.error("")
        logger.error("Possible issues:")
        logger.error("1. Google API quota exceeded")
        logger.error("2. CSE not configured to search entire web")
        logger.error("3. Search queries not matching any results")
        logger.error("4. Network/API connection issue")
        return False
    
    logger.info(f"✅ Found {len(companies)} companies:")
    for i, company in enumerate(companies, 1):
        logger.info(f"   [{i}] {company.get('name')}")
        logger.info(f"       Domain: {company.get('domain')}")
        logger.info(f"       Website: {company.get('website')}")
        logger.info(f"       Description: {company.get('description', '')[:100]}...")
    logger.info("")
    
    # Step 3: Find contacts for first company
    logger.info("=" * 80)
    logger.info("STEP 3: Find Contacts (Hunter.io)")
    logger.info("=" * 80)
    
    first_company = companies[0]
    logger.info(f"Finding contacts for: {first_company.get('name')}")
    logger.info(f"Domain: {first_company.get('domain')}")
    logger.info("")
    
    contacts = await find_company_contacts(first_company, criteria)
    
    if not contacts:
        logger.error("❌ NO CONTACTS FOUND!")
        logger.error(f"Hunter.io found no one at {first_company.get('domain')}")
        logger.error("")
        logger.error("Possible issues:")
        logger.error("1. Domain doesn't have publicly listed contacts")
        logger.error("2. Hunter.io quota exceeded")
        logger.error("3. Domain extraction failed")
        return False
    
    logger.info(f"✅ Found {len(contacts)} contacts:")
    for i, contact in enumerate(contacts, 1):
        logger.info(f"   [{i}] {contact.get('contact_name')}")
        logger.info(f"       Email: {contact.get('email')}")
        logger.info(f"       Role: {contact.get('role')}")
        logger.info(f"       LinkedIn: {contact.get('linkedin', 'N/A')}")
        logger.info(f"       Confidence: {contact.get('confidence', 0):.2%}")
    logger.info("")
    
    # Summary
    logger.info("=" * 80)
    logger.info("📊 TEST RESULTS SUMMARY")
    logger.info("=" * 80)
    logger.info(f"✅ Extracted targeting criteria: {len(criteria)} fields")
    logger.info(f"✅ Found companies: {len(companies)}")
    logger.info(f"✅ Found contacts: {len(contacts)}")
    logger.info("")
    
    logger.info("🎉 FULL FLOW TEST PASSED!")
    logger.info("")
    logger.info("Sample Lead Data:")
    logger.info("-" * 80)
    sample_lead = contacts[0]
    logger.info(f"Company: {sample_lead.get('company')}")
    logger.info(f"Contact: {sample_lead.get('contact_name')}")
    logger.info(f"Email: {sample_lead.get('email')}")
    logger.info(f"Role: {sample_lead.get('role')}")
    logger.info(f"Website: {sample_lead.get('website')}")
    logger.info(f"LinkedIn: {sample_lead.get('linkedin')}")
    logger.info("")
    
    return True


if __name__ == "__main__":
    try:
        result = asyncio.run(test_full_flow())
        if result:
            logger.info("✅ All systems working - ready for production!")
            sys.exit(0)
        else:
            logger.error("❌ Test failed - fix issues above")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

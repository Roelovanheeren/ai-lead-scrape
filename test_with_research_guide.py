#!/usr/bin/env python3
"""
Test: Extract Targeting Criteria from Research Guide
Tests if AI properly reads and understands research documents
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
# You need to add your real OpenAI key here!
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', 'sk-placeholder')

from services.real_research import extract_targeting_criteria, search_companies

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_research_guide():
    """Test targeting extraction with research guide"""
    
    logger.info("=" * 80)
    logger.info("🧪 TEST: Research Guide Understanding")
    logger.info("=" * 80)
    logger.info("")
    
    # Simulate research guide (this is what would be in your uploaded PDF)
    research_guide = """
    === Lead Generation Research Guide ===
    
    TARGET MARKET:
    Real estate development companies and real estate investment firms that are 
    actively developing commercial properties, residential properties, or mixed-use 
    developments.
    
    COMPANY CRITERIA:
    - Industry: Real Estate Development, Real Estate Investment
    - Company Size: 50-500 employees
    - Geographic Focus: United States (primarily major metros)
    - Activity Level: Actively developing new projects
    
    TARGET CONTACTS:
    We need to reach decision-makers who oversee development projects:
    - VP of Development
    - Vice President of Development  
    - Senior Vice President of Development
    - Director of Development
    - Development Manager
    - Project Manager
    - Head of Acquisitions
    
    WHAT TO AVOID:
    - Real estate brokerages (residential sales)
    - Property management companies (unless they also develop)
    - REITs that only own/manage properties (not active development)
    
    IDEAL COMPANIES:
    Companies like:
    - Related Companies
    - Hillwood (Perot Company)
    - Toll Brothers
    - Lennar
    - PulteGroup
    - Hines
    - Trammell Crow Company
    - Greystar
    """
    
    # User's simple prompt
    user_prompt = "Generate leads as explained in the knowledge base"
    
    # Combine them (this is what the backend does)
    full_prompt = f"{user_prompt}\n\nResearch Guide Documents:\n{research_guide}"
    
    logger.info("📋 User Prompt:")
    logger.info(f"   {user_prompt}")
    logger.info("")
    
    logger.info("📚 Research Guide Preview (first 300 chars):")
    logger.info(f"   {research_guide[:300]}...")
    logger.info("")
    
    # Test: Extract targeting criteria
    logger.info("=" * 80)
    logger.info("STEP 1: Extract Targeting Criteria with AI")
    logger.info("=" * 80)
    
    criteria = await extract_targeting_criteria(full_prompt)
    
    logger.info("")
    logger.info("✅ AI Extracted:")
    logger.info(f"   Industry: {criteria.get('industry')}")
    logger.info(f"   Location: {criteria.get('location')}")
    logger.info(f"   Company Size: {criteria.get('company_size')}")
    logger.info(f"   Keywords: {criteria.get('keywords', [])[:10]}")
    logger.info(f"   Target Roles: {criteria.get('target_roles', [])}")
    logger.info(f"   Target Department: {criteria.get('target_department')}")
    logger.info("")
    
    logger.info("📊 Search Queries AI Generated:")
    search_queries = criteria.get('search_queries', [])
    if search_queries:
        for i, query in enumerate(search_queries[:5], 1):
            logger.info(f"   {i}. \"{query}\"")
        if len(search_queries) > 5:
            logger.info(f"   ... and {len(search_queries) - 5} more")
    else:
        logger.warning("   ⚠️ No search queries generated!")
    logger.info("")
    
    # Check if AI understood correctly
    logger.info("=" * 80)
    logger.info("🔍 VALIDATION: Did AI Understand the Research Guide?")
    logger.info("=" * 80)
    
    checks = []
    
    # Check 1: Industry
    industry = (criteria.get('industry', '') or '').lower()
    if 'real estate' in industry or 'development' in industry:
        logger.info("✅ Industry: Correctly identified 'Real Estate Development'")
        checks.append(True)
    else:
        logger.error(f"❌ Industry: WRONG! Got '{criteria.get('industry')}', should be 'Real Estate Development'")
        checks.append(False)
    
    # Check 2: Target Roles
    target_roles = criteria.get('target_roles', [])
    has_vp_dev = any('vp' in role.lower() and 'dev' in role.lower() for role in target_roles)
    has_director = any('director' in role.lower() for role in target_roles)
    if has_vp_dev or has_director:
        logger.info(f"✅ Target Roles: Found relevant roles ({len(target_roles)} total)")
        checks.append(True)
    else:
        logger.error(f"❌ Target Roles: Missing 'VP of Development' or 'Director'. Got: {target_roles}")
        checks.append(False)
    
    # Check 3: Search Queries
    if search_queries:
        good_queries = [q for q in search_queries if 'real estate' in q.lower() or 'development' in q.lower()]
        if good_queries:
            logger.info(f"✅ Search Queries: {len(good_queries)}/{len(search_queries)} mention real estate/development")
            checks.append(True)
        else:
            logger.error(f"❌ Search Queries: None mention 'real estate' or 'development'!")
            checks.append(False)
    else:
        logger.error("❌ Search Queries: None generated!")
        checks.append(False)
    
    logger.info("")
    
    if all(checks):
        logger.info("🎉 SUCCESS: AI correctly understood the research guide!")
        logger.info("")
        
        # Now test actual search
        logger.info("=" * 80)
        logger.info("STEP 2: Search for Companies Using AI-Generated Criteria")
        logger.info("=" * 80)
        
        companies = await search_companies(criteria, target_count=3)
        
        if companies:
            logger.info(f"✅ Found {len(companies)} companies:")
            for i, company in enumerate(companies, 1):
                logger.info(f"   [{i}] {company.get('name')}")
                logger.info(f"       Domain: {company.get('domain')}")
                logger.info(f"       Website: {company.get('website')}")
        else:
            logger.error("❌ No companies found!")
        
        return True
    else:
        failed_checks = sum(1 for c in checks if not c)
        logger.error(f"❌ FAILED: AI misunderstood research guide ({failed_checks}/{len(checks)} checks failed)")
        logger.error("")
        logger.error("DIAGNOSIS:")
        logger.error("The AI is not properly extracting targeting criteria from your research guide.")
        logger.error("")
        logger.error("Possible causes:")
        logger.error("1. OpenAI/Claude API key not set correctly")
        logger.error("2. AI prompt needs improvement")
        logger.error("3. Research guide format not clear enough")
        logger.error("")
        logger.error(f"Current OpenAI key: {os.getenv('OPENAI_API_KEY', 'NOT SET')[:20]}...")
        
        return False


if __name__ == "__main__":
    try:
        result = asyncio.run(test_research_guide())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        logger.info("\n⚠️ Test interrupted")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

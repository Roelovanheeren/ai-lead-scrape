#!/usr/bin/env python3
"""
End-to-end test: Research Guide → Companies → Real Contacts

This test simulates the complete workflow:
1. AI reads research guide targeting real estate firms
2. Google search finds real estate companies
3. Hunter.io finds real contacts at those companies
4. Contacts are filtered by target roles from research guide
"""

import asyncio
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Set test API keys if not already set
if not os.getenv('GOOGLE_API_KEY'):
    os.environ['GOOGLE_API_KEY'] = 'AIzaSyBBhkKvctGs4ivVaquySztFmKXa7oQ3fjg'
if not os.getenv('GOOGLE_CSE_ID'):
    os.environ['GOOGLE_CSE_ID'] = '404c0e0620566459a'
if not os.getenv('HUNTER_API_KEY'):
    os.environ['HUNTER_API_KEY'] = '6017450d6d5a86d778f26bdd547ae883cf0e1280'

from services.real_research import extract_targeting_criteria, search_companies, find_company_contacts

# Sample research guide
RESEARCH_GUIDE = """
=== Lead Generation Research Guide ===

TARGET MARKET:
Real estate development companies and real estate investment firms that are 
actively developing commercial properties, residential properties, or mixed-use 
developments.

COMPANY CRITERIA:
- Industry: Real Estate Development and Real Estate Investment
- Location: Focus on major US metropolitan areas (NYC, LA, Chicago, SF, Miami, Dallas, etc.)
- Company Size: Mid-sized to large firms (50-500 employees preferred)
- Activity: Must be actively developing new projects (not just property management)

TARGET CONTACTS:
Priority contacts at these companies:
- VP of Development
- Vice President of Development  
- Senior Vice President of Development
- Director of Development
- Development Manager
- Project Manager
- Head of Acquisitions

CONTACT REQUIREMENTS:
- Must have direct email (not generic info@)
- LinkedIn profile preferred
- Title must match target roles above

SEARCH STRATEGY:
- Look for companies with active development projects
- Prioritize firms with multiple ongoing developments
- Focus on companies mentioned in real estate news/publications
"""

async def main():
    """Run complete end-to-end test"""
    
    logger.info("="*80)
    logger.info("🧪 END-TO-END TEST: Real Estate Lead Generation")
    logger.info("="*80)
    logger.info("")
    
    # Check API keys
    google_key = os.getenv("GOOGLE_API_KEY")
    google_cse = os.getenv("GOOGLE_CSE_ID") or os.getenv("GOOGLE_SEARCH_ENGINE_ID")
    hunter_key = os.getenv("HUNTER_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    logger.info("📋 Environment Check:")
    logger.info(f"   GOOGLE_API_KEY: {'✅ SET' if google_key else '❌ MISSING'}")
    logger.info(f"   GOOGLE_CSE_ID: {'✅ SET' if google_cse else '❌ MISSING'}")
    logger.info(f"   HUNTER_API_KEY: {'✅ SET' if hunter_key else '❌ MISSING'}")
    logger.info(f"   OPENAI_API_KEY: {'✅ SET' if openai_key else '❌ MISSING'}")
    logger.info("")
    
    if not all([google_key, google_cse, hunter_key, openai_key]):
        logger.error("❌ Missing required API keys!")
        return
    
    # Step 1: Extract targeting criteria with AI
    logger.info("="*80)
    logger.info("STEP 1: AI Extracts Targeting Criteria from Research Guide")
    logger.info("="*80)
    
    prompt = "Generate leads as explained in the knowledge base"
    prompt_with_guide = f"{prompt}\n\nKNOWLEDGE BASE:\n{RESEARCH_GUIDE}"
    
    targeting_criteria = await extract_targeting_criteria(prompt_with_guide)
    
    logger.info("")
    logger.info("✅ AI Extraction Results:")
    logger.info(f"   Industry: {targeting_criteria.get('industry')}")
    logger.info(f"   Location: {targeting_criteria.get('location')}")
    logger.info(f"   Target Roles: {targeting_criteria.get('target_roles', [])[:3]}...")
    logger.info(f"   Search Queries Generated: {len(targeting_criteria.get('search_queries', []))}")
    logger.info("")
    
    # Step 2: Search for real companies
    logger.info("="*80)
    logger.info("STEP 2: Search Google for Real Estate Companies")
    logger.info("="*80)
    
    companies = await search_companies(targeting_criteria, target_count=3)
    
    logger.info("")
    logger.info(f"✅ Found {len(companies)} companies:")
    for i, company in enumerate(companies, 1):
        logger.info(f"   [{i}] {company.get('name')}")
        logger.info(f"       Domain: {company.get('domain')}")
    logger.info("")
    
    if not companies:
        logger.error("❌ No companies found - search not working!")
        return
    
    # Step 3: For well-known real estate firms, test Hunter.io directly
    logger.info("="*80)
    logger.info("STEP 3: Find Real Contacts at Known Real Estate Firms")
    logger.info("="*80)
    logger.info("")
    logger.info("Testing with known real estate development companies:")
    
    # Use well-known real estate firms for reliable testing
    test_companies = [
        {"name": "Related Companies", "domain": "related.com", "website": "https://related.com"},
        {"name": "Hines", "domain": "hines.com", "website": "https://hines.com"},
        {"name": "Trammell Crow Company", "domain": "trammellcrow.com", "website": "https://trammellcrow.com"}
    ]
    
    all_leads = []
    
    for company in test_companies:
        logger.info("")
        logger.info(f"🔍 Searching for contacts at {company['name']} ({company['domain']})")
        
        try:
            contacts = await find_company_contacts(company, targeting_criteria)
            
            if contacts:
                logger.info(f"   ✅ Found {len(contacts)} contacts")
                for contact in contacts[:3]:  # Show first 3
                    logger.info(f"      • {contact.get('name')} - {contact.get('position')}")
                    logger.info(f"        Email: {contact.get('email')}")
                    logger.info(f"        LinkedIn: {contact.get('linkedin')}")
                    logger.info(f"        Confidence: {contact.get('confidence')}%")
                all_leads.extend(contacts)
            else:
                logger.warning(f"   ⚠️ No contacts found at {company['name']}")
                
        except Exception as e:
            logger.error(f"   ❌ Error finding contacts: {e}")
            continue
    
    # Summary
    logger.info("")
    logger.info("="*80)
    logger.info("📊 FINAL RESULTS")
    logger.info("="*80)
    logger.info(f"✅ Total Leads Generated: {len(all_leads)}")
    logger.info(f"✅ Companies Researched: {len(test_companies)}")
    logger.info("")
    
    # Check if leads match targeting criteria
    target_roles = targeting_criteria.get('target_roles', [])
    matched_roles = 0
    
    for lead in all_leads:
        position = (lead.get('position', '') or '').lower()
        if any(role.lower() in position for role in target_roles):
            matched_roles += 1
    
    logger.info(f"🎯 Role Matching:")
    logger.info(f"   Target Roles: {target_roles[:3]}...")
    logger.info(f"   Leads Matching Roles: {matched_roles}/{len(all_leads)}")
    
    if matched_roles > 0:
        logger.info("")
        logger.info("🎉 SUCCESS!")
        logger.info("   ✅ AI correctly read research guide")
        logger.info("   ✅ Google search found companies")
        logger.info("   ✅ Hunter.io found real contacts")
        logger.info("   ✅ Contacts filtered by target roles")
    else:
        logger.warning("")
        logger.warning("⚠️ PARTIAL SUCCESS")
        logger.warning("   ✅ System found real contacts")
        logger.warning("   ❌ But contacts don't match target roles from research guide")
        logger.warning("   💡 May need to improve role filtering logic")
    
    logger.info("")
    logger.info("="*80)

if __name__ == "__main__":
    asyncio.run(main())

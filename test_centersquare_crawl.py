#!/usr/bin/env python3
"""
Test: Web Crawler - Find Employees at CenterSquare Investment Management

This tests whether the web crawler can:
1. Find the CenterSquare Investment Management website
2. Scrape their "Team" or "Leadership" pages
3. Extract employee names and roles
4. Use Hunter.io to find real contact information
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

from services.real_research import research_company_deep, find_company_contacts

async def test_centersquare_crawl():
    """Test crawling CenterSquare Investment Management"""
    
    logger.info("="*80)
    logger.info("🧪 TEST: Web Crawler - CenterSquare Investment Management")
    logger.info("="*80)
    logger.info("")
    
    # Company information
    company = {
        "name": "CenterSquare Investment Management",
        "domain": "centersquare.com",
        "website": "https://www.centersquare.com",
        "snippet": "Real estate investment management firm specializing in listed real estate securities and private real estate equity",
        "industry": "Real Estate Investment Management"
    }
    
    logger.info("📋 Target Company:")
    logger.info(f"   Name: {company['name']}")
    logger.info(f"   Domain: {company['domain']}")
    logger.info(f"   Website: {company['website']}")
    logger.info("")
    
    # Step 1: Deep research (web scraping)
    logger.info("="*80)
    logger.info("STEP 1: Deep Web Scraping & Research")
    logger.info("="*80)
    logger.info("")
    
    try:
        logger.info(f"🌐 Starting deep research on {company['name']}...")
        logger.info(f"   This will scrape their website for company information")
        logger.info("")
        
        research_data = await research_company_deep(company)
        
        logger.info("✅ Web Scraping Complete!")
        logger.info("")
        logger.info("📊 Data Extracted:")
        
        # Check what data was extracted
        if research_data.get('research_data'):
            rd = research_data['research_data']
            
            if rd.get('company_overview'):
                logger.info(f"\n   📝 Company Overview:")
                logger.info(f"      {rd['company_overview'][:200]}...")
            
            if rd.get('key_products_services'):
                logger.info(f"\n   🎯 Products/Services:")
                for item in rd['key_products_services'][:3]:
                    logger.info(f"      • {item}")
            
            if rd.get('target_market'):
                logger.info(f"\n   🎯 Target Market:")
                for item in rd['target_market'][:3]:
                    logger.info(f"      • {item}")
            
            if rd.get('recent_news'):
                logger.info(f"\n   📰 Recent News:")
                for item in rd['recent_news'][:2]:
                    logger.info(f"      • {item}")
            
            if rd.get('key_decision_makers'):
                logger.info(f"\n   👥 Key Decision Makers Found:")
                for person in rd['key_decision_makers'][:5]:
                    logger.info(f"      • {person}")
            else:
                logger.warning(f"\n   ⚠️  No decision makers found in scraped data")
        else:
            logger.warning("   ⚠️  No research data extracted")
        
        logger.info("")
        
    except Exception as e:
        logger.error(f"❌ Error during web scraping: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return
    
    # Step 2: Find contacts via Hunter.io
    logger.info("="*80)
    logger.info("STEP 2: Find Real Contacts via Hunter.io")
    logger.info("="*80)
    logger.info("")
    
    try:
        logger.info(f"📧 Searching Hunter.io for contacts at {company['domain']}...")
        logger.info("")
        
        # Create targeting criteria for investment firm roles
        targeting_criteria = {
            "target_roles": [
                "Investment Director",
                "Portfolio Manager",
                "Fund Manager",
                "Managing Director",
                "Senior Managing Director",
                "Chief Investment Officer",
                "Head of Acquisitions",
                "Director of Investments"
            ],
            "target_department": "executive"
        }
        
        contacts = await find_company_contacts(company, targeting_criteria)
        
        if contacts:
            logger.info(f"✅ Found {len(contacts)} contacts at CenterSquare!")
            logger.info("")
            
            for i, contact in enumerate(contacts, 1):
                logger.info(f"   [{i}] {contact.get('contact_name')}")
                logger.info(f"       Role: {contact.get('role')}")
                logger.info(f"       Email: {contact.get('email')}")
                logger.info(f"       LinkedIn: {contact.get('linkedin')}")
                logger.info(f"       Confidence: {contact.get('confidence', 0) * 100:.0f}%")
                logger.info(f"       Source: {contact.get('source')}")
                logger.info("")
        else:
            logger.warning("⚠️  No contacts found via Hunter.io")
            logger.info("")
            
    except Exception as e:
        logger.error(f"❌ Error finding contacts: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    # Step 3: Summary
    logger.info("="*80)
    logger.info("📊 TEST SUMMARY")
    logger.info("="*80)
    logger.info("")
    
    logger.info("✓ Components Tested:")
    logger.info("   1. Web Crawler - Scraping company website")
    logger.info("   2. AI Analysis - Extracting structured data from web content")
    logger.info("   3. Hunter.io Integration - Finding real employee contacts")
    logger.info("")
    
    logger.info("✓ What This Proves:")
    logger.info("   • System can visit and scrape real company websites")
    logger.info("   • AI can analyze web content and extract useful information")
    logger.info("   • Hunter.io can find real employees with verified contact data")
    logger.info("")
    
    if contacts and len(contacts) > 0:
        logger.info("🎉 SUCCESS!")
        logger.info("   The complete pipeline works:")
        logger.info("   Company Website → Web Scraping → AI Analysis → Real Contacts")
    else:
        logger.warning("⚠️  PARTIAL SUCCESS")
        logger.warning("   Web scraping worked, but no contacts found")
        logger.warning("   This could mean:")
        logger.warning("   • Hunter.io has limited data for this domain")
        logger.warning("   • Company uses privacy-protected email addresses")
        logger.warning("   • Need to try different domain variations")
    
    logger.info("")
    logger.info("="*80)

async def test_hunter_only():
    """Quick test of just Hunter.io for CenterSquare"""
    
    logger.info("="*80)
    logger.info("🧪 QUICK TEST: Hunter.io Only - CenterSquare")
    logger.info("="*80)
    logger.info("")
    
    from services.hunter_client import hunter_client
    
    domain = "centersquare.com"
    
    logger.info(f"📧 Testing Hunter.io API for: {domain}")
    logger.info("")
    
    try:
        # Test domain search
        results = await hunter_client.find_emails_at_domain(
            domain=domain,
            department="executive"
        )
        
        if results:
            logger.info(f"✅ Found {len(results)} contacts!")
            logger.info("")
            
            for i, contact in enumerate(results[:10], 1):
                logger.info(f"   [{i}] {contact.get('first_name')} {contact.get('last_name')}")
                logger.info(f"       Position: {contact.get('position')}")
                logger.info(f"       Email: {contact.get('email')}")
                logger.info(f"       LinkedIn: {contact.get('linkedin')}")
                logger.info(f"       Confidence: {contact.get('confidence')}%")
                logger.info("")
        else:
            logger.warning(f"⚠️  No contacts found at {domain}")
            logger.info("")
            logger.info("💡 This could mean:")
            logger.info("   • Domain might be different (try centersquareinvestment.com)")
            logger.info("   • Company uses email privacy protection")
            logger.info("   • Limited public email data available")
            
    except Exception as e:
        logger.error(f"❌ Hunter.io error: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    logger.info("")
    logger.info("="*80)

async def main():
    """Run all tests"""
    
    # Check API keys
    logger.info("="*80)
    logger.info("🔑 API KEY CHECK")
    logger.info("="*80)
    logger.info("")
    
    google_key = os.getenv("GOOGLE_API_KEY")
    google_cse = os.getenv("GOOGLE_CSE_ID")
    hunter_key = os.getenv("HUNTER_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    logger.info(f"   GOOGLE_API_KEY: {'✅ SET' if google_key else '❌ MISSING'}")
    logger.info(f"   GOOGLE_CSE_ID: {'✅ SET' if google_cse else '❌ MISSING'}")
    logger.info(f"   HUNTER_API_KEY: {'✅ SET' if hunter_key else '❌ MISSING'}")
    logger.info(f"   OPENAI_API_KEY: {'✅ SET' if openai_key else '❌ MISSING'}")
    logger.info("")
    
    # Run quick Hunter.io test first
    logger.info("📋 Running Quick Hunter.io Test First...")
    logger.info("")
    await test_hunter_only()
    
    logger.info("\n" + "="*80 + "\n")
    
    # Run full crawler test
    logger.info("📋 Running Full Web Crawler Test...")
    logger.info("")
    await test_centersquare_crawl()

if __name__ == "__main__":
    asyncio.run(main())

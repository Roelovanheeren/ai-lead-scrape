#!/usr/bin/env python3
"""
Test Google Custom Search API Configuration
Run this script to verify your Google API credentials are working
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger.info("✅ Loaded .env file")
except Exception as e:
    logger.warning(f"⚠️ Could not load .env file: {e}")

async def test_google_api():
    """Test Google Custom Search API"""
    
    print("="*80)
    print("🔍 GOOGLE CUSTOM SEARCH API TEST")
    print("="*80)
    
    # Check environment variables
    google_api_key = os.getenv("GOOGLE_API_KEY")
    google_cse_id = os.getenv("GOOGLE_CSE_ID") or os.getenv("GOOGLE_SEARCH_ENGINE_ID")
    
    print("\n📋 Configuration Check:")
    print(f"  GOOGLE_API_KEY: {'✅ SET (len={})'.format(len(google_api_key)) if google_api_key else '❌ NOT SET'}")
    print(f"  GOOGLE_CSE_ID: {'✅ SET (len={})'.format(len(google_cse_id)) if google_cse_id else '❌ NOT SET'}")
    
    if not google_api_key:
        print("\n❌ ERROR: GOOGLE_API_KEY is not set!")
        print("   Set it in Railway or .env file:")
        print("   GOOGLE_API_KEY=your_api_key_here")
        return False
    
    if not google_cse_id:
        print("\n❌ ERROR: GOOGLE_CSE_ID or GOOGLE_SEARCH_ENGINE_ID is not set!")
        print("   Set it in Railway or .env file:")
        print("   GOOGLE_CSE_ID=your_search_engine_id_here")
        return False
    
    # Check if aiohttp is available
    try:
        import aiohttp
        print("  aiohttp: ✅ Available")
    except ImportError:
        print("  aiohttp: ❌ NOT AVAILABLE - Install with: pip install aiohttp")
        return False
    
    # Try to make a test API call
    print("\n🌐 Testing Google Custom Search API...")
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": google_api_key,
        "cx": google_cse_id,
        "q": "technology companies",
        "num": 3
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print(f"  Making request to: {url}")
            print(f"  Search query: 'technology companies'")
            
            async with session.get(url, params=params) as response:
                print(f"  Response status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    items_count = len(data.get("items", []))
                    
                    print(f"\n✅ SUCCESS! API is working correctly")
                    print(f"  Found {items_count} search results")
                    
                    if items_count > 0:
                        print("\n📊 Sample Results:")
                        for i, item in enumerate(data.get("items", [])[:3], 1):
                            print(f"    {i}. {item.get('title', 'N/A')}")
                            print(f"       {item.get('link', 'N/A')}")
                    
                    return True
                else:
                    error_text = await response.text()
                    print(f"\n❌ API ERROR: Status {response.status}")
                    print(f"  Error: {error_text[:500]}")
                    
                    if response.status == 400:
                        print("\n💡 Possible issues:")
                        print("  - GOOGLE_API_KEY is invalid")
                        print("  - GOOGLE_CSE_ID is invalid")
                        print("  - API key doesn't have Custom Search API enabled")
                    elif response.status == 403:
                        print("\n💡 Possible issues:")
                        print("  - API key has exceeded quota")
                        print("  - Custom Search API is not enabled for this project")
                        print("  - Billing is not enabled")
                    
                    return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        print(f"  Traceback: {traceback.format_exc()}")
        return False

async def test_real_research_module():
    """Test if real research module loads correctly"""
    
    print("\n" + "="*80)
    print("🔬 REAL RESEARCH MODULE TEST")
    print("="*80)
    
    try:
        from services.real_research import (
            extract_targeting_criteria,
            search_companies,
            research_company_deep,
            find_company_contacts,
            generate_personalized_outreach
        )
        
        print("\n✅ Real research module loaded successfully")
        print("  - extract_targeting_criteria: ✅")
        print("  - search_companies: ✅")
        print("  - research_company_deep: ✅")
        print("  - find_company_contacts: ✅")
        print("  - generate_personalized_outreach: ✅")
        
        # Test a simple search
        print("\n🔍 Testing search_companies function...")
        criteria = {
            "keywords": ["technology", "software"],
            "industry": "Technology"
        }
        
        companies = await search_companies(criteria, target_count=3)
        
        if companies:
            print(f"✅ Found {len(companies)} companies:")
            for company in companies:
                print(f"  - {company.get('name', 'Unknown')}")
                print(f"    Website: {company.get('website', 'N/A')}")
        else:
            print("⚠️ No companies found (this might indicate Google API issues)")
        
        return True
        
    except ImportError as e:
        print(f"\n❌ Failed to import real research module: {e}")
        print("\n💡 Possible issues:")
        print("  - Missing dependencies (aiohttp, openai, anthropic)")
        print("  - Install with: pip install aiohttp openai anthropic")
        return False
    except Exception as e:
        print(f"\n❌ Error testing real research module: {e}")
        import traceback
        print(f"  Traceback: {traceback.format_exc()}")
        return False

async def main():
    """Main test function"""
    
    print("\n" + "🚀 AI Lead Scrape - Google API Configuration Test" + "\n")
    
    # Test 1: Google API
    api_success = await test_google_api()
    
    # Test 2: Real Research Module
    module_success = await test_real_research_module()
    
    # Final summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    print(f"  Google API: {'✅ PASS' if api_success else '❌ FAIL'}")
    print(f"  Real Research Module: {'✅ PASS' if module_success else '❌ FAIL'}")
    
    if api_success and module_success:
        print("\n✅ All tests passed! Your system is ready for real web scraping.")
    else:
        print("\n⚠️ Some tests failed. Please fix the issues above before deploying.")
    
    print("="*80 + "\n")
    
    return api_success and module_success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

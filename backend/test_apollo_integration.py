#!/usr/bin/env python3
"""
Test Apollo.io API integration
Tests the contact discovery functionality
"""

import asyncio
import logging
import os
import httpx
from typing import Dict, Any, List

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ApolloAPITester:
    """Test Apollo.io API integration"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.apollo.io/api/v1"
        self.headers = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache"
        }
    
    async def test_people_search(self, company_domain: str = "apollo.io") -> Dict[str, Any]:
        """Test searching for people at a company"""
        try:
            url = f"{self.base_url}/mixed_people/search"
            
            # Apollo.io search parameters
            params = {
                "api_key": self.api_key,
                "q_organization_domains": company_domain,
                "page": 1,
                "per_page": 10,
                "person_titles": ["CEO", "CTO", "VP", "Director", "Manager"],
                "person_seniorities": ["c_level", "vp", "director", "manager"]
            }
            
            logger.info(f"Searching for people at {company_domain}...")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=self.headers)
                
                if response.status_code == 200:
                    data = response.json()
                    people = data.get("people", [])
                    
                    logger.info(f"✅ Found {len(people)} people at {company_domain}")
                    
                    # Show sample results
                    for person in people[:3]:  # Show first 3
                        logger.info(f"  - {person.get('name', 'N/A')} ({person.get('title', 'N/A')})")
                    
                    return {
                        "success": True,
                        "people_count": len(people),
                        "people": people[:5],  # Return first 5
                        "api_response": data
                    }
                else:
                    logger.error(f"❌ API request failed: {response.status_code}")
                    logger.error(f"Response: {response.text}")
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}",
                        "response": response.text
                    }
                    
        except Exception as e:
            logger.error(f"❌ Apollo API test failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def test_company_search(self, company_name: str = "Apollo") -> Dict[str, Any]:
        """Test searching for companies"""
        try:
            url = f"{self.base_url}/mixed_companies/search"
            
            params = {
                "api_key": self.api_key,
                "q": company_name,
                "page": 1,
                "per_page": 5
            }
            
            logger.info(f"Searching for companies matching '{company_name}'...")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=self.headers)
                
                if response.status_code == 200:
                    data = response.json()
                    companies = data.get("organizations", [])
                    
                    logger.info(f"✅ Found {len(companies)} companies")
                    
                    for company in companies[:3]:
                        logger.info(f"  - {company.get('name', 'N/A')} ({company.get('website_url', 'N/A')})")
                    
                    return {
                        "success": True,
                        "companies_count": len(companies),
                        "companies": companies[:3]
                    }
                else:
                    logger.error(f"❌ Company search failed: {response.status_code}")
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"❌ Company search failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

async def test_apollo_integration():
    """Test Apollo.io API integration"""
    logger.info("🧪 Testing Apollo.io API Integration...")
    
    # Get API key from environment or prompt user
    api_key = os.getenv('APOLLO_API_KEY')
    
    if not api_key:
        logger.error("❌ APOLLO_API_KEY not found in environment variables")
        logger.info("Please set your Apollo.io API key:")
        logger.info("export APOLLO_API_KEY=your_api_key_here")
        return False
    
    # Initialize tester
    tester = ApolloAPITester(api_key)
    
    # Test 1: Company Search
    logger.info("\n🔍 Test 1: Company Search")
    company_result = await tester.test_company_search("Apollo")
    
    # Test 2: People Search
    logger.info("\n👥 Test 2: People Search")
    people_result = await tester.test_people_search("apollo.io")
    
    # Summary
    logger.info("\n📊 Test Results:")
    logger.info(f"Company Search: {'✅ PASS' if company_result.get('success') else '❌ FAIL'}")
    logger.info(f"People Search: {'✅ PASS' if people_result.get('success') else '❌ FAIL'}")
    
    if company_result.get('success') and people_result.get('success'):
        logger.info("\n🎉 Apollo.io integration working perfectly!")
        logger.info("Ready to integrate into the main platform.")
        return True
    else:
        logger.error("\n❌ Some Apollo.io tests failed.")
        return False

async def main():
    """Main test function"""
    success = await test_apollo_integration()
    
    if success:
        logger.info("\n🚀 Next steps:")
        logger.info("1. Test other API integrations (OpenAI, Claude, Google)")
        logger.info("2. Run end-to-end test with real data")
        logger.info("3. Deploy to Railway")
    else:
        logger.error("\n🔧 Please check your Apollo.io API key and try again.")

if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Comprehensive API Testing Script
Tests all configured APIs to ensure they're working
"""

import asyncio
import logging
import os
import httpx
import json
from typing import Dict, Any, List, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APITester:
    """Test all configured APIs"""
    
    def __init__(self):
        self.results = {}
    
    async def test_google_search(self) -> bool:
        """Test Google Custom Search API"""
        logger.info("🔍 Testing Google Custom Search API...")
        
        api_key = os.getenv('GOOGLE_API_KEY')
        search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
        
        if not api_key or not search_engine_id:
            logger.warning("❌ Google API keys not set")
            return False
        
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": api_key,
                "cx": search_engine_id,
                "q": "AI startups",
                "num": 3
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    items = data.get("items", [])
                    logger.info(f"✅ Google Search: Found {len(items)} results")
                    self.results["google_search"] = {
                        "status": "success",
                        "results_count": len(items),
                        "quota_remaining": data.get("searchInformation", {}).get("totalResults", "Unknown")
                    }
                    return True
                else:
                    logger.error(f"❌ Google Search failed: {response.status_code}")
                    logger.error(f"Response: {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Google Search error: {str(e)}")
            return False
    
    async def test_openai(self) -> bool:
        """Test OpenAI API"""
        logger.info("🤖 Testing OpenAI API...")
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.warning("❌ OpenAI API key not set")
            return False
        
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "user", "content": "Say 'Hello from OpenAI API test'"}
                ],
                "max_tokens": 50
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=data)
                
                if response.status_code == 200:
                    result = response.json()
                    message = result["choices"][0]["message"]["content"]
                    logger.info(f"✅ OpenAI: {message.strip()}")
                    self.results["openai"] = {
                        "status": "success",
                        "model": "gpt-3.5-turbo",
                        "response": message.strip()
                    }
                    return True
                else:
                    logger.error(f"❌ OpenAI failed: {response.status_code}")
                    logger.error(f"Response: {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ OpenAI error: {str(e)}")
            return False
    
    async def test_claude(self) -> bool:
        """Test Claude API"""
        logger.info("🧠 Testing Claude API...")
        
        api_key = os.getenv('CLAUDE_API_KEY')
        if not api_key:
            logger.warning("❌ Claude API key not set")
            return False
        
        try:
            url = "https://api.anthropic.com/v1/messages"
            headers = {
                "x-api-key": api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            data = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 50,
                "messages": [
                    {"role": "user", "content": "Say 'Hello from Claude API test'"}
                ]
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=data)
                
                if response.status_code == 200:
                    result = response.json()
                    message = result["content"][0]["text"]
                    logger.info(f"✅ Claude: {message.strip()}")
                    self.results["claude"] = {
                        "status": "success",
                        "model": "claude-3-haiku-20240307",
                        "response": message.strip()
                    }
                    return True
                else:
                    logger.error(f"❌ Claude failed: {response.status_code}")
                    logger.error(f"Response: {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Claude error: {str(e)}")
            return False
    
    async def test_clearbit(self) -> bool:
        """Test Clearbit API"""
        logger.info("🏢 Testing Clearbit API...")
        
        api_key = os.getenv('CLEARBIT_API_KEY')
        if not api_key:
            logger.warning("⚠️ Clearbit API key not set (optional)")
            return False
        
        try:
            url = "https://company.clearbit.com/v2/companies/find?domain=google.com"
            headers = {"Authorization": f"Bearer {api_key}"}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ Clearbit: Found {data.get('name', 'Unknown')}")
                    self.results["clearbit"] = {
                        "status": "success",
                        "company": data.get('name', 'Unknown'),
                        "domain": data.get('domain', 'Unknown')
                    }
                    return True
                else:
                    logger.error(f"❌ Clearbit failed: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Clearbit error: {str(e)}")
            return False
    
    async def test_hunter(self) -> bool:
        """Test Hunter.io API"""
        logger.info("👥 Testing Hunter.io API...")
        
        api_key = os.getenv('HUNTER_API_KEY')
        if not api_key:
            logger.warning("⚠️ Hunter.io API key not set (optional)")
            return False
        
        try:
            url = "https://api.hunter.io/v2/domain-search"
            params = {
                "domain": "google.com",
                "api_key": api_key,
                "limit": 1
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    emails = data.get("data", {}).get("emails", [])
                    logger.info(f"✅ Hunter.io: Found {len(emails)} emails")
                    self.results["hunter"] = {
                        "status": "success",
                        "emails_found": len(emails),
                        "domain": "google.com"
                    }
                    return True
                else:
                    logger.error(f"❌ Hunter.io failed: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Hunter.io error: {str(e)}")
            return False
    
    async def test_all_apis(self) -> bool:
        """Test all configured APIs"""
        logger.info("🧪 Testing All APIs...")
        logger.info("=" * 50)
        
        # Test required APIs
        google_success = await self.test_google_search()
        openai_success = await self.test_openai()
        claude_success = await self.test_claude()
        
        # Test optional APIs
        clearbit_success = await self.test_clearbit()
        hunter_success = await self.test_hunter()
        
        # Summary
        logger.info("\n📊 API Test Results:")
        logger.info("=" * 30)
        
        required_apis = [
            ("Google Search", google_success),
            ("OpenAI", openai_success),
            ("Claude", claude_success)
        ]
        
        optional_apis = [
            ("Clearbit", clearbit_success),
            ("Hunter.io", hunter_success)
        ]
        
        required_passed = sum(1 for _, success in required_apis if success)
        optional_passed = sum(1 for _, success in optional_apis if success)
        
        logger.info("\n🔑 Required APIs:")
        for name, success in required_apis:
            status = "✅ PASS" if success else "❌ FAIL"
            logger.info(f"  {name}: {status}")
        
        logger.info("\n🔑 Optional APIs:")
        for name, success in optional_apis:
            status = "✅ PASS" if success else "⚠️ SKIP"
            logger.info(f"  {name}: {status}")
        
        logger.info(f"\n📈 Summary:")
        logger.info(f"  Required APIs: {required_passed}/3 passed")
        logger.info(f"  Optional APIs: {optional_passed}/2 passed")
        
        if required_passed == 3:
            logger.info("\n🎉 All required APIs working! Ready to deploy!")
            return True
        else:
            logger.info(f"\n⚠️ {3 - required_passed} required APIs failed. Please check your keys.")
            return False

async def main():
    """Main testing function"""
    tester = APITester()
    success = await tester.test_all_apis()
    
    if success:
        logger.info("\n🚀 Ready to test the full platform!")
        logger.info("Run: python3 free_lead_generator.py")
    else:
        logger.info("\n🔧 Please fix the API issues first.")
        logger.info("See FREE_API_SETUP.md for setup instructions.")

if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3
"""
Test the deployed AI Lead Generation Platform
"""

import asyncio
import logging
import httpx
import time
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlatformTester:
    """Test the deployed platform"""
    
    def __init__(self, base_url: str = "https://ai-lead-scrape-production.up.railway.app"):
        self.base_url = base_url
        self.timeout = 30
    
    async def test_health_endpoint(self) -> bool:
        """Test the health endpoint"""
        logger.info("🔍 Testing health endpoint...")
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/health")
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ Health check: {data}")
                    return True
                else:
                    logger.error(f"❌ Health check failed: {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"❌ Health check error: {str(e)}")
            return False
    
    async def test_root_endpoint(self) -> bool:
        """Test the root endpoint"""
        logger.info("🔍 Testing root endpoint...")
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/")
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ Root endpoint: {data}")
                    return True
                else:
                    logger.error(f"❌ Root endpoint failed: {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"❌ Root endpoint error: {str(e)}")
            return False
    
    async def test_job_creation(self) -> bool:
        """Test job creation endpoint"""
        logger.info("🔍 Testing job creation...")
        try:
            job_data = {
                "prompt": "Find AI startups in San Francisco",
                "target_count": 5,
                "quality_threshold": 0.8
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/jobs/", json=job_data)
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ Job created: {data}")
                    return True
                else:
                    logger.error(f"❌ Job creation failed: {response.status_code}")
                    logger.error(f"Response: {response.text}")
                    return False
        except Exception as e:
            logger.error(f"❌ Job creation error: {str(e)}")
            return False
    
    async def test_platform_availability(self) -> bool:
        """Test if the platform is accessible"""
        logger.info("🔍 Testing platform availability...")
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/")
                if response.status_code in [200, 404]:  # 404 means app is deployed but route not found
                    logger.info(f"✅ Platform is accessible: {response.status_code}")
                    return True
                else:
                    logger.error(f"❌ Platform not accessible: {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"❌ Platform availability error: {str(e)}")
            return False
    
    async def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests"""
        logger.info("🧪 Testing Deployed AI Lead Generation Platform")
        logger.info("=" * 60)
        
        # Test platform availability first
        availability = await self.test_platform_availability()
        
        if not availability:
            logger.error("❌ Platform is not accessible. It might still be deploying.")
            return {"availability": False}
        
        # Run other tests
        health = await self.test_health_endpoint()
        root = await self.test_root_endpoint()
        job_creation = await self.test_job_creation()
        
        results = {
            "availability": availability,
            "health": health,
            "root": root,
            "job_creation": job_creation
        }
        
        # Summary
        logger.info("\n📊 Test Results:")
        logger.info("=" * 30)
        for test, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"  {test}: {status}")
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        logger.info(f"\n📈 Summary: {passed}/{total} tests passed")
        
        if passed == total:
            logger.info("\n🎉 All tests passed! Your platform is working!")
        elif passed > 0:
            logger.info("\n⚠️ Some tests passed. Platform is partially working.")
        else:
            logger.info("\n❌ All tests failed. Platform needs attention.")
        
        return results

async def main():
    """Main test function"""
    tester = PlatformTester()
    results = await tester.run_all_tests()
    
    if results.get("availability", False):
        logger.info(f"\n🚀 Your AI Lead Generation Platform is live!")
        logger.info(f"🔗 URL: https://ai-lead-scrape-production.up.railway.app")
        logger.info(f"\n🎯 Ready to generate leads!")
    else:
        logger.info(f"\n⏳ Platform is still deploying. Please wait a few minutes and try again.")

if __name__ == "__main__":
    asyncio.run(main())

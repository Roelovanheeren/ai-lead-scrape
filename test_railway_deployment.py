#!/usr/bin/env python3
"""
Test Railway deployment status
"""

import asyncio
import logging
import httpx
import time
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RailwayTester:
    """Test Railway deployment"""
    
    def __init__(self, base_url: str = "https://ai-lead-scrape-production.up.railway.app"):
        self.base_url = base_url
        self.timeout = 30
    
    async def test_all_endpoints(self):
        """Test all available endpoints"""
        logger.info("🧪 Testing Railway Deployment")
        logger.info("=" * 50)
        
        endpoints = [
            ("/", "Root endpoint"),
            ("/health", "Health check"),
            ("/test", "Test endpoint"),
            ("/jobs/", "Jobs list"),
        ]
        
        results = {}
        
        for endpoint, description in endpoints:
            logger.info(f"\n🔍 Testing {description}: {endpoint}")
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(f"{self.base_url}{endpoint}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        logger.info(f"✅ {description}: {response.status_code}")
                        logger.info(f"   Response: {data}")
                        results[endpoint] = {"status": "success", "data": data}
                    else:
                        logger.error(f"❌ {description}: {response.status_code}")
                        logger.error(f"   Response: {response.text}")
                        results[endpoint] = {"status": "error", "code": response.status_code}
                        
            except Exception as e:
                logger.error(f"❌ {description}: {str(e)}")
                results[endpoint] = {"status": "error", "message": str(e)}
        
        # Test job creation
        logger.info(f"\n🔍 Testing job creation...")
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
                    logger.info(f"✅ Job creation: {response.status_code}")
                    logger.info(f"   Response: {data}")
                    results["/jobs/ POST"] = {"status": "success", "data": data}
                else:
                    logger.error(f"❌ Job creation: {response.status_code}")
                    logger.error(f"   Response: {response.text}")
                    results["/jobs/ POST"] = {"status": "error", "code": response.status_code}
                    
        except Exception as e:
            logger.error(f"❌ Job creation: {str(e)}")
            results["/jobs/ POST"] = {"status": "error", "message": str(e)}
        
        return results
    
    def print_summary(self, results: Dict[str, Any]):
        """Print test summary"""
        logger.info("\n📊 Test Results Summary:")
        logger.info("=" * 30)
        
        successful = 0
        total = len(results)
        
        for endpoint, result in results.items():
            if result["status"] == "success":
                logger.info(f"✅ {endpoint}: PASS")
                successful += 1
            else:
                logger.info(f"❌ {endpoint}: FAIL")
        
        logger.info(f"\n📈 Overall: {successful}/{total} endpoints working")
        
        if successful == total:
            logger.info("\n🎉 All tests passed! Your platform is working!")
        elif successful > 0:
            logger.info("\n⚠️ Some endpoints working. Platform is partially functional.")
        else:
            logger.info("\n❌ No endpoints working. Platform needs attention.")
            
        logger.info(f"\n🔗 Your platform URL: {self.base_url}")
        logger.info("📋 Next steps:")
        if successful > 0:
            logger.info("1. Add your API keys to Railway environment variables")
            logger.info("2. Test the full functionality")
            logger.info("3. Start generating leads!")
        else:
            logger.info("1. Check Railway deployment logs")
            logger.info("2. Verify environment variables are set")
            logger.info("3. Check if the application is starting correctly")

async def main():
    """Main test function"""
    tester = RailwayTester()
    results = await tester.test_all_endpoints()
    tester.print_summary(results)

if __name__ == "__main__":
    asyncio.run(main())

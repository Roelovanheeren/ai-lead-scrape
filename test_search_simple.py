#!/usr/bin/env python3
"""
Simplified Search API Test
Tests if Google Custom Search API can find and retrieve real company data
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import required libraries
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    logger.error("❌ aiohttp not installed. Run: pip install aiohttp")
    AIOHTTP_AVAILABLE = False
    sys.exit(1)

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ requests not installed. Using aiohttp only.")
    REQUESTS_AVAILABLE = False


class SimpleSearchTester:
    """Test Google Custom Search API with real queries"""
    
    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.google_cse_id = os.getenv("GOOGLE_CSE_ID") or os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        
        logger.info("=" * 80)
        logger.info("🔍 SIMPLE SEARCH API TESTER")
        logger.info("=" * 80)
        
        # Check API keys
        if not self.google_api_key:
            logger.error("❌ GOOGLE_API_KEY not set!")
            logger.info("Set it with: export GOOGLE_API_KEY='your_key_here'")
            sys.exit(1)
        else:
            logger.info(f"✅ GOOGLE_API_KEY found: {self.google_api_key[:10]}...{self.google_api_key[-10:]}")
        
        if not self.google_cse_id:
            logger.error("❌ GOOGLE_CSE_ID not set!")
            logger.info("Set it with: export GOOGLE_CSE_ID='your_cse_id_here'")
            sys.exit(1)
        else:
            logger.info(f"✅ GOOGLE_CSE_ID found: {self.google_cse_id}")
        
        logger.info("")
    
    async def test_google_search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Test Google Custom Search API with a real query"""
        
        logger.info(f"🔎 Testing Google Search API")
        logger.info(f"   Query: '{query}'")
        logger.info(f"   Requested results: {num_results}")
        logger.info("")
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.google_api_key,
            "cx": self.google_cse_id,
            "q": query,
            "num": min(num_results, 10)  # API max is 10 per request
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                logger.info("📡 Sending request to Google Custom Search API...")
                async with session.get(url, params=params, timeout=30) as response:
                    status = response.status
                    logger.info(f"📥 Response status: {status}")
                    
                    if status == 200:
                        data = await response.json()
                        
                        # Parse results
                        search_info = data.get("searchInformation", {})
                        total_results = search_info.get("totalResults", "0")
                        search_time = search_info.get("searchTime", 0)
                        
                        # Convert total_results to int for formatting
                        try:
                            total_results_int = int(total_results)
                            total_results_str = f"{total_results_int:,}"
                        except (ValueError, TypeError):
                            total_results_str = total_results
                        
                        logger.info("")
                        logger.info("✅ SEARCH SUCCESSFUL!")
                        logger.info(f"   Total results available: {total_results_str}")
                        logger.info(f"   Search time: {search_time} seconds")
                        logger.info("")
                        
                        # Get search results
                        items = data.get("items", [])
                        logger.info(f"📄 Retrieved {len(items)} results:")
                        logger.info("")
                        
                        results = []
                        for i, item in enumerate(items, 1):
                            title = item.get("title", "No title")
                            link = item.get("link", "No URL")
                            snippet = item.get("snippet", "No description")
                            
                            logger.info(f"   [{i}] {title}")
                            logger.info(f"       URL: {link}")
                            logger.info(f"       Snippet: {snippet[:100]}...")
                            logger.info("")
                            
                            results.append({
                                "title": title,
                                "url": link,
                                "snippet": snippet,
                                "rank": i
                            })
                        
                        return results
                    
                    elif status == 403:
                        error_data = await response.json()
                        error_msg = error_data.get("error", {}).get("message", "Unknown error")
                        logger.error(f"❌ API KEY ERROR (403): {error_msg}")
                        logger.error("   Check if your API key is valid and has Custom Search enabled")
                        return []
                    
                    elif status == 400:
                        error_data = await response.json()
                        error_msg = error_data.get("error", {}).get("message", "Unknown error")
                        logger.error(f"❌ BAD REQUEST (400): {error_msg}")
                        logger.error("   Check if your CSE ID is correct")
                        return []
                    
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ API ERROR ({status}): {error_text[:200]}")
                        return []
        
        except asyncio.TimeoutError:
            logger.error("❌ Request timed out after 30 seconds")
            return []
        except Exception as e:
            logger.error(f"❌ Exception occurred: {type(e).__name__}: {str(e)}")
            return []
    
    async def test_simple_scrape(self, url: str) -> Dict[str, Any]:
        """Test simple page scraping"""
        
        logger.info(f"🕷️  Testing page scrape")
        logger.info(f"   URL: {url}")
        logger.info("")
        
        try:
            async with aiohttp.ClientSession() as session:
                logger.info("📡 Fetching page content...")
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                async with session.get(url, headers=headers, timeout=30) as response:
                    status = response.status
                    content_type = response.headers.get('Content-Type', 'unknown')
                    
                    logger.info(f"📥 Response status: {status}")
                    logger.info(f"📄 Content-Type: {content_type}")
                    
                    if status == 200:
                        text = await response.text()
                        text_length = len(text)
                        
                        logger.info(f"✅ Page fetched successfully!")
                        logger.info(f"   Content length: {text_length:,} characters")
                        logger.info(f"   First 500 chars:")
                        logger.info("-" * 80)
                        logger.info(text[:500])
                        logger.info("-" * 80)
                        logger.info("")
                        
                        return {
                            "success": True,
                            "status": status,
                            "content_type": content_type,
                            "length": text_length,
                            "preview": text[:500]
                        }
                    else:
                        logger.error(f"❌ Failed to fetch page: Status {status}")
                        return {"success": False, "status": status}
        
        except Exception as e:
            logger.error(f"❌ Exception: {type(e).__name__}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def run_full_test(self):
        """Run complete search and scrape test"""
        
        logger.info("🚀 Starting full search and scrape test")
        logger.info("")
        
        # Test 1: Search for real estate development companies
        test_queries = [
            "real estate development companies",
            "commercial real estate developers",
            "residential property developers"
        ]
        
        all_results = []
        
        for query in test_queries:
            logger.info("=" * 80)
            results = await self.test_google_search(query, num_results=3)
            all_results.extend(results)
            logger.info("")
            await asyncio.sleep(1)  # Be nice to the API
        
        # Test 2: Try to scrape the first result
        if all_results:
            logger.info("=" * 80)
            first_url = all_results[0]["url"]
            scrape_result = await self.test_simple_scrape(first_url)
            logger.info("")
        
        # Summary
        logger.info("=" * 80)
        logger.info("📊 TEST SUMMARY")
        logger.info("=" * 80)
        logger.info(f"✅ Total search results found: {len(all_results)}")
        logger.info(f"✅ URLs discovered:")
        for i, result in enumerate(all_results[:5], 1):
            logger.info(f"   [{i}] {result['url']}")
        logger.info("")
        logger.info("🎉 Test complete!")
        logger.info("")


async def main():
    """Main test function"""
    tester = SimpleSearchTester()
    await tester.run_full_test()


if __name__ == "__main__":
    # Check if running in async context
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n⚠️ Test interrupted by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)

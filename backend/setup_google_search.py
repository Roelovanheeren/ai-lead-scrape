#!/usr/bin/env python3
"""
Google Custom Search Engine Setup Helper
Helps you create and configure a Google Custom Search Engine
"""

import asyncio
import logging
import os
import httpx
import webbrowser
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleSearchSetup:
    """Help set up Google Custom Search Engine"""
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            logger.error("❌ GOOGLE_API_KEY not set")
            return
    
    def show_manual_setup(self):
        """Show manual setup instructions"""
        logger.info("🔍 Google Custom Search Engine Setup")
        logger.info("=" * 50)
        logger.info("")
        logger.info("📋 Manual Setup (Recommended):")
        logger.info("1. Go to: https://cse.google.com/cse/")
        logger.info("2. Click 'Add' to create a new search engine")
        logger.info("3. Sites to search: * (searches entire web)")
        logger.info("4. Name: 'AI Lead Generation Search'")
        logger.info("5. Click 'Create'")
        logger.info("6. Go to 'Setup' → 'Basics'")
        logger.info("7. Copy your 'Search engine ID'")
        logger.info("")
        logger.info("🚀 Quick Setup URL:")
        logger.info("https://cse.google.com/cse/create/new")
        logger.info("")
        
        # Try to open the URL
        try:
            webbrowser.open("https://cse.google.com/cse/create/new")
            logger.info("✅ Opened Google CSE setup page in your browser")
        except:
            logger.info("⚠️ Could not open browser automatically")
            logger.info("   Please copy and paste the URL above")
    
    async def test_search_engine(self, search_engine_id: str) -> bool:
        """Test if a search engine ID works"""
        if not self.api_key:
            logger.error("❌ GOOGLE_API_KEY not set")
            return False
        
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": self.api_key,
                "cx": search_engine_id,
                "q": "test search",
                "num": 1
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info("✅ Search engine ID is working!")
                    logger.info(f"   Found {data.get('searchInformation', {}).get('totalResults', 'Unknown')} total results")
                    return True
                else:
                    logger.error(f"❌ Search engine test failed: {response.status_code}")
                    logger.error(f"   Response: {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Search engine test error: {str(e)}")
            return False
    
    def update_env_file(self, search_engine_id: str):
        """Update .env file with search engine ID"""
        try:
            # Read current .env file
            with open('.env', 'r') as f:
                content = f.read()
            
            # Replace the placeholder
            updated_content = content.replace(
                'GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here',
                f'GOOGLE_SEARCH_ENGINE_ID={search_engine_id}'
            )
            
            # Write back to file
            with open('.env', 'w') as f:
                f.write(updated_content)
            
            logger.info(f"✅ Updated .env file with search engine ID: {search_engine_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating .env file: {str(e)}")
            return False
    
    async def interactive_setup(self):
        """Interactive setup process"""
        logger.info("🚀 Google Custom Search Engine Setup")
        logger.info("=" * 50)
        
        if not self.api_key:
            logger.error("❌ GOOGLE_API_KEY not set in environment")
            return False
        
        logger.info(f"✅ Google API Key: {self.api_key[:10]}...")
        logger.info("")
        
        # Show manual setup instructions
        self.show_manual_setup()
        
        # Get search engine ID from user
        logger.info("")
        search_engine_id = input("🔑 Enter your Search Engine ID: ").strip()
        
        if not search_engine_id:
            logger.error("❌ No search engine ID provided")
            return False
        
        # Test the search engine
        logger.info(f"\n🧪 Testing search engine ID: {search_engine_id}")
        if await self.test_search_engine(search_engine_id):
            # Update .env file
            if self.update_env_file(search_engine_id):
                logger.info("\n🎉 Google Custom Search setup complete!")
                logger.info("✅ API Key: Set")
                logger.info("✅ Search Engine ID: Set")
                logger.info("✅ Test: Passed")
                return True
            else:
                logger.error("❌ Failed to update .env file")
                return False
        else:
            logger.error("❌ Search engine ID test failed")
            return False

async def main():
    """Main setup function"""
    setup = GoogleSearchSetup()
    
    if not setup.api_key:
        logger.error("❌ Please set GOOGLE_API_KEY first")
        logger.info("Run: export GOOGLE_API_KEY=your_key_here")
        return
    
    success = await setup.interactive_setup()
    
    if success:
        logger.info("\n🚀 Ready to test the full platform!")
        logger.info("Run: python3 test_all_apis.py")
    else:
        logger.info("\n🔧 Please try the setup again")

if __name__ == "__main__":
    asyncio.run(main())

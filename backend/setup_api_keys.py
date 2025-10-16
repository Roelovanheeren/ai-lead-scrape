#!/usr/bin/env python3
"""
API Key Setup and Testing Script
Helps you set up and test all the free APIs
"""

import asyncio
import logging
import os
import sys
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIKeySetup:
    """Help set up and test API keys"""
    
    def __init__(self):
        self.required_keys = {
            "GOOGLE_API_KEY": "Google Custom Search API key",
            "GOOGLE_SEARCH_ENGINE_ID": "Google Custom Search Engine ID",
            "OPENAI_API_KEY": "OpenAI API key",
            "CLAUDE_API_KEY": "Claude API key"
        }
        
        self.optional_keys = {
            "CLEARBIT_API_KEY": "Clearbit API key (optional)",
            "HUNTER_API_KEY": "Hunter.io API key (optional)"
        }
    
    def check_environment(self) -> Dict[str, bool]:
        """Check which API keys are set"""
        results = {}
        
        logger.info("🔍 Checking API keys...")
        
        for key, description in self.required_keys.items():
            value = os.getenv(key)
            if value:
                logger.info(f"✅ {key}: Set")
                results[key] = True
            else:
                logger.warning(f"❌ {key}: Not set")
                results[key] = False
        
        for key, description in self.optional_keys.items():
            value = os.getenv(key)
            if value:
                logger.info(f"✅ {key}: Set (optional)")
                results[key] = True
            else:
                logger.info(f"⚠️ {key}: Not set (optional)")
                results[key] = False
        
        return results
    
    def show_setup_instructions(self):
        """Show setup instructions for missing keys"""
        logger.info("\n📋 API Key Setup Instructions:")
        logger.info("=" * 50)
        
        missing_required = [key for key in self.required_keys if not os.getenv(key)]
        missing_optional = [key for key in self.optional_keys if not os.getenv(key)]
        
        if missing_required:
            logger.info("\n🔑 Required API Keys:")
            for key in missing_required:
                logger.info(f"  {key}: {self.required_keys[key]}")
        
        if missing_optional:
            logger.info("\n🔑 Optional API Keys:")
            for key in missing_optional:
                logger.info(f"  {key}: {self.optional_keys[key]}")
        
        logger.info("\n📖 Full setup guide: FREE_API_SETUP.md")
    
    def create_env_file(self):
        """Create a .env file template"""
        env_content = """# AI Lead Generation Platform - Environment Variables
# Copy this file to .env and fill in your API keys

# Required APIs
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
OPENAI_API_KEY=your_openai_api_key_here
CLAUDE_API_KEY=your_claude_api_key_here

# Optional APIs
CLEARBIT_API_KEY=your_clearbit_api_key_here
HUNTER_API_KEY=your_hunter_api_key_here

# Application Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
"""
        
        try:
            with open('.env.template', 'w') as f:
                f.write(env_content)
            logger.info("✅ Created .env.template file")
            logger.info("📝 Copy it to .env and fill in your API keys")
        except Exception as e:
            logger.error(f"❌ Error creating .env.template: {str(e)}")
    
    async def test_apis(self):
        """Test all configured APIs"""
        logger.info("\n🧪 Testing API integrations...")
        
        # Import and run the API tester
        try:
            from test_all_apis import test_all_apis
            success = await test_all_apis()
            return success
        except ImportError:
            logger.error("❌ test_all_apis.py not found")
            return False
        except Exception as e:
            logger.error(f"❌ API testing failed: {str(e)}")
            return False
    
    def show_next_steps(self, has_required_keys: bool):
        """Show next steps based on current status"""
        if has_required_keys:
            logger.info("\n🎉 Great! You have the required API keys.")
            logger.info("\n🚀 Next steps:")
            logger.info("1. Test your APIs: python3 test_all_apis.py")
            logger.info("2. Test the platform: python3 free_lead_generator.py")
            logger.info("3. Deploy to Railway: railway up")
        else:
            logger.info("\n⚠️ You're missing some required API keys.")
            logger.info("\n🔧 Next steps:")
            logger.info("1. Get your API keys (see FREE_API_SETUP.md)")
            logger.info("2. Set them as environment variables")
            logger.info("3. Run this script again to test")

async def main():
    """Main setup function"""
    logger.info("🚀 AI Lead Generation Platform - API Key Setup")
    logger.info("=" * 60)
    
    setup = APIKeySetup()
    
    # Check current environment
    results = setup.check_environment()
    
    # Show setup instructions for missing keys
    setup.show_setup_instructions()
    
    # Create .env template
    setup.create_env_file()
    
    # Check if we have required keys
    required_keys = ["GOOGLE_API_KEY", "GOOGLE_SEARCH_ENGINE_ID", "OPENAI_API_KEY", "CLAUDE_API_KEY"]
    has_required = all(results.get(key, False) for key in required_keys)
    
    if has_required:
        logger.info("\n🧪 Testing your APIs...")
        success = await setup.test_apis()
        
        if success:
            logger.info("\n🎉 All APIs working! Ready to deploy!")
        else:
            logger.info("\n⚠️ Some APIs failed. Check your keys and try again.")
    else:
        logger.info("\n📋 Please set up your API keys first.")
        logger.info("See FREE_API_SETUP.md for detailed instructions.")
    
    # Show next steps
    setup.show_next_steps(has_required)

if __name__ == "__main__":
    asyncio.run(main())

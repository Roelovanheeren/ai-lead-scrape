#!/usr/bin/env python3
"""
Local Development Script for AI Lead Generation Platform
Tests basic functionality without external API dependencies
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_database_connection():
    """Test database connection"""
    try:
        from database.connection import DatabaseConnection
        
        # Use in-memory SQLite for testing if PostgreSQL not available
        db_url = os.getenv('DATABASE_URL', 'sqlite:///test.db')
        logger.info(f"Testing database connection: {db_url}")
        
        db = DatabaseConnection(db_url)
        await db.connect()
        
        # Test basic query
        result = await db.fetch_one("SELECT 1 as test")
        if result and result.get('test') == 1:
            logger.info("✅ Database connection successful")
            return True
        else:
            logger.error("❌ Database test query failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Database connection failed: {str(e)}")
        return False

async def test_api_endpoints():
    """Test basic API endpoints"""
    try:
        import httpx
        
        # Test health endpoint
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health")
            if response.status_code == 200:
                logger.info("✅ Health endpoint working")
                return True
            else:
                logger.error(f"❌ Health endpoint failed: {response.status_code}")
                return False
                
    except Exception as e:
        logger.error(f"❌ API endpoint test failed: {str(e)}")
        return False

async def test_basic_functionality():
    """Test basic platform functionality"""
    logger.info("🧪 Testing AI Lead Generation Platform locally...")
    
    # Test 1: Database Connection
    logger.info("1. Testing database connection...")
    db_ok = await test_database_connection()
    
    # Test 2: API Endpoints (if server is running)
    logger.info("2. Testing API endpoints...")
    api_ok = await test_api_endpoints()
    
    # Test 3: Basic imports
    logger.info("3. Testing module imports...")
    try:
        from models.schemas import JobCreate, JobResponse
        from services.job_orchestrator import JobOrchestrator
        from services.company_discovery import CompanyDiscoveryService
        logger.info("✅ All modules imported successfully")
        imports_ok = True
    except Exception as e:
        logger.error(f"❌ Module import failed: {str(e)}")
        imports_ok = False
    
    # Summary
    logger.info("\n📊 Test Results:")
    logger.info(f"Database: {'✅ PASS' if db_ok else '❌ FAIL'}")
    logger.info(f"API Endpoints: {'✅ PASS' if api_ok else '❌ FAIL'}")
    logger.info(f"Module Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    
    if db_ok and imports_ok:
        logger.info("\n🎉 Basic functionality test PASSED!")
        logger.info("Ready to proceed with API key setup and deployment.")
        return True
    else:
        logger.error("\n❌ Some tests failed. Please fix issues before proceeding.")
        return False

async def start_local_server():
    """Start the local development server"""
    try:
        import uvicorn
        
        logger.info("🚀 Starting local development server...")
        logger.info("Server will be available at: http://localhost:8000")
        logger.info("API documentation at: http://localhost:8000/docs")
        
        # Start the server
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start server: {str(e)}")
        return False

async def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Run tests
        await test_basic_functionality()
    elif len(sys.argv) > 1 and sys.argv[1] == "server":
        # Start server
        await start_local_server()
    else:
        # Show help
        print("""
🧪 AI Lead Generation Platform - Local Development

Usage:
  python local_dev.py test    - Run basic functionality tests
  python local_dev.py server  - Start local development server

Examples:
  python local_dev.py test
  python local_dev.py server
        """)

if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Simple test script for AI Lead Generation Platform
Tests basic functionality without complex imports
"""

import asyncio
import logging
import os
import sys

# Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_basic_imports():
    """Test basic Python imports"""
    try:
        # Test FastAPI
        from fastapi import FastAPI
        logger.info("✅ FastAPI imported successfully")
        
        # Test Pydantic
        from pydantic import BaseModel
        logger.info("✅ Pydantic imported successfully")
        
        # Test HTTP client
        import httpx
        logger.info("✅ HTTPX imported successfully")
        
        return True
    except Exception as e:
        logger.error(f"❌ Import test failed: {str(e)}")
        return False

async def test_sqlite_connection():
    """Test SQLite database connection"""
    try:
        import aiosqlite
        
        # Create a simple test database
        async with aiosqlite.connect("test.db") as db:
            await db.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT)")
            await db.execute("INSERT OR REPLACE INTO test (id, name) VALUES (1, 'test')")
            await db.commit()
            
            # Test query
            cursor = await db.execute("SELECT * FROM test WHERE id = 1")
            row = await cursor.fetchone()
            
            if row and row[1] == 'test':
                logger.info("✅ SQLite database test successful")
                return True
            else:
                logger.error("❌ SQLite test query failed")
                return False
                
    except Exception as e:
        logger.error(f"❌ SQLite test failed: {str(e)}")
        return False

async def test_fastapi_app():
    """Test creating a simple FastAPI app"""
    try:
        from fastapi import FastAPI
        
        app = FastAPI(title="Test App")
        
        @app.get("/")
        async def root():
            return {"message": "Hello World"}
        
        @app.get("/health")
        async def health():
            return {"status": "healthy"}
        
        logger.info("✅ FastAPI app created successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ FastAPI app test failed: {str(e)}")
        return False

async def test_pydantic_models():
    """Test Pydantic model creation"""
    try:
        from pydantic import BaseModel
        from typing import Optional
        from datetime import datetime
        
        class TestJob(BaseModel):
            id: str
            prompt: str
            status: str = "pending"
            created_at: datetime
            
        # Test model creation
        job = TestJob(
            id="test-123",
            prompt="Find SaaS companies",
            created_at=datetime.now()
        )
        
        # Test model validation
        assert job.id == "test-123"
        assert job.status == "pending"
        
        logger.info("✅ Pydantic models working correctly")
        return True
        
    except Exception as e:
        logger.error(f"❌ Pydantic model test failed: {str(e)}")
        return False

async def main():
    """Run all tests"""
    logger.info("🧪 Running simple functionality tests...")
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("SQLite Connection", test_sqlite_connection),
        ("FastAPI App", test_fastapi_app),
        ("Pydantic Models", test_pydantic_models),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n🔍 Testing {test_name}...")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ {test_name} failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n📊 Test Results:")
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\n🎯 Summary: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        logger.info("🎉 All tests passed! Ready for next steps.")
        return True
    else:
        logger.error("❌ Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    asyncio.run(main())

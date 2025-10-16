#!/usr/bin/env python3
"""
Railway startup script for AI Lead Generation Platform
Handles database initialization and application startup
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from database.railway_config import railway_db_config
from database.connection import init_database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def initialize_application():
    """Initialize the application for Railway deployment"""
    try:
        logger.info("Starting AI Lead Generation Platform on Railway...")
        
        # Test database connection
        logger.info("Testing database connection...")
        if not await railway_db_config.test_connection():
            logger.error("Database connection failed!")
            sys.exit(1)
        
        # Initialize database schema
        logger.info("Initializing database schema...")
        await railway_db_config.initialize_database()
        
        logger.info("Application initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"Application initialization failed: {str(e)}")
        sys.exit(1)

async def main():
    """Main startup function"""
    # Check if we're in Railway environment
    if os.getenv('RAILWAY_ENVIRONMENT'):
        logger.info("Running in Railway environment")
        await initialize_application()
    
    # Start the FastAPI application
    import uvicorn
    
    # Get port from Railway environment variable
    port = int(os.getenv('PORT', 8000))
    host = os.getenv('HOST', '0.0.0.0')
    
    logger.info(f"Starting server on {host}:{port}")
    
    # Run the application
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    asyncio.run(main())

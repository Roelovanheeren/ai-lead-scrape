#!/usr/bin/env python3
"""
Simple Railway startup script for AI Lead Generation Platform
"""

import os
import sys
import logging
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Start the FastAPI application"""
    try:
        logger.info("Starting AI Lead Generation Platform on Railway...")
        
        # Test imports first
        logger.info("Testing imports...")
        try:
            import uvicorn
            logger.info("✅ uvicorn imported successfully")
        except ImportError as e:
            logger.error(f"❌ Failed to import uvicorn: {e}")
            raise
        
        try:
            from main_simple import app
            logger.info("✅ main_simple imported successfully")
        except ImportError as e:
            logger.error(f"❌ Failed to import main_simple: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Error importing main_simple: {e}")
            raise
        
        logger.info("✅ All imports successful")
        
        # Get port from Railway environment variable
        port = int(os.getenv('PORT', 8000))
        host = os.getenv('HOST', '0.0.0.0')
        
        logger.info(f"Starting server on {host}:{port}")
        
        # Run the application
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

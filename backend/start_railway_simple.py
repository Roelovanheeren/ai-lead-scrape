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
        logger.info("🚀 Starting AI Lead Generation Platform on Railway...")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Working directory: {os.getcwd()}")
        logger.info(f"Environment variables: PORT={os.getenv('PORT')}, HOST={os.getenv('HOST')}")
        
        # Test imports first
        logger.info("🔍 Testing imports...")
        try:
            import uvicorn
            logger.info("✅ uvicorn imported successfully")
            logger.info(f"uvicorn version: {uvicorn.__version__}")
        except ImportError as e:
            logger.error(f"❌ Failed to import uvicorn: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Error importing uvicorn: {e}")
            raise
        
        try:
            logger.info("🔍 Importing main_simple...")
            from main_simple import app
            logger.info("✅ main_simple imported successfully")
            logger.info(f"App type: {type(app)}")
            logger.info(f"App object: {app}")
        except ImportError as e:
            logger.error(f"❌ Failed to import main_simple: {e}")
            logger.error(f"Import error details: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Error importing main_simple: {e}")
            logger.error(f"Exception type: {type(e)}")
            logger.error(f"Exception details: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
        
        logger.info("✅ All imports successful")
        
        # Get port from Railway environment variable
        port = int(os.getenv('PORT', 8000))
        host = os.getenv('HOST', '0.0.0.0')
        
        logger.info(f"🌐 Starting server on {host}:{port}")
        logger.info(f"App object: {app}")
        logger.info(f"App type: {type(app)}")
        
        # Test the app before starting
        try:
            logger.info("🔍 Testing app endpoints...")
            logger.info(f"App routes: {[route.path for route in app.routes]}")
            logger.info(f"Number of routes: {len(app.routes)}")
            
            # Test if we can access the root route
            logger.info("🔍 Testing root route...")
            for route in app.routes:
                if hasattr(route, 'path') and route.path == '/':
                    logger.info(f"✅ Found root route: {route}")
                    break
            else:
                logger.warning("⚠️ No root route found!")
            
            logger.info("✅ App is ready to start")
        except Exception as e:
            logger.error(f"❌ App test failed: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Don't raise - continue anyway
            logger.warning("⚠️ Continuing despite app test failure")
        
        # Run the application
        logger.info("🚀 Starting uvicorn server...")
        logger.info(f"uvicorn.run called with: host={host}, port={port}")
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=True,
            reload=False
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

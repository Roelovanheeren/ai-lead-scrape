"""
Railway-specific database configuration
Handles PostgreSQL connection for Railway deployment
"""

import os
import logging
from typing import Optional
import asyncpg
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class RailwayDatabaseConfig:
    """Railway database configuration"""
    
    def __init__(self):
        self.database_url = self._get_database_url()
        self.parsed_url = self._parse_database_url()
    
    def _get_database_url(self) -> str:
        """Get database URL from Railway environment variables"""
        # Railway provides DATABASE_URL automatically
        database_url = os.getenv('DATABASE_URL')
        
        if not database_url:
            # Fallback for local development
            database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/lead_generation')
            logger.warning("Using fallback database URL for local development")
        
        return database_url
    
    def _parse_database_url(self) -> dict:
        """Parse database URL into components"""
        try:
            parsed = urlparse(self.database_url)
            return {
                'host': parsed.hostname,
                'port': parsed.port or 5432,
                'database': parsed.path[1:],  # Remove leading slash
                'user': parsed.username,
                'password': parsed.password,
                'sslmode': 'require' if 'railway.app' in parsed.hostname else 'prefer'
            }
        except Exception as e:
            logger.error(f"Error parsing database URL: {str(e)}")
            return {}
    
    def get_connection_params(self) -> dict:
        """Get connection parameters for asyncpg"""
        return {
            'host': self.parsed_url.get('host'),
            'port': self.parsed_url.get('port'),
            'database': self.parsed_url.get('database'),
            'user': self.parsed_url.get('user'),
            'password': self.parsed_url.get('password'),
            'ssl': 'require' if self.parsed_url.get('sslmode') == 'require' else None
        }
    
    def get_connection_string(self) -> str:
        """Get connection string for SQLAlchemy"""
        return self.database_url
    
    async def test_connection(self) -> bool:
        """Test database connection"""
        try:
            params = self.get_connection_params()
            conn = await asyncpg.connect(**params)
            await conn.close()
            logger.info("Database connection successful")
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            return False
    
    async def initialize_database(self):
        """Initialize database with schema"""
        try:
            params = self.get_connection_params()
            conn = await asyncpg.connect(**params)
            
            # Read and execute schema
            schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
            if os.path.exists(schema_path):
                with open(schema_path, 'r') as f:
                    schema_sql = f.read()
                
                await conn.execute(schema_sql)
                logger.info("Database schema initialized successfully")
            else:
                logger.warning("Schema file not found, skipping initialization")
            
            await conn.close()
            
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise

# Global instance
railway_db_config = RailwayDatabaseConfig()

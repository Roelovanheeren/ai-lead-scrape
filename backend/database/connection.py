"""
Database Connection Module
Handles PostgreSQL database connections and operations
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Union
import asyncpg
from contextlib import asynccontextmanager
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Database connection handler for PostgreSQL"""
    
    def __init__(self, connection_string: Optional[str] = None):
        self.connection_string = connection_string or self._get_connection_string()
        self.pool = None
    
    def _get_connection_string(self) -> str:
        """Get database connection string from environment variables"""
        # Check for Railway DATABASE_URL first
        railway_url = os.getenv('DATABASE_URL')
        if railway_url:
            return railway_url
        
        # Fallback to individual environment variables
        return (
            f"postgresql://{os.getenv('DB_USER', 'postgres')}:"
            f"{os.getenv('DB_PASSWORD', 'password')}@"
            f"{os.getenv('DB_HOST', 'localhost')}:"
            f"{os.getenv('DB_PORT', '5432')}/"
            f"{os.getenv('DB_NAME', 'lead_generation')}"
        )
    
    async def connect(self):
        """Create database connection pool"""
        try:
            # Check if using SQLite for local development
            if self.connection_string.startswith('sqlite'):
                # For SQLite, we'll use aiosqlite instead of asyncpg
                import aiosqlite
                self.pool = None  # SQLite doesn't need connection pooling for testing
                logger.info("SQLite database connection configured")
            else:
                # PostgreSQL connection pool
                self.pool = await asyncpg.create_pool(
                    self.connection_string,
                    min_size=5,
                    max_size=20,
                    command_timeout=60
                )
                logger.info("PostgreSQL connection pool created")
        except Exception as e:
            logger.error(f"Error creating database connection pool: {str(e)}")
            raise
    
    async def disconnect(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get database connection from pool"""
        if not self.pool:
            await self.connect()
        
        async with self.pool.acquire() as connection:
            yield connection
    
    async def execute(self, query: str, *args) -> 'QueryResult':
        """Execute a query and return result"""
        try:
            async with self.get_connection() as connection:
                if query.strip().upper().startswith(('SELECT', 'WITH')):
                    result = await connection.fetch(query, *args)
                    return QueryResult(rows=result, rowcount=len(result))
                else:
                    result = await connection.execute(query, *args)
                    return QueryResult(rows=[], rowcount=int(result.split()[-1]) if result else 0)
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            raise
    
    async def fetch_one(self, query: str, *args) -> Optional[Dict[str, Any]]:
        """Fetch one row from database"""
        try:
            async with self.get_connection() as connection:
                result = await connection.fetchrow(query, *args)
                return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error fetching one row: {str(e)}")
            raise
    
    async def fetch_all(self, query: str, *args) -> List[Dict[str, Any]]:
        """Fetch all rows from database"""
        try:
            async with self.get_connection() as connection:
                results = await connection.fetch(query, *args)
                return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error fetching all rows: {str(e)}")
            raise
    
    async def fetch_many(self, query: str, size: int, *args) -> List[Dict[str, Any]]:
        """Fetch many rows from database with limit"""
        try:
            async with self.get_connection() as connection:
                results = await connection.fetch(query, *args)
                return [dict(row) for row in results[:size]]
        except Exception as e:
            logger.error(f"Error fetching many rows: {str(e)}")
            raise
    
    async def transaction(self):
        """Get database transaction context manager"""
        return DatabaseTransaction(self)

class DatabaseTransaction:
    """Database transaction handler"""
    
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self.connection = None
        self.transaction = None
    
    async def __aenter__(self):
        """Start transaction"""
        self.connection = await self.db.pool.acquire()
        self.transaction = self.connection.transaction()
        await self.transaction.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """End transaction"""
        try:
            if exc_type is None:
                await self.transaction.commit()
            else:
                await self.transaction.rollback()
        finally:
            await self.db.pool.release(self.connection)
    
    async def execute(self, query: str, *args) -> 'QueryResult':
        """Execute query within transaction"""
        try:
            if query.strip().upper().startswith(('SELECT', 'WITH')):
                result = await self.connection.fetch(query, *args)
                return QueryResult(rows=result, rowcount=len(result))
            else:
                result = await self.connection.execute(query, *args)
                return QueryResult(rows=[], rowcount=int(result.split()[-1]) if result else 0)
        except Exception as e:
            logger.error(f"Error executing query in transaction: {str(e)}")
            raise
    
    async def fetch_one(self, query: str, *args) -> Optional[Dict[str, Any]]:
        """Fetch one row within transaction"""
        try:
            result = await self.connection.fetchrow(query, *args)
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error fetching one row in transaction: {str(e)}")
            raise
    
    async def fetch_all(self, query: str, *args) -> List[Dict[str, Any]]:
        """Fetch all rows within transaction"""
        try:
            results = await self.connection.fetch(query, *args)
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error fetching all rows in transaction: {str(e)}")
            raise

class QueryResult:
    """Query result wrapper"""
    
    def __init__(self, rows: List[Dict[str, Any]], rowcount: int):
        self.rows = rows
        self.rowcount = rowcount
    
    def __iter__(self):
        return iter(self.rows)
    
    def __len__(self):
        return len(self.rows)
    
    def __getitem__(self, index):
        return self.rows[index]

# Global database connection instance
_db_connection: Optional[DatabaseConnection] = None

async def get_db() -> DatabaseConnection:
    """Get database connection instance"""
    global _db_connection
    
    if _db_connection is None:
        _db_connection = DatabaseConnection()
        await _db_connection.connect()
    
    return _db_connection

async def close_db():
    """Close database connection"""
    global _db_connection
    
    if _db_connection:
        await _db_connection.disconnect()
        _db_connection = None

# Database initialization
async def init_database():
    """Initialize database with schema"""
    try:
        db = DatabaseConnection()
        await db.connect()
        
        # Read and execute schema
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            
            await db.execute(schema_sql)
            logger.info("Database schema initialized")
        else:
            logger.warning("Schema file not found, skipping initialization")
        
        await db.disconnect()
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

# Database health check
async def check_database_health() -> bool:
    """Check database connection health"""
    try:
        db = DatabaseConnection()
        await db.connect()
        
        # Simple health check query
        result = await db.fetch_one("SELECT 1 as health_check")
        
        await db.disconnect()
        
        return result is not None and result.get('health_check') == 1
        
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False

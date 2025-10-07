"""
Project IRIS - Database Connection Manager
Supabase/PostgreSQL connection handling with connection pooling and error management
"""

import logging
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
import asyncio
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError, DisconnectionError, OperationalError
from sqlalchemy.pool import QueuePool
import time

from config import settings

logger = logging.getLogger(__name__)


class DatabaseClient:
    """Supabase/PostgreSQL database client with connection pooling and error handling"""

    def __init__(self):
        """Initialize the PostgreSQL client"""
        self.engine = None
        self.SessionLocal = None
        self._initialize_engine()

    def _initialize_engine(self):
        """Initialize SQLAlchemy engine with connection pooling"""
        try:
            import socket
            
            # Force IPv4 resolution for Supabase
            original_getaddrinfo = socket.getaddrinfo
            def getaddrinfo_ipv4_only(host, port, family=0, type=0, proto=0, flags=0):
                return original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
            socket.getaddrinfo = getaddrinfo_ipv4_only
            
            db_url = settings.database_url
            # Mask password for logging
            masked_url = db_url.replace(settings.supabase_db_password, "***") if settings.supabase_db_password else db_url
            logger.info(f"Initializing database connection to: {masked_url}")
            print(f"DEBUG: Database URL (masked): {masked_url}")
            print(f"DEBUG: Full URL length: {len(db_url)}")
            
            self.engine = create_engine(
                db_url,
                poolclass=QueuePool,
                pool_size=settings.db_pool_size,
                max_overflow=settings.db_max_overflow,
                pool_pre_ping=True,  # Verify connections before use
                pool_recycle=3600,   # Recycle connections after 1 hour
                echo=settings.is_development,  # Log SQL in development
                connect_args={
                    "connect_timeout": 30,
                    "application_name": "iris_forensic",
                    "options": "-c search_path=public"
                }
            )
            
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info("Database engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database engine: {e}")
            raise

    def test_connection(self) -> bool:
        """Test database connectivity"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                return result.scalar() == 1
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False

    @contextmanager
    def get_session(self):
        """Get a database session with automatic cleanup"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a raw SQL query and return results"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query), params or {})
                
                # Handle SELECT queries
                if result.returns_rows:
                    columns = result.keys()
                    rows = result.fetchall()
                    return [dict(zip(columns, row)) for row in rows]
                
                # Handle INSERT/UPDATE/DELETE queries
                return [{"affected_rows": result.rowcount}]
                
        except SQLAlchemyError as e:
            logger.error(f"SQL query execution failed: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during query execution: {e}")
            raise

    def execute_transaction(self, queries: List[Dict[str, Any]]) -> bool:
        """Execute multiple queries in a transaction"""
        try:
            with self.engine.begin() as conn:
                for query_info in queries:
                    query = query_info.get("query")
                    params = query_info.get("params", {})
                    
                    if not query:
                        raise ValueError("Query is required for each transaction item")
                    
                    conn.execute(text(query), params)
                
                logger.info(f"Transaction completed successfully with {len(queries)} queries")
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"Transaction failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during transaction: {e}")
            return False

    def check_table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database"""
        try:
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            return table_name in tables
        except Exception as e:
            logger.error(f"Error checking table existence: {e}")
            return False

    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get information about a table structure"""
        try:
            inspector = inspect(self.engine)
            
            if not self.check_table_exists(table_name):
                return {"exists": False}
            
            columns = inspector.get_columns(table_name)
            indexes = inspector.get_indexes(table_name)
            foreign_keys = inspector.get_foreign_keys(table_name)
            
            return {
                "exists": True,
                "columns": columns,
                "indexes": indexes,
                "foreign_keys": foreign_keys
            }
            
        except Exception as e:
            logger.error(f"Error getting table info for {table_name}: {e}")
            return {"exists": False, "error": str(e)}

    def execute_with_retry(self, query: str, params: Optional[Dict[str, Any]] = None, max_retries: int = 3) -> List[Dict[str, Any]]:
        """Execute query with retry logic for connection issues"""
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                return self.execute_query(query, params)
                
            except (DisconnectionError, OperationalError) as e:
                last_exception = e
                logger.warning(f"Database connection error on attempt {attempt + 1}: {e}")
                
                if attempt < max_retries - 1:
                    # Wait before retry with exponential backoff
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    
                    # Reinitialize engine on connection errors
                    try:
                        self._initialize_engine()
                    except Exception as init_error:
                        logger.error(f"Failed to reinitialize engine: {init_error}")
                        
            except Exception as e:
                # Don't retry for non-connection errors
                logger.error(f"Non-retryable error: {e}")
                raise
        
        # All retries exhausted
        logger.error(f"Query failed after {max_retries} attempts")
        raise last_exception

    def get_connection_info(self) -> Dict[str, Any]:
        """Get current connection pool information"""
        try:
            pool = self.engine.pool
            return {
                "pool_size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "invalid": pool.invalid(),
                "total_connections": pool.size() + pool.overflow()
            }
        except Exception as e:
            logger.error(f"Error getting connection info: {e}")
            return {"error": str(e)}

    def close_all_connections(self):
        """Close all database connections"""
        try:
            if self.engine:
                self.engine.dispose()
                logger.info("All database connections closed")
        except Exception as e:
            logger.error(f"Error closing connections: {e}")

    def __del__(self):
        """Cleanup on object destruction"""
        self.close_all_connections()


# Global database client instance
db_client = DatabaseClient()


def get_db_client() -> DatabaseClient:
    """Get the global database client instance"""
    return db_client


# Convenience functions
def execute_sql(query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Execute SQL query using the global client"""
    return db_client.execute_query(query, params)


def execute_transaction(queries: List[Dict[str, Any]]) -> bool:
    """Execute transaction using the global client"""
    return db_client.execute_transaction(queries)


def test_database_connection() -> bool:
    """Test database connection using the global client"""
    return db_client.test_connection()

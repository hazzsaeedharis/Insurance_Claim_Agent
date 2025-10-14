"""
Database connection manager for Insurance Claim Agent.
Provides connection pooling, transaction management, and common query patterns.
"""

import os
import sys
from typing import Optional, Dict, Any, List, Type, TypeVar, Generator
from contextlib import contextmanager
from datetime import datetime
import logging

from sqlalchemy import create_engine, text, MetaData, Table, inspect
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError
import psycopg2
from psycopg2.extras import RealDictCursor

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.common.config import get_settings
from services.common.logger import get_logger
from services.common.metrics import timer, increment

logger = get_logger(__name__)
settings = get_settings()

# SQLAlchemy Base
Base = declarative_base()

# Type variable for generic model operations
T = TypeVar('T', bound=Base)


class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize database manager.
        
        Args:
            database_url: Database URL (defaults to config settings)
        """
        self.database_url = database_url or settings.database.url
        self._engine = None
        self._session_factory = None
        self._metadata = MetaData()
        
    @property
    def engine(self):
        """Get or create database engine with connection pooling."""
        if self._engine is None:
            self._engine = create_engine(
                self.database_url,
                pool_size=settings.database.pool_size,
                max_overflow=settings.database.max_overflow,
                pool_timeout=settings.database.pool_timeout,
                pool_pre_ping=True,  # Verify connections before using
                echo=settings.app.debug,  # Log SQL in debug mode
                poolclass=QueuePool
            )
            logger.info("Database engine created with connection pooling")
        return self._engine
    
    @property
    def session_factory(self):
        """Get or create session factory."""
        if self._session_factory is None:
            self._session_factory = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False
            )
        return self._session_factory
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Get a database session with automatic cleanup.
        
        Usage:
            with db.get_session() as session:
                # Use session
                pass
        """
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def create_tables(self):
        """Create all tables defined in models."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except SQLAlchemyError as e:
            logger.error(f"Error creating tables: {e}")
            raise
    
    def drop_tables(self):
        """Drop all tables (use with caution!)."""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.warning("All database tables dropped")
        except SQLAlchemyError as e:
            logger.error(f"Error dropping tables: {e}")
            raise
    
    def execute_migration(self, migration_file: str):
        """
        Execute a SQL migration file.
        
        Args:
            migration_file: Path to SQL migration file
        """
        try:
            with open(migration_file, 'r') as f:
                migration_sql = f.read()
            
            with self.engine.connect() as conn:
                conn.execute(text(migration_sql))
                conn.commit()
            
            logger.info(f"Migration executed successfully: {migration_file}")
        except Exception as e:
            logger.error(f"Error executing migration {migration_file}: {e}")
            raise
    
    def health_check(self) -> bool:
        """Check database connectivity."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                return result.scalar() == 1
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


class DatabaseRepository:
    """Base repository class with common database operations."""
    
    def __init__(self, db_manager: DatabaseManager, model_class: Type[T]):
        """
        Initialize repository.
        
        Args:
            db_manager: Database manager instance
            model_class: SQLAlchemy model class
        """
        self.db = db_manager
        self.model_class = model_class
        self.logger = get_logger(f"{__name__}.{model_class.__name__}")
    
    @timer("db.query.create")
    def create(self, **kwargs) -> T:
        """Create a new record."""
        with self.db.get_session() as session:
            try:
                instance = self.model_class(**kwargs)
                session.add(instance)
                session.commit()
                session.refresh(instance)
                
                increment("db.record.created", labels={"table": self.model_class.__tablename__})
                self.logger.debug(f"Created {self.model_class.__name__} with id: {instance.id}")
                return instance
            except SQLAlchemyError as e:
                increment("db.error", labels={"operation": "create", "table": self.model_class.__tablename__})
                self.logger.error(f"Error creating {self.model_class.__name__}: {e}")
                raise
    
    @timer("db.query.get")
    def get(self, id: Any) -> Optional[T]:
        """Get a record by ID."""
        with self.db.get_session() as session:
            try:
                instance = session.query(self.model_class).filter_by(id=id).first()
                if instance:
                    increment("db.record.found", labels={"table": self.model_class.__tablename__})
                else:
                    increment("db.record.not_found", labels={"table": self.model_class.__tablename__})
                return instance
            except SQLAlchemyError as e:
                increment("db.error", labels={"operation": "get", "table": self.model_class.__tablename__})
                self.logger.error(f"Error getting {self.model_class.__name__} with id {id}: {e}")
                raise
    
    @timer("db.query.get_all")
    def get_all(self, limit: int = 100, offset: int = 0, **filters) -> List[T]:
        """Get all records with optional filtering."""
        with self.db.get_session() as session:
            try:
                query = session.query(self.model_class)
                
                # Apply filters
                for key, value in filters.items():
                    if hasattr(self.model_class, key):
                        query = query.filter(getattr(self.model_class, key) == value)
                
                # Apply pagination
                instances = query.limit(limit).offset(offset).all()
                
                increment("db.records.retrieved", value=len(instances), 
                         labels={"table": self.model_class.__tablename__})
                return instances
            except SQLAlchemyError as e:
                increment("db.error", labels={"operation": "get_all", "table": self.model_class.__tablename__})
                self.logger.error(f"Error getting all {self.model_class.__name__}: {e}")
                raise
    
    @timer("db.query.update")
    def update(self, id: Any, **kwargs) -> Optional[T]:
        """Update a record."""
        with self.db.get_session() as session:
            try:
                instance = session.query(self.model_class).filter_by(id=id).first()
                if not instance:
                    return None
                
                for key, value in kwargs.items():
                    if hasattr(instance, key):
                        setattr(instance, key, value)
                
                if hasattr(instance, 'updated_at'):
                    instance.updated_at = datetime.utcnow()
                
                session.commit()
                session.refresh(instance)
                
                increment("db.record.updated", labels={"table": self.model_class.__tablename__})
                self.logger.debug(f"Updated {self.model_class.__name__} with id: {id}")
                return instance
            except SQLAlchemyError as e:
                increment("db.error", labels={"operation": "update", "table": self.model_class.__tablename__})
                self.logger.error(f"Error updating {self.model_class.__name__} with id {id}: {e}")
                raise
    
    @timer("db.query.delete")
    def delete(self, id: Any) -> bool:
        """Delete a record."""
        with self.db.get_session() as session:
            try:
                instance = session.query(self.model_class).filter_by(id=id).first()
                if not instance:
                    return False
                
                session.delete(instance)
                session.commit()
                
                increment("db.record.deleted", labels={"table": self.model_class.__tablename__})
                self.logger.debug(f"Deleted {self.model_class.__name__} with id: {id}")
                return True
            except SQLAlchemyError as e:
                increment("db.error", labels={"operation": "delete", "table": self.model_class.__tablename__})
                self.logger.error(f"Error deleting {self.model_class.__name__} with id {id}: {e}")
                raise
    
    @timer("db.query.count")
    def count(self, **filters) -> int:
        """Count records with optional filtering."""
        with self.db.get_session() as session:
            try:
                query = session.query(self.model_class)
                
                # Apply filters
                for key, value in filters.items():
                    if hasattr(self.model_class, key):
                        query = query.filter(getattr(self.model_class, key) == value)
                
                count = query.count()
                return count
            except SQLAlchemyError as e:
                increment("db.error", labels={"operation": "count", "table": self.model_class.__tablename__})
                self.logger.error(f"Error counting {self.model_class.__name__}: {e}")
                raise
    
    def exists(self, **filters) -> bool:
        """Check if a record exists with given filters."""
        return self.count(**filters) > 0


class RawDatabaseConnection:
    """Direct database connection for complex queries."""
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize raw database connection."""
        self.database_url = database_url or settings.database.url
        self.logger = get_logger(__name__)
    
    @contextmanager
    def get_connection(self):
        """Get a raw psycopg2 connection."""
        conn = None
        try:
            conn = psycopg2.connect(self.database_url)
            yield conn
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    @contextmanager
    def get_cursor(self, cursor_factory=RealDictCursor):
        """Get a database cursor with automatic cleanup."""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=cursor_factory)
            try:
                yield cursor
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                cursor.close()
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results."""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_command(self, command: str, params: Optional[tuple] = None) -> int:
        """Execute an INSERT/UPDATE/DELETE command and return affected rows."""
        with self.get_cursor() as cursor:
            cursor.execute(command, params)
            return cursor.rowcount


# Global database manager instance
_db_manager = None


def get_db_manager() -> DatabaseManager:
    """Get global database manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


# Example usage
if __name__ == "__main__":
    # Test database connection
    db = get_db_manager()
    
    # Health check
    if db.health_check():
        print("✅ Database connection successful")
    else:
        print("❌ Database connection failed")
    
    # Test raw connection
    raw_db = RawDatabaseConnection()
    try:
        result = raw_db.execute_query("SELECT version()")
        print(f"PostgreSQL version: {result[0]['version']}")
    except Exception as e:
        print(f"Error: {e}")


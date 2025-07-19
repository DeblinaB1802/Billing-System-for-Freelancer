from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, TypeVar, Generic
from contextlib import contextmanager
import sqlite3
import logging
from config.database import db_manager
from Utils.exceptions import DatabaseError

T = TypeVar('T')
logger = logging.getLogger(__name__)

class BaseRepository(ABC, Generic[T]):
    """Base repository class implementing common CRUD operations."""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.db_manager = db_manager
    
    @contextmanager
    def get_connection(self):
        """Get database connection with error handling."""
        try:
            with self.db_manager.get_connection() as conn:
                yield conn
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            raise DatabaseError(f"Database operation failed: {e}")
    
    @abstractmethod
    def _row_to_model(self, row: sqlite3.Row) -> T:
        """Convert database row to model instance."""
        pass
    
    def find_by_id(self, id: int) -> Optional[T]:
        """Find record by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {self.table_name} WHERE id = ?", (id,))
            row = cursor.fetchone()
            return self._row_to_model(row) if row else None
    
    def find_all(self) -> List[T]:
        """Find all records."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {self.table_name} ORDER BY created_at DESC")
            rows = cursor.fetchall()
            return [self._row_to_model(row) for row in rows]
    
    def delete(self, id: int) -> bool:
        """Delete record by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {self.table_name} WHERE id = ?", (id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def count(self) -> int:
        """Count total records."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
            return cursor.fetchone()[0]

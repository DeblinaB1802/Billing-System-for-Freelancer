import sqlite3
import logging
from pathlib import Path
from typing import Optional
from contextlib import contextmanager
from .settings import settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connections and initialization."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.get_database_path()
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        """Ensure database file and directory exist."""
        db_path = Path(self.db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
    
    @contextmanager
    def get_connection(self):
        """Get database connection with context management."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        try:
            yield conn
        finally:
            conn.close()
    
    def initialize_database(self):
        """Initialize database with required tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Clients table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    phone TEXT,
                    company TEXT,
                    address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Projects table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    hourly_rate REAL,
                    fixed_rate REAL,
                    hours_worked REAL DEFAULT 0,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (client_id) REFERENCES clients (id)
                )
            ''')
            
            # Invoices table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_number TEXT UNIQUE NOT NULL,
                    client_id INTEGER NOT NULL,
                    project_id INTEGER,
                    subtotal REAL NOT NULL,
                    tax_amount REAL DEFAULT 0,
                    total_amount REAL NOT NULL,
                    status TEXT DEFAULT 'unpaid',
                    issue_date DATE NOT NULL,
                    due_date DATE NOT NULL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (client_id) REFERENCES clients (id),
                    FOREIGN KEY (project_id) REFERENCES projects (id)
                )
            ''')
            
            # Invoice items table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS invoice_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_id INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    rate REAL NOT NULL,
                    amount REAL NOT NULL,
                    FOREIGN KEY (invoice_id) REFERENCES invoices (id)
                )
            ''')
            
            # Payments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    payment_date DATE NOT NULL,
                    payment_method TEXT,
                    transaction_id TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (invoice_id) REFERENCES invoices (id)
                )
            ''')
            
            conn.commit()
            logger.info("Database initialized successfully")

# Global database manager instance
db_manager = DatabaseManager()
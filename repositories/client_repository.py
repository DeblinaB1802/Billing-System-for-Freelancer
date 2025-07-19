from typing import List, Optional
import sqlite3
from models.client import Client
from .base_repository import BaseRepository
from Utils.exceptions import DatabaseError

class ClientRepository(BaseRepository[Client]):
    """Repository for client data access."""
    
    def __init__(self):
        super().__init__("clients")
    
    def _row_to_model(self, row: sqlite3.Row) -> Client:
        """Convert database row to Client model."""
        return Client.from_dict(dict(row))
    
    def create(self, client: Client) -> Client:
        """Create new client."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO clients (name, email, phone, company, address)
                VALUES (?, ?, ?, ?, ?)
            ''', (client.name, client.email, client.phone, client.company, client.address))
            
            client.id = cursor.lastrowid
            conn.commit()
            return client
    
    def update(self, client: Client) -> Client:
        """Update existing client."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE clients 
                SET name = ?, email = ?, phone = ?, company = ?, address = ?, 
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (client.name, client.email, client.phone, client.company, 
                  client.address, client.id))
            
            conn.commit()
            if cursor.rowcount == 0:
                raise DatabaseError(f"Client with ID {client.id} not found")
            return client
    
    def find_by_email(self, email: str) -> Optional[Client]:
        """Find client by email."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clients WHERE email = ?", (email,))
            row = cursor.fetchone()
            return self._row_to_model(row) if row else None
    
    def search(self, query: str) -> List[Client]:
        """Search clients by name or company."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            search_pattern = f"%{query}%"
            cursor.execute('''
                SELECT * FROM clients 
                WHERE name LIKE ? OR company LIKE ?
                ORDER BY name
            ''', (search_pattern, search_pattern))
            rows = cursor.fetchall()
            return [self._row_to_model(row) for row in rows]
from typing import List, Optional
import sqlite3
from datetime import date
from models.invoice import Invoice, InvoiceItem, InvoiceStatus
from .base_repository import BaseRepository

class InvoiceRepository(BaseRepository[Invoice]):
    """Repository for invoice data access."""
    
    def __init__(self):
        super().__init__("invoices")
    
    def _row_to_model(self, row: sqlite3.Row) -> Invoice:
        """Convert database row to Invoice model."""
        invoice = Invoice.from_dict(dict(row))
        # Load invoice items
        invoice.items = self._load_invoice_items(invoice.id)
        return invoice
    
    def _load_invoice_items(self, invoice_id: int) -> List[InvoiceItem]:
        """Load items for an invoice."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT description, quantity, rate, amount 
                FROM invoice_items 
                WHERE invoice_id = ?
                ORDER BY id
            ''', (invoice_id,))
            rows = cursor.fetchall()
            return [InvoiceItem(row['description'], row['quantity'], row['rate']) 
                   for row in rows]
    
    def create(self, invoice: Invoice) -> Invoice:
        """Create new invoice with items."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Insert invoice
            cursor.execute('''
                INSERT INTO invoices 
                (invoice_number, client_id, project_id, subtotal, tax_amount, 
                 total_amount, status, issue_date, due_date, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (invoice.invoice_number, invoice.client_id, invoice.project_id,
                  invoice.subtotal, invoice.tax_amount, invoice.total_amount,
                  invoice.status.value, invoice.issue_date, invoice.due_date, 
                  invoice.notes))
            
            invoice.id = cursor.lastrowid
            
            # Insert invoice items
            for item in invoice.items:
                cursor.execute('''
                    INSERT INTO invoice_items 
                    (invoice_id, description, quantity, rate, amount)
                    VALUES (?, ?, ?, ?, ?)
                ''', (invoice.id, item.description, item.quantity, 
                      item.rate, item.amount))
            
            conn.commit()
            return invoice
    
    def update_status(self, invoice_id: int, status: InvoiceStatus) -> bool:
        """Update invoice status."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE invoices 
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (status.value, invoice_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def find_by_client(self, client_id: int) -> List[Invoice]:
        """Find invoices by client."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM invoices 
                WHERE client_id = ? 
                ORDER BY created_at DESC
            ''', (client_id,))
            rows = cursor.fetchall()
            return [self._row_to_model(row) for row in rows]
    
    def find_overdue(self) -> List[Invoice]:
        """Find overdue invoices."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM invoices 
                WHERE due_date < ? AND status NOT IN ('paid', 'cancelled')
                ORDER BY due_date
            ''', (date.today(),))
            rows = cursor.fetchall()
            return [self._row_to_model(row) for row in rows]
    
    def get_monthly_revenue(self, year: int, month: int) -> float:
        """Get total revenue for a month."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT SUM(total_amount) as revenue
                FROM invoices 
                WHERE status = 'paid' 
                AND strftime('%Y', issue_date) = ?
                AND strftime('%m', issue_date) = ?
            ''', (str(year), f"{month:02d}"))
            result = cursor.fetchone()
            return result['revenue'] or 0.0
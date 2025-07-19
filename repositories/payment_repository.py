from typing import List, Optional
import sqlite3
from datetime import date, datetime, timedelta
from models.payment import Payment, PaymentMethod
from .base_repository import BaseRepository
from Utils.exceptions import DatabaseError

class PaymentRepository(BaseRepository[Payment]):
    """Repository for payment data access."""
    
    def __init__(self):
        super().__init__("payments")
    
    def _row_to_model(self, row: sqlite3.Row) -> Payment:
        """Convert database row to Payment model."""
        return Payment.from_dict(dict(row))
    
    def create(self, payment: Payment) -> Payment:
        """Create new payment record."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO payments (invoice_id, amount, payment_date, 
                                    payment_method, transaction_id, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (payment.invoice_id, payment.amount, payment.payment_date,
                  payment.payment_method.value if payment.payment_method else None,
                  payment.transaction_id, payment.notes))
            
            payment.id = cursor.lastrowid
            conn.commit()
            return payment
    
    def update(self, payment: Payment) -> Payment:
        """Update existing payment."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE payments 
                SET amount = ?, payment_date = ?, payment_method = ?, 
                    transaction_id = ?, notes = ?
                WHERE id = ?
            ''', (payment.amount, payment.payment_date,
                  payment.payment_method.value if payment.payment_method else None,
                  payment.transaction_id, payment.notes, payment.id))
            
            conn.commit()
            if cursor.rowcount == 0:
                raise DatabaseError(f"Payment with ID {payment.id} not found")
            return payment
    
    def find_by_invoice(self, invoice_id: int) -> List[Payment]:
        """Find all payments for an invoice."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM payments 
                WHERE invoice_id = ? 
                ORDER BY payment_date DESC
            ''', (invoice_id,))
            rows = cursor.fetchall()
            return [self._row_to_model(row) for row in rows]
    
    def get_total_paid_for_invoice(self, invoice_id: int) -> float:
        """Get total amount paid for an invoice."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT SUM(amount) as total_paid 
                FROM payments 
                WHERE invoice_id = ?
            ''', (invoice_id,))
            result = cursor.fetchone()
            return result['total_paid'] or 0.0
    
    def find_by_date_range(self, start_date: date, end_date: date) -> List[Payment]:
        """Find payments within date range."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM payments 
                WHERE payment_date BETWEEN ? AND ?
                ORDER BY payment_date DESC
            ''', (start_date, end_date))
            rows = cursor.fetchall()
            return [self._row_to_model(row) for row in rows]
    
    def get_monthly_payments(self, year: int, month: int) -> List[Payment]:
        """Get all payments for a specific month."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM payments 
                WHERE strftime('%Y', payment_date) = ?
                AND strftime('%m', payment_date) = ?
                ORDER BY payment_date DESC
            ''', (str(year), f"{month:02d}"))
            rows = cursor.fetchall()
            return [self._row_to_model(row) for row in rows]
    
    def get_payment_summary(self, start_date: date, end_date: date) -> dict:
        """Get payment summary for date range."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total payments
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_payments,
                    SUM(amount) as total_amount,
                    AVG(amount) as avg_amount
                FROM payments 
                WHERE payment_date BETWEEN ? AND ?
            ''', (start_date, end_date))
            summary = dict(cursor.fetchone())
            
            # Payments by method
            cursor.execute('''
                SELECT 
                    payment_method,
                    COUNT(*) as count,
                    SUM(amount) as amount
                FROM payments 
                WHERE payment_date BETWEEN ? AND ?
                GROUP BY payment_method
                ORDER BY amount DESC
            ''', (start_date, end_date))
            
            summary['by_method'] = [dict(row) for row in cursor.fetchall()]
            
            return summary
    
    def get_recent_payments(self, days: int = 30) -> List[Payment]:
        """Get payments from last N days."""
        start_date = date.today() - timedelta(days=days)
        return self.find_by_date_range(start_date, date.today())
    
    def find_by_transaction_id(self, transaction_id: str) -> Optional[Payment]:
        """Find payment by transaction ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM payments 
                WHERE transaction_id = ?
            ''', (transaction_id,))
            row = cursor.fetchone()
            return self._row_to_model(row) if row else None
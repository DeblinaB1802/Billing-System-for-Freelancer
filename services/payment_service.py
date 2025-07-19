from typing import List, Optional
import logging
from datetime import date
from models.payment import Payment, PaymentMethod
from models.invoice import InvoiceStatus
from repositories.payment_repository import PaymentRepository
from repositories.invoice_repository import InvoiceRepository
from Utils.exceptions import PaymentNotFoundError, InvoiceNotFoundError, ValidationError

logger = logging.getLogger(__name__)

class PaymentService:
    """Service for payment business logic."""
    
    def __init__(self):
        self.repository = PaymentRepository()
        self.invoice_repository = InvoiceRepository()
    
    def record_payment(self, invoice_id: int, amount: float, 
                      payment_date: date = None, payment_method: PaymentMethod = None,
                      transaction_id: str = None, notes: str = None) -> Payment:
        """Record a new payment for an invoice."""
        # Validate invoice exists
        invoice = self.invoice_repository.find_by_id(invoice_id)
        if not invoice:
            raise InvoiceNotFoundError(f"Invoice with ID {invoice_id} not found")
        
        if invoice.status == InvoiceStatus.CANCELLED:
            raise ValidationError("Cannot add payment to cancelled invoice")
        
        if amount <= 0:
            raise ValidationError("Payment amount must be positive")
        
        # Check if payment exceeds remaining amount
        total_paid = self.repository.get_total_paid_for_invoice(invoice_id)
        remaining_amount = invoice.total_amount - total_paid
        
        if amount > remaining_amount:
            raise ValidationError(f"Payment amount (₹{amount:.2f}) exceeds remaining "
                                f"balance (₹{remaining_amount:.2f})")
        
        # Check for duplicate transaction ID
        if transaction_id:
            existing_payment = self.repository.find_by_transaction_id(transaction_id)
            if existing_payment:
                raise ValidationError(f"Payment with transaction ID '{transaction_id}' already exists")
        
        payment = Payment(
            invoice_id=invoice_id,
            amount=amount,
            payment_date=payment_date or date.today(),
            payment_method=payment_method,
            transaction_id=transaction_id.strip() if transaction_id else None,
            notes=notes.strip() if notes else None
        )
        
        created_payment = self.repository.create(payment)
        
        # Update invoice status if fully paid
        new_total_paid = total_paid + amount
        if new_total_paid >= invoice.total_amount:
            self.invoice_repository.update_status(invoice_id, InvoiceStatus.PAID)
            logger.info(f"Invoice {invoice.invoice_number} marked as fully paid")
        elif invoice.status == InvoiceStatus.DRAFT:
            self.invoice_repository.update_status(invoice_id, InvoiceStatus.PARTIALLY_PAID)
        
        logger.info(f"Recorded payment of ₹{amount:.2f} for invoice {invoice.invoice_number}")
        return created_payment
    
    def update_payment(self, payment_id: int, amount: float = None,
                      payment_date: date = None, payment_method: PaymentMethod = None,
                      transaction_id: str = None, notes: str = None) -> Payment:
        """Update an existing payment."""
        payment = self.repository.find_by_id(payment_id)
        if not payment:
            raise PaymentNotFoundError(f"Payment with ID {payment_id} not found")
        
        # Store original amount for invoice status recalculation
        original_amount = payment.amount
        
        # Update provided fields
        if amount is not None:
            if amount <= 0:
                raise ValidationError("Payment amount must be positive")
            
            # Check if new amount is valid
            invoice = self.invoice_repository.find_by_id(payment.invoice_id)
            total_paid = self.repository.get_total_paid_for_invoice(payment.invoice_id)
            # Subtract original amount and add new amount
            new_total = total_paid - original_amount + amount
            
            if new_total > invoice.total_amount:
                raise ValidationError(f"Updated payment amount would exceed invoice total")
            
            payment.amount = amount
        
        if payment_date is not None:
            payment.payment_date = payment_date
        if payment_method is not None:
            payment.payment_method = payment_method
        if transaction_id is not None:
            # Check for duplicate transaction ID (excluding current payment)
            existing = self.repository.find_by_transaction_id(transaction_id.strip())
            if existing and existing.id != payment_id:
                raise ValidationError(f"Payment with transaction ID '{transaction_id}' already exists")
            payment.transaction_id = transaction_id.strip() if transaction_id else None
        if notes is not None:
            payment.notes = notes.strip() if notes else None
        
        updated_payment = self.repository.update(payment)
        
        # Recalculate invoice payment status
        self._update_invoice_payment_status(payment.invoice_id)
        
        logger.info(f"Updated payment ID {payment_id}")
        return updated_payment
    
    def delete_payment(self, payment_id: int) -> bool:
        """Delete a payment record."""
        payment = self.repository.find_by_id(payment_id)
        if not payment:
            raise PaymentNotFoundError(f"Payment with ID {payment_id} not found")
        
        invoice_id = payment.invoice_id
        success = self.repository.delete(payment_id)
        
        if success:
            # Recalculate invoice payment status
            self._update_invoice_payment_status(invoice_id)
            logger.info(f"Deleted payment ID {payment_id}")
        
        return success
    
    def _update_invoice_payment_status(self, invoice_id: int):
        """Update invoice payment status based on payments."""
        invoice = self.invoice_repository.find_by_id(invoice_id)
        total_paid = self.repository.get_total_paid_for_invoice(invoice_id)
        
        if total_paid == 0:
            new_status = InvoiceStatus.SENT if invoice.status == InvoiceStatus.PARTIALLY_PAID else invoice.status
        elif total_paid >= invoice.total_amount:
            new_status = InvoiceStatus.PAID
        else:
            new_status = InvoiceStatus.PARTIALLY_PAID
        
        if new_status != invoice.status:
            self.invoice_repository.update_status(invoice_id, new_status)
    
    def get_payment(self, payment_id: int) -> Payment:
        """Get payment by ID."""
        payment = self.repository.find_by_id(payment_id)
        if not payment:
            raise PaymentNotFoundError(f"Payment with ID {payment_id} not found")
        return payment
    
    def get_all_payments(self) -> List[Payment]:
        """Get all payments."""
        return self.repository.find_all()
    
    def get_invoice_payments(self, invoice_id: int) -> List[Payment]:
        """Get all payments for an invoice."""
        return self.repository.find_by_invoice(invoice_id)
    
    def get_payments_by_date_range(self, start_date: date, end_date: date) -> List[Payment]:
        """Get payments within date range."""
        return self.repository.find_by_date_range(start_date, end_date)
    
    def get_recent_payments(self, days: int = 30) -> List[Payment]:
        """Get recent payments."""
        return self.repository.get_recent_payments(days)
    
    def get_payment_summary(self, start_date: date, end_date: date) -> dict:
        """Get payment summary for date range."""
        return self.repository.get_payment_summary(start_date, end_date)
    
    def get_invoice_payment_status(self, invoice_id: int) -> dict:
        """Get payment status for an invoice."""
        invoice = self.invoice_repository.find_by_id(invoice_id)
        if not invoice:
            raise InvoiceNotFoundError(f"Invoice with ID {invoice_id} not found")
        
        total_paid = self.repository.get_total_paid_for_invoice(invoice_id)
        remaining = invoice.total_amount - total_paid
        
        return {
            'invoice_id': invoice_id,
            'invoice_number': invoice.invoice_number,
            'total_amount': invoice.total_amount,
            'amount_paid': total_paid,
            'amount_remaining': remaining,
            'is_fully_paid': remaining <= 0,
            'payment_percentage': (total_paid / invoice.total_amount * 100) if invoice.total_amount > 0 else 0
        }
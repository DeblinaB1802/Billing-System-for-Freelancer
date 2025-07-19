from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime, date
from enum import Enum
from decimal import Decimal
from .base import BaseModel
from Utils.exceptions import ValidationError

class PaymentMethod(Enum):
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    CHEQUE = "cheque"
    UPI = "upi"
    CARD = "card"
    OTHER = "other"

class PaymentStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Payment(BaseModel):
    """Payment model for tracking invoice payments."""
    invoice_id: int = 0
    client_id: int = 0
    amount: Decimal = field(default_factory=lambda: Decimal('0.00'))
    payment_date: date = field(default_factory=date.today)
    payment_method: PaymentMethod = PaymentMethod.BANK_TRANSFER
    status: PaymentStatus = PaymentStatus.PENDING
    reference_number: Optional[str] = None
    notes: Optional[str] = None
    transaction_fee: Decimal = field(default_factory=lambda: Decimal('0.00'))
    net_amount: Decimal = field(default_factory=lambda: Decimal('0.00'))
    
    def __post_init__(self):
        """Validate payment data after initialization."""
        if self.invoice_id <= 0:
            raise ValidationError("Valid invoice ID is required")
        
        if self.client_id <= 0:
            raise ValidationError("Valid client ID is required")
        
        if self.amount <= 0:
            raise ValidationError("Payment amount must be positive")
        
        # Calculate net amount (amount minus transaction fee)
        self.calculate_net_amount()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Payment':
        """Create Payment instance from dictionary."""
        # Handle payment method
        payment_method = data.get('payment_method', 'bank_transfer')
        if isinstance(payment_method, str):
            payment_method = PaymentMethod(payment_method)
        
        # Handle payment status
        status = data.get('status', 'pending')
        if isinstance(status, str):
            status = PaymentStatus(status)
        
        # Parse payment date
        payment_date = data.get('payment_date')
        if isinstance(payment_date, str):
            payment_date = datetime.fromisoformat(payment_date).date()
        
        # Handle decimal amounts
        amount = data.get('amount', '0.00')
        if isinstance(amount, (int, float, str)):
            amount = Decimal(str(amount))
        
        transaction_fee = data.get('transaction_fee', '0.00')
        if isinstance(transaction_fee, (int, float, str)):
            transaction_fee = Decimal(str(transaction_fee))
        
        net_amount = data.get('net_amount', '0.00')
        if isinstance(net_amount, (int, float, str)):
            net_amount = Decimal(str(net_amount))
        
        return cls(
            id=data.get('id'),
            invoice_id=data.get('invoice_id', 0),
            client_id=data.get('client_id', 0),
            amount=amount,
            payment_date=payment_date or date.today(),
            payment_method=payment_method,
            status=status,
            reference_number=data.get('reference_number'),
            notes=data.get('notes'),
            transaction_fee=transaction_fee,
            net_amount=net_amount,
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def calculate_net_amount(self):
        """Calculate net amount after deducting transaction fees."""
        self.net_amount = self.amount - self.transaction_fee
        self.update_timestamp()
    
    def mark_as_completed(self, reference_number: Optional[str] = None):
        """Mark payment as completed."""
        self.status = PaymentStatus.COMPLETED
        if reference_number:
            self.reference_number = reference_number
        self.update_timestamp()
    
    def mark_as_failed(self, reason: Optional[str] = None):
        """Mark payment as failed."""
        self.status = PaymentStatus.FAILED
        if reason:
            self.notes = f"Failed: {reason}" if not self.notes else f"{self.notes}. Failed: {reason}"
        self.update_timestamp()
    
    def cancel_payment(self, reason: Optional[str] = None):
        """Cancel the payment."""
        if self.status == PaymentStatus.COMPLETED:
            raise ValidationError("Cannot cancel a completed payment")
        
        self.status = PaymentStatus.CANCELLED
        if reason:
            self.notes = f"Cancelled: {reason}" if not self.notes else f"{self.notes}. Cancelled: {reason}"
        self.update_timestamp()
    
    def set_transaction_fee(self, fee: Decimal):
        """Set transaction fee and recalculate net amount."""
        if fee < 0:
            raise ValidationError("Transaction fee cannot be negative")
        
        if fee > self.amount:
            raise ValidationError("Transaction fee cannot exceed payment amount")
        
        self.transaction_fee = fee
        self.calculate_net_amount()
    
    def is_partial_payment(self, invoice_total: Decimal) -> bool:
        """Check if this is a partial payment."""
        return self.amount < invoice_total
    
    def get_payment_method_display(self) -> str:
        """Get display name for payment method."""
        method_names = {
            PaymentMethod.CASH: "Cash",
            PaymentMethod.BANK_TRANSFER: "Bank Transfer",
            PaymentMethod.CHEQUE: "Cheque",
            PaymentMethod.UPI: "UPI",
            PaymentMethod.CARD: "Credit/Debit Card",
            PaymentMethod.OTHER: "Other"
        }
        return method_names.get(self.payment_method, "Unknown")
    
    def get_status_display(self) -> str:
        """Get display name for payment status."""
        status_names = {
            PaymentStatus.PENDING: "Pending",
            PaymentStatus.COMPLETED: "Completed",
            PaymentStatus.FAILED: "Failed",
            PaymentStatus.CANCELLED: "Cancelled"
        }
        return status_names.get(self.status, "Unknown")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert payment to dictionary with proper serialization."""
        result = super().to_dict()
        
        # Convert Decimal to string for JSON serialization
        if isinstance(result.get('amount'), Decimal):
            result['amount'] = str(result['amount'])
        if isinstance(result.get('transaction_fee'), Decimal):
            result['transaction_fee'] = str(result['transaction_fee'])
        if isinstance(result.get('net_amount'), Decimal):
            result['net_amount'] = str(result['net_amount'])
        
        # Convert enums to string values
        if isinstance(result.get('payment_method'), PaymentMethod):
            result['payment_method'] = result['payment_method'].value
        if isinstance(result.get('status'), PaymentStatus):
            result['status'] = result['status'].value
        
        return result
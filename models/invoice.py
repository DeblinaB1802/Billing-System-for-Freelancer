from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime, date
from enum import Enum
from .base import BaseModel
from config.settings import settings
from Utils.exceptions import ValidationError

class InvoiceStatus(Enum):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

@dataclass
class InvoiceItem:
    """Individual item on an invoice."""
    description: str
    quantity: float
    rate: float
    amount: float = field(init=False)
    
    def __post_init__(self):
        self.amount = self.quantity * self.rate

@dataclass
class Invoice(BaseModel):
    """Invoice model for billing clients."""
    invoice_number: str = ""
    client_id: int = 0
    project_id: Optional[int] = None
    items: List[InvoiceItem] = field(default_factory=list)
    subtotal: float = 0.0
    tax_amount: float = 0.0
    total_amount: float = 0.0
    status: InvoiceStatus = InvoiceStatus.DRAFT
    issue_date: date = field(default_factory=date.today)
    due_date: date = field(default_factory=lambda: date.today())
    notes: Optional[str] = None
    
    def __post_init__(self):
        """Validate and calculate invoice totals."""
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        
        if self.client_id <= 0:
            raise ValidationError("Valid client ID is required")
        
        self.calculate_totals()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Invoice':
        """Create Invoice instance from dictionary."""
        status = data.get('status', 'draft')
        if isinstance(status, str):
            status = InvoiceStatus(status)
        
        # Parse dates
        issue_date = data.get('issue_date')
        if isinstance(issue_date, str):
            issue_date = datetime.fromisoformat(issue_date).date()
        
        due_date = data.get('due_date')
        if isinstance(due_date, str):
            due_date = datetime.fromisoformat(due_date).date()
        
        return cls(
            id=data.get('id'),
            invoice_number=data.get('invoice_number', ''),
            client_id=data.get('client_id', 0),
            project_id=data.get('project_id'),
            subtotal=data.get('subtotal', 0.0),
            tax_amount=data.get('tax_amount', 0.0),
            total_amount=data.get('total_amount', 0.0),
            status=status,
            issue_date=issue_date or date.today(),
            due_date=due_date or date.today(),
            notes=data.get('notes'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def generate_invoice_number(self) -> str:
        """Generate unique invoice number."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{settings.invoice.invoice_prefix}-{timestamp}"
    
    def add_item(self, description: str, quantity: float, rate: float):
        """Add item to invoice."""
        if not description.strip():
            raise ValidationError("Item description is required")
        if quantity <= 0:
            raise ValidationError("Quantity must be positive")
        if rate < 0:
            raise ValidationError("Rate must be non-negative")
        
        item = InvoiceItem(description, quantity, rate)
        self.items.append(item)
        self.calculate_totals()
    
    def calculate_totals(self):
        """Calculate invoice totals."""
        self.subtotal = sum(item.amount for item in self.items)
        self.tax_amount = self.subtotal * settings.invoice.tax_rate
        self.total_amount = self.subtotal + self.tax_amount
        self.update_timestamp()
    
    def mark_as_paid(self):
        """Mark invoice as paid."""
        self.status = InvoiceStatus.PAID
        self.update_timestamp()
    
    def is_overdue(self) -> bool:
        """Check if invoice is overdue."""
        return (
            self.status not in [InvoiceStatus.PAID, InvoiceStatus.CANCELLED] 
            and self.due_date < date.today())
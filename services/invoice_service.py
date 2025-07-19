from typing import List, Optional, Dict, Any
import logging
from datetime import date, timedelta
from models.invoice import Invoice, InvoiceStatus
from models.client import Client
from models.project import Project
from repositories.invoice_repository import InvoiceRepository
from repositories.client_repository import ClientRepository
from repositories.project_repository import ProjectRepository
from Utils.exceptions import InvoiceNotFoundError, ClientNotFoundError, ValidationError

logger = logging.getLogger(__name__)

class InvoiceService:
    """Service for invoice business logic."""
    
    def __init__(self):
        self.repository = InvoiceRepository()
        self.client_repository = ClientRepository()
        self.project_repository = ProjectRepository()
    
    def create_invoice(self, client_id: int, project_id: int = None, 
                      due_days: int = 30, notes: str = None) -> Invoice:
        """Create a new invoice."""
        # Validate client exists
        client = self.client_repository.find_by_id(client_id)
        if not client:
            raise ClientNotFoundError(f"Client with ID {client_id} not found")
        
        # Validate project if provided
        project = None
        if project_id:
            project = self.project_repository.find_by_id(project_id)
            if not project:
                raise ValidationError(f"Project with ID {project_id} not found")
            if project.client_id != client_id:
                raise ValidationError("Project does not belong to the specified client")
        
        # Create invoice
        invoice = Invoice(
            client_id=client_id,
            project_id=project_id,
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=due_days),
            notes=notes
        )
        
        # If project is specified, add project work as invoice item
        if project:
            amount = project.calculate_amount()
            if amount > 0:
                description = f"Work on project: {project.name}"
                if project.hourly_rate:
                    description += f" ({project.hours_worked} hours @ ₹{project.hourly_rate}/hr)"
                invoice.add_item(description, 1, amount)
        
        created_invoice = self.repository.create(invoice)
        logger.info(f"Created invoice {created_invoice.invoice_number} for client {client.display_name()}")
        return created_invoice
    
    def add_invoice_item(self, invoice_id: int, description: str, 
                        quantity: float, rate: float) -> Invoice:
        """Add item to existing invoice."""
        invoice = self.repository.find_by_id(invoice_id)
        if not invoice:
            raise InvoiceNotFoundError(f"Invoice with ID {invoice_id} not found")
        
        if invoice.status != InvoiceStatus.DRAFT:
            raise ValidationError("Can only add items to draft invoices")
        
        invoice.add_item(description, quantity, rate)
        # Update invoice in database
        updated_invoice = self.repository.update(invoice)
        logger.info(f"Added item to invoice {invoice.invoice_number}")
        return updated_invoice
    
    def mark_invoice_paid(self, invoice_id: int) -> Invoice:
        """Mark invoice as paid."""
        invoice = self.repository.find_by_id(invoice_id)
        if not invoice:
            raise InvoiceNotFoundError(f"Invoice with ID {invoice_id} not found")
        
        if invoice.status == InvoiceStatus.PAID:
            raise ValidationError("Invoice is already marked as paid")
        
        invoice.mark_as_paid()
        self.repository.update_status(invoice_id, InvoiceStatus.PAID)
        logger.info(f"Marked invoice {invoice.invoice_number} as paid")
        return invoice
    
    def send_invoice(self, invoice_id: int) -> Invoice:
        """Mark invoice as sent."""
        invoice = self.repository.find_by_id(invoice_id)
        if not invoice:
            raise InvoiceNotFoundError(f"Invoice with ID {invoice_id} not found")
        
        if invoice.status not in [InvoiceStatus.DRAFT, InvoiceStatus.SENT]:
            raise ValidationError("Can only send draft or previously sent invoices")
        
        self.repository.update_status(invoice_id, InvoiceStatus.SENT)
        logger.info(f"Marked invoice {invoice.invoice_number} as sent")
        return invoice
    
    def get_invoice(self, invoice_id: int) -> Invoice:
        """Get invoice by ID."""
        invoice = self.repository.find_by_id(invoice_id)
        if not invoice:
            raise InvoiceNotFoundError(f"Invoice with ID {invoice_id} not found")
        return invoice
    
    def get_all_invoices(self) -> List[Invoice]:
        """Get all invoices."""
        return self.repository.find_all()
    
    def get_client_invoices(self, client_id: int) -> List[Invoice]:
        """Get invoices for a specific client."""
        return self.repository.find_by_client(client_id)
    
    def get_overdue_invoices(self) -> List[Invoice]:
        """Get overdue invoices."""
        return self.repository.find_overdue()
    
    def get_invoice_summary(self) -> Dict[str, Any]:
        """Get invoice summary statistics."""
        all_invoices = self.repository.find_all()
        
        total_invoices = len(all_invoices)
        paid_invoices = sum(1 for inv in all_invoices if inv.status == InvoiceStatus.PAID)
        overdue_invoices = sum(1 for inv in all_invoices if inv.is_overdue())
        
        total_revenue = sum(inv.total_amount for inv in all_invoices if inv.status == InvoiceStatus.PAID)
        outstanding_amount = sum(inv.total_amount for inv in all_invoices 
                               if inv.status not in [InvoiceStatus.PAID, InvoiceStatus.CANCELLED])
        
        return {
            'total_invoices': total_invoices,
            'paid_invoices': paid_invoices,
            'overdue_invoices': overdue_invoices,
            'total_revenue': total_revenue,
            'outstanding_amount': outstanding_amount,
            'payment_rate': (paid_invoices / total_invoices * 100) if total_invoices > 0 else 0
        }
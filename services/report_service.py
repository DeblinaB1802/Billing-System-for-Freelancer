from typing import Dict, List, Any
from datetime import date, datetime
from calendar import monthrange
from repositories.invoice_repository import InvoiceRepository
from repositories.client_repository import ClientRepository
from models.invoice import InvoiceStatus

class ReportService:
    """Service for generating reports."""
    
    def __init__(self):
        self.invoice_repository = InvoiceRepository()
        self.client_repository = ClientRepository()
    
    def get_monthly_report(self, year: int, month: int) -> Dict[str, Any]:
        """Generate monthly revenue report."""
        # Get total revenue for the month
        revenue = self.invoice_repository.get_monthly_revenue(year, month)
        
        # Get all invoices for the month
        start_date = date(year, month, 1)
        _, last_day = monthrange(year, month)
        end_date = date(year, month, last_day)
        
        invoices = []
        for invoice in self.invoice_repository.find_all():
            if start_date <= invoice.issue_date <= end_date:
                invoices.append(invoice)
        
        # Calculate statistics
        total_invoices = len(invoices)
        paid_invoices = sum(1 for inv in invoices if inv.status == InvoiceStatus.PAID)
        pending_invoices = total_invoices - paid_invoices
        total_amount = sum(inv.total_amount for inv in invoices)
        pending_amount = sum(inv.total_amount for inv in invoices 
                           if inv.status != InvoiceStatus.PAID)
        
        return {
            'year': year,
            'month': month,
            'month_name': date(year, month, 1).strftime('%B'),
            'total_revenue': revenue,
            'total_invoices': total_invoices,
            'paid_invoices': paid_invoices,
            'pending_invoices': pending_invoices,
            'total_amount': total_amount,
            'pending_amount': pending_amount,
            'collection_rate': (revenue / total_amount * 100) if total_amount > 0 else 0
        }
    
    def get_client_revenue_report(self) -> List[Dict[str, Any]]:
        """Generate client-wise revenue report."""
        clients = self.client_repository.find_all()
        client_reports = []
        
        for client in clients:
            client_invoices = self.invoice_repository.find_by_client(client.id)
            
            total_invoices = len(client_invoices)
            paid_amount = sum(inv.total_amount for inv in client_invoices 
                            if inv.status == InvoiceStatus.PAID)
            pending_amount = sum(inv.total_amount for inv in client_invoices 
                               if inv.status not in [InvoiceStatus.PAID, InvoiceStatus.CANCELLED])
            total_amount = paid_amount + pending_amount
            
            if total_amount > 0:  # Only include clients with invoices
                client_reports.append({
                    'client_id': client.id,
                    'client_name': client.display_name(),
                    'email': client.email,
                    'total_invoices': total_invoices,
                    'total_amount': total_amount,
                    'paid_amount': paid_amount,
                    'pending_amount': pending_amount
                })
        
        # Sort by total amount (descending)
        client_reports.sort(key=lambda x: x['total_amount'], reverse=True)
        return client_reports
    
    def get_outstanding_payments_report(self) -> Dict[str, Any]:
        """Generate outstanding payments report."""
        overdue_invoices = self.invoice_repository.find_overdue()
        
        # Get all unpaid invoices
        all_invoices = self.invoice_repository.find_all()
        unpaid_invoices = [inv for inv in all_invoices 
                          if inv.status not in [InvoiceStatus.PAID, InvoiceStatus.CANCELLED]]
        
        total_outstanding = sum(inv.total_amount for inv in unpaid_invoices)
        overdue_amount = sum(inv.total_amount for inv in overdue_invoices)
        
        # Group by client
        client_outstanding = {}
        for invoice in unpaid_invoices:
            client = self.client_repository.find_by_id(invoice.client_id)
            if client:
                if client.id not in client_outstanding:
                    client_outstanding[client.id] = {
                        'client_name': client.display_name(),
                        'email': client.email,
                        'total_amount': 0,
                        'overdue_amount': 0,
                        'invoice_count': 0
                    }
                
                client_outstanding[client.id]['total_amount'] += invoice.total_amount
                client_outstanding[client.id]['invoice_count'] += 1
                
                if invoice.is_overdue():
                    client_outstanding[client.id]['overdue_amount'] += invoice.total_amount
        
        return {
            'total_outstanding': total_outstanding,
            'overdue_amount': overdue_amount,
            'total_unpaid_invoices': len(unpaid_invoices),
            'overdue_invoices_count': len(overdue_invoices),
            'client_breakdown': list(client_outstanding.values())
        }
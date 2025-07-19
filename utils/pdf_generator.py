import os
from typing import List
from datetime import date
from fpdf import FPDF
from models.invoice import Invoice
from models.client import Client
from config.settings import settings

class InvoicePDFGenerator:
    """Generate PDF invoices using FPDF."""
    
    def __init__(self):
        self.pdf = None
        
    def generate_invoice_pdf(self, invoice: Invoice, client: Client, 
                           company_info: dict) -> str:
        """Generate PDF for an invoice."""
        self.pdf = FPDF()
        self.pdf.add_page()
        self.pdf.set_font('Arial', 'B', 16)
        
        # Header
        self._add_header(company_info, invoice)
        
        # Client information
        self._add_client_info(client)
        
        # Invoice details
        self._add_invoice_details(invoice)
        
        # Items table
        self._add_items_table(invoice)
        
        # Footer
        self._add_footer(invoice)
        
        # Generate filename and save
        filename = f"{invoice.invoice_number}.pdf"
        filepath = os.path.join(settings.pdf.output_path, filename)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        self.pdf.output(filepath)
        return filepath
    
    def _add_header(self, company_info: dict, invoice: Invoice):
        """Add header with company info and invoice title."""
        # Company name
        self.pdf.set_font('Arial', 'B', 20)
        self.pdf.cell(0, 10, company_info.get('name', 'Your Company'), ln=True)
        
        # Company details
        self.pdf.set_font('Arial', '', 10)
        if company_info.get('address'):
            self.pdf.cell(0, 5, company_info['address'], ln=True)
        if company_info.get('phone'):
            self.pdf.cell(0, 5, f"Phone: {company_info['phone']}", ln=True)
        if company_info.get('email'):
            self.pdf.cell(0, 5, f"Email: {company_info['email']}", ln=True)
        
        self.pdf.ln(10)
        
        # Invoice title
        self.pdf.set_font('Arial', 'B', 16)
        self.pdf.cell(0, 10, 'INVOICE', align='C', ln=True)
        self.pdf.ln(5)
    
    def _add_client_info(self, client: Client):
        """Add client information."""
        self.pdf.set_font('Arial', 'B', 12)
        self.pdf.cell(0, 8, 'Bill To:', ln=True)
        
        self.pdf.set_font('Arial', '', 10)
        self.pdf.cell(0, 6, client.name, ln=True)
        if client.company:
            self.pdf.cell(0, 6, client.company, ln=True)
        self.pdf.cell(0, 6, client.email, ln=True)
        if client.phone:
            self.pdf.cell(0, 6, f"Phone: {client.phone}", ln=True)
        if client.address:
            self.pdf.cell(0, 6, client.address, ln=True)
        
        self.pdf.ln(10)
    
    def _add_invoice_details(self, invoice: Invoice):
        """Add invoice details."""
        # Invoice details in two columns
        y_position = self.pdf.get_y()
        
        # Left column
        self.pdf.set_font('Arial', 'B', 10)
        self.pdf.cell(40, 6, 'Invoice Number:', ln=False)
        self.pdf.set_font('Arial', '', 10)
        self.pdf.cell(60, 6, invoice.invoice_number, ln=True)
        
        self.pdf.set_font('Arial', 'B', 10)
        self.pdf.cell(40, 6, 'Issue Date:', ln=False)
        self.pdf.set_font('Arial', '', 10)
        self.pdf.cell(60, 6, invoice.issue_date.strftime('%B %d, %Y'), ln=True)
        
        self.pdf.set_font('Arial', 'B', 10)
        self.pdf.cell(40, 6, 'Due Date:', ln=False)
        self.pdf.set_font('Arial', '', 10)
        self.pdf.cell(60, 6, invoice.due_date.strftime('%B %d, %Y'), ln=True)
        
        self.pdf.ln(10)
    
    def _add_items_table(self, invoice: Invoice):
        """Add items table."""
        # Table header
        self.pdf.set_font('Arial', 'B', 10)
        self.pdf.cell(80, 8, 'Description', border=1)
        self.pdf.cell(30, 8, 'Quantity', border=1, align='C')
        self.pdf.cell(30, 8, 'Rate', border=1, align='C')
        self.pdf.cell(30, 8, 'Amount', border=1, align='C')
        self.pdf.ln()
        
        # Table rows
        self.pdf.set_font('Arial', '', 9)
        for item in invoice.items:
            self.pdf.cell(80, 6, item.description[:40], border=1)
            self.pdf.cell(30, 6, f"{item.quantity:.2f}", border=1, align='C')
            self.pdf.cell(30, 6, f"₹{item.rate:.2f}", border=1, align='C')
            self.pdf.cell(30, 6, f"₹{item.amount:.2f}", border=1, align='C')
            self.pdf.ln()
        
        self.pdf.ln(5)
        
        # Totals
        self.pdf.set_font('Arial', 'B', 10)
        
        # Subtotal
        self.pdf.cell(140, 6, 'Subtotal:', align='R')
        self.pdf.cell(30, 6, f"₹{invoice.subtotal:.2f}", align='R', ln=True)
        
        # Tax
        if invoice.tax_amount > 0:
            tax_rate = settings.invoice.tax_rate * 100
            self.pdf.cell(140, 6, f'Tax ({tax_rate:.0f}%):', align='R')
            self.pdf.cell(30, 6, f"₹{invoice.tax_amount:.2f}", align='R', ln=True)
        
        # Total
        self.pdf.set_font('Arial', 'B', 12)
        self.pdf.cell(140, 8, 'Total:', align='R')
        self.pdf.cell(30, 8, f"₹{invoice.total_amount:.2f}", align='R', ln=True)
        
        self.pdf.ln(10)
    
    def _add_footer(self, invoice: Invoice):
        """Add footer with notes and payment info."""
        if invoice.notes:
            self.pdf.set_font('Arial', 'B', 10)
            self.pdf.cell(0, 6, 'Notes:', ln=True)
            self.pdf.set_font('Arial', '', 9)
            self.pdf.multi_cell(0, 5, invoice.notes)
            self.pdf.ln(5)
        
        # Payment terms
        self.pdf.set_font('Arial', '', 8)
        self.pdf.cell(0, 5, 'Payment Terms: Payment is due within 30 days of invoice date.', ln=True)
        self.pdf.cell(0, 5, 'Thank you for your business!', ln=True)
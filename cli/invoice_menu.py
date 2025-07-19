from services.invoice_service import InvoiceService
from services.client_service import ClientService
from services.project_service import ProjectService
from Utils.exceptions import InvoiceNotFoundError, ClientNotFoundError, ValidationError
from Utils.formatters import Formatters
from datetime import date, timedelta

class InvoiceMenu:
    """CLI menu for invoice management."""
    
    def __init__(self):
        self.invoice_service = InvoiceService()
        self.client_service = ClientService()
        self.project_service = ProjectService()
    
    def show_menu(self):
        """Display invoice management menu."""
        while True:
            self._display_menu()
            choice = input("\nEnter your choice (1-8): ").strip()
            
            if choice == '1':
                self._create_invoice()
            elif choice == '2':
                self._view_all_invoices()
            elif choice == '3':
                self._view_client_invoices()
            elif choice == '4':
                self._view_invoice_details()
            elif choice == '5':
                self._update_invoice_status()
            elif choice == '6':
                self._generate_pdf()
            elif choice == '7':
                self._delete_invoice()
            elif choice == '8':
                break
            else:
                print("Invalid choice. Please try again.")
                input("Press Enter to continue...")
    
    def _display_menu(self):
        """Display invoice menu options."""
        print("\n" + "-"*40)
        print("        INVOICE MANAGEMENT")
        print("-"*40)
        print("1. Create New Invoice")
        print("2. View All Invoices")
        print("3. View Client Invoices")
        print("4. View Invoice Details")
        print("5. Update Invoice Status")
        print("6. Generate PDF")
        print("7. Delete Invoice")
        print("8. Back to Main Menu")
    
    def _create_invoice(self):
        """Create a new invoice."""
        print("\n--- Create New Invoice ---")
        try:
            # Show available clients
            clients = self.client_service.get_all_clients()
            if not clients:
                print("No clients found. Please add a client first.")
                input("Press Enter to continue...")
                return
            
            print("Available clients:")
            for client in clients:
                print(f"  {client.id}: {client.display_name()}")
            
            client_id = int(input("\nEnter Client ID: "))
            client = self.client_service.get_client(client_id)
            
            # Show client's projects
            projects = self.project_service.get_projects_by_client(client_id)
            project_id = None
            
            if projects:
                print(f"\nProjects for {client.display_name()}:")
                print("0: No specific project")
                for project in projects:
                    print(f"  {project.id}: {project.name}")
                
                proj_choice = input("Enter Project ID (or 0 for none): ").strip()
                if proj_choice != '0':
                    project_id = int(proj_choice)
            
            # Invoice details
            invoice_number = input("Invoice Number (leave blank for auto-generation): ").strip() or None
            
            print("\nInvoice dates:")
            issue_date_input = input("Issue Date (YYYY-MM-DD, or press Enter for today): ").strip()
            if issue_date_input:
                issue_date = date.fromisoformat(issue_date_input)
            else:
                issue_date = date.today()
            
            due_date_input = input("Due Date (YYYY-MM-DD, or press Enter for 30 days): ").strip()
            if due_date_input:
                due_date = date.fromisoformat(due_date_input)
            else:
                due_date = issue_date + timedelta(days=30)
            
            notes = input("Notes (optional): ").strip() or None
            
            # Create invoice
            invoice = self.invoice_service.create_invoice(
                client_id, project_id, issue_date, due_date, notes, invoice_number
            )
            
            print(f"\nInvoice {invoice.invoice_number} created successfully!")
            print("Now add items to the invoice...")
            
            # Add items
            self._add_invoice_items(invoice.id)
            
        except (ValueError, ValidationError, ClientNotFoundError) as e:
            print(f"\nError: {e}")
        
        input("Press Enter to continue...")
    
    def _add_invoice_items(self, invoice_id):
        """Add items to an invoice."""
        while True:
            print("\n--- Add Invoice Item ---")
            description = input("Item Description: ").strip()
            if not description:
                break
            
            try:
                quantity = float(input("Quantity: "))
                rate = float(input("Rate (₹): "))
                
                self.invoice_service.add_invoice_item(invoice_id, description, quantity, rate)
                print("Item added successfully!")
                
                another = input("Add another item? (y/N): ").strip().lower()
                if another != 'y':
                    break
                    
            except ValueError:
                print("Invalid quantity or rate. Please try again.")
    
    def _view_all_invoices(self):
        """View all invoices."""
        print("\n--- All Invoices ---")
        invoices = self.invoice_service.get_all_invoices()
        
        if not invoices:
            print("No invoices found.")
        else:
            print(f"\nFound {len(invoices)} invoice(s):")
            self._display_invoices_table(invoices)
        
        input("\nPress Enter to continue...")
    
    def _view_client_invoices(self):
        """View invoices for a specific client."""
        print("\n--- Client Invoices ---")
        try:
            client_id = int(input("Enter Client ID: "))
            client = self.client_service.get_client(client_id)
            invoices = self.invoice_service.get_invoices_by_client(client_id)
            
            print(f"\nInvoices for: {client.display_name()}")
            
            if not invoices:
                print("No invoices found for this client.")
            else:
                self._display_invoices_table(invoices)
                
        except (ValueError, ClientNotFoundError) as e:
            print(f"\nError: {e}")
        
        input("\nPress Enter to continue...")
    
    def _view_invoice_details(self):
        """View detailed invoice information."""
        print("\n--- Invoice Details ---")
        try:
            invoice_id = int(input("Enter Invoice ID: "))
            invoice = self.invoice_service.get_invoice(invoice_id)
            client = self.client_service.get_client(invoice.client_id)
            
            print(f"\n{'='*50}")
            print(f"Invoice: {invoice.invoice_number}")
            print(f"{'='*50}")
            print(f"Client: {client.display_name()}")
            print(f"Issue Date: {Formatters.format_date(invoice.issue_date)}")
            print(f"Due Date: {Formatters.format_date(invoice.due_date)}")
            print(f"Status: {Formatters.format_status(invoice.status)}")
            
            if invoice.notes:
                print(f"Notes: {invoice.notes}")
            
            print(f"\n{'Items:':<40}")
            print("-" * 70)
            print(f"{'Description':<30} {'Qty':<8} {'Rate':<12} {'Amount':<12}")
            print("-" * 70)
            
            for item in invoice.items:
                print(f"{item.description[:29]:<30} {item.quantity:<8.2f} "
                      f"{Formatters.format_currency_simple(item.rate):<12} "
                      f"{Formatters.format_currency_simple(item.amount):<12}")
            
            print("-" * 70)
            print(f"{'Subtotal:':<58} {Formatters.format_currency(invoice.subtotal)}")
            if invoice.tax_amount > 0:
                print(f"{'Tax:':<58} {Formatters.format_currency(invoice.tax_amount)}")
            print(f"{'TOTAL:':<58} {Formatters.format_currency(invoice.total_amount)}")
            
        except (ValueError, InvoiceNotFoundError) as e:
            print(f"\nError: {e}")
        
        input("\nPress Enter to continue...")
    
    def _update_invoice_status(self):
        """Update invoice status."""
        print("\n--- Update Invoice Status ---")
        try:
            invoice_id = int(input("Enter Invoice ID: "))
            invoice = self.invoice_service.get_invoice(invoice_id)
            
            print(f"\nInvoice: {invoice.invoice_number}")
            print(f"Current Status: {Formatters.format_status(invoice.status)}")
            
            print("\nAvailable statuses:")
            statuses = ['draft', 'sent', 'paid', 'overdue', 'cancelled']
            for i, status in enumerate(statuses, 1):
                print(f"{i}. {Formatters.format_status(status)}")
            
            choice = int(input("Choose status (1-5): "))
            if 1 <= choice <= 5:
                new_status = statuses[choice - 1]
                updated_invoice = self.invoice_service.update_invoice_status(invoice_id, new_status)
                print(f"\nInvoice status updated to: {Formatters.format_status(new_status)}")
            else:
                print("Invalid choice.")
                
        except (ValueError, InvoiceNotFoundError, ValidationError) as e:
            print(f"\nError: {e}")
        
        input("Press Enter to continue...")
    
    def _generate_pdf(self):
        """Generate PDF for an invoice."""
        print("\n--- Generate PDF ---")
        try:
            invoice_id = int(input("Enter Invoice ID: "))
            
            company_info = {
                'name': input("Your Company Name: ").strip() or "Your Company",
                'address': input("Company Address: ").strip() or "",
                'phone': input("Company Phone: ").strip() or "",
                'email': input("Company Email: ").strip() or ""
            }
            
            pdf_path = self.invoice_service.generate_pdf(invoice_id, company_info)
            print(f"\nPDF generated successfully: {pdf_path}")
            
        except (ValueError, InvoiceNotFoundError) as e:
            print(f"\nError: {e}")
        
        input("Press Enter to continue...")
    
    def _delete_invoice(self):
        """Delete an invoice."""
        print("\n--- Delete Invoice ---")
        try:
            invoice_id = int(input("Enter Invoice ID: "))
            invoice = self.invoice_service.get_invoice(invoice_id)
            
            print(f"\nInvoice to delete: {invoice.invoice_number}")
            confirm = input("Are you sure? This action cannot be undone (y/N): ").strip().lower()
            
            if confirm == 'y':
                if self.invoice_service.delete_invoice(invoice_id):
                    print(f"\nInvoice {invoice.invoice_number} deleted successfully!")
                else:
                    print("\nFailed to delete invoice.")
            else:
                print("Deletion cancelled.")
                
        except (ValueError, InvoiceNotFoundError) as e:
            print(f"\nError: {e}")
        
        input("Press Enter to continue...")
    
    def _display_invoices_table(self, invoices):
        """Display invoices in a formatted table."""
        print("-" * 90)
        print(f"{'ID':<4} {'Number':<12} {'Client':<15} {'Date':<12} {'Due':<12} {'Amount':<12} {'Status':<10}")
        print("-" * 90)
        
        for invoice in invoices:
            try:
                client = self.client_service.get_client(invoice.client_id)
                client_name = client.name[:14] if client else 'Unknown'
            except:
                client_name = 'Unknown'
            
            print(f"{invoice.id:<4} {invoice.invoice_number[:11]:<12} {client_name:<15} "
                  f"{Formatters.format_date(invoice.issue_date, 'short'):<12} "
                  f"{Formatters.format_date(invoice.due_date, 'short'):<12} "
                  f"{Formatters.format_currency_simple(invoice.total_amount):<12} "
                  f"{Formatters.format_status(invoice.status)[:9]:<10}")



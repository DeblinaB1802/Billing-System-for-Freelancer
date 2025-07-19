from services.report_service import ReportService
from services.client_service import ClientService
from services.invoice_service import InvoiceService
from services.project_service import ProjectService
from Utils.exceptions import ValidationError
from Utils.formatters import Formatters
from datetime import date, datetime, timedelta
import os

class ReportMenu:
    """CLI menu for reports and analytics."""
    
    def __init__(self):
        self.report_service = ReportService()
        self.client_service = ClientService()
        self.invoice_service = InvoiceService()
        self.project_service = ProjectService()
    
    def show_menu(self):
        """Display reports menu."""
        while True:
            self._display_menu()
            choice = input("\nEnter your choice (1-10): ").strip()
            
            if choice == '1':
                self._revenue_summary()
            elif choice == '2':
                self._client_summary()
            elif choice == '3':
                self._project_summary()
            elif choice == '4':
                self._invoice_status_report()
            elif choice == '5':
                self._outstanding_invoices()
            elif choice == '6':
                self._monthly_revenue()
            elif choice == '7':
                self._client_revenue()
            elif choice == '8':
                self._time_tracking_report()
            elif choice == '9':
                self._export_data()
            elif choice == '10':
                break
            else:
                print("Invalid choice. Please try again.")
                input("Press Enter to continue...")
    
    def _display_menu(self):
        """Display report menu options."""
        print("\n" + "-"*40)
        print("        REPORTS & ANALYTICS")
        print("-"*40)
        print("1. Revenue Summary")
        print("2. Client Summary")
        print("3. Project Summary")
        print("4. Invoice Status Report")
        print("5. Outstanding Invoices")
        print("6. Monthly Revenue Report")
        print("7. Revenue by Client")
        print("8. Time Tracking Report")
        print("9. Export Data")
        print("10. Back to Main Menu")
    
    def _revenue_summary(self):
        """Display overall revenue summary."""
        print("\n--- Revenue Summary ---")
        try:
            summary = self.report_service.get_revenue_summary()
            
            print(f"\n{'='*50}")
            print("REVENUE OVERVIEW")
            print(f"{'='*50}")
            print(f"Total Revenue:        {Formatters.format_currency(summary.get('total_revenue', 0))}")
            print(f"Paid Invoices:        {Formatters.format_currency(summary.get('paid_revenue', 0))}")
            print(f"Outstanding Amount:   {Formatters.format_currency(summary.get('outstanding', 0))}")
            print(f"Draft Invoices:       {Formatters.format_currency(summary.get('draft_amount', 0))}")
            
            print(f"\n{'INVOICE COUNTS'}")
            print(f"{'-'*30}")
            print(f"Total Invoices:       {summary.get('total_invoices', 0)}")
            print(f"Paid:                 {summary.get('paid_count', 0)}")
            print(f"Pending:              {summary.get('pending_count', 0)}")
            print(f"Overdue:              {summary.get('overdue_count', 0)}")
            print(f"Draft:                {summary.get('draft_count', 0)}")
            
            # Payment rates
            total_invoices = summary.get('total_invoices', 0)
            if total_invoices > 0:
                paid_rate = (summary.get('paid_count', 0) / total_invoices) * 100
                print(f"\nPayment Rate:         {paid_rate:.1f}%")
            
        except Exception as e:
            print(f"\nError generating revenue summary: {e}")
        
        input("\nPress Enter to continue...")
    
    def _client_summary(self):
        """Display client summary report."""
        print("\n--- Client Summary ---")
        try:
            clients = self.client_service.get_all_clients()
            
            print(f"\n{'='*80}")
            print("CLIENT OVERVIEW")
            print(f"{'='*80}")
            print(f"Total Clients: {len(clients)}")
            
            if not clients:
                print("No clients found.")
                input("\nPress Enter to continue...")
                return
            
            # Get client statistics
            client_stats = []
            for client in clients:
                invoices = self.invoice_service.get_invoices_by_client(client.id)
                projects = self.project_service.get_projects_by_client(client.id)
                
                total_revenue = sum(inv.total_amount for inv in invoices if inv.status == 'paid')
                outstanding = sum(inv.total_amount for inv in invoices if inv.status in ['sent', 'overdue'])
                
                client_stats.append({
                    'client': client,
                    'invoices': len(invoices),
                    'projects': len(projects),
                    'revenue': total_revenue,
                    'outstanding': outstanding
                })
            
            # Sort by revenue (highest first)
            client_stats.sort(key=lambda x: x['revenue'], reverse=True)
            
            print(f"\n{'-'*100}")
            print(f"{'Client':<25} {'Invoices':<10} {'Projects':<10} {'Revenue':<15} {'Outstanding':<15}")
            print(f"{'-'*100}")
            
            for stat in client_stats:
                print(f"{stat['client'].name[:24]:<25} {stat['invoices']:<10} {stat['projects']:<10} "
                      f"{Formatters.format_currency_simple(stat['revenue']):<15} "
                      f"{Formatters.format_currency_simple(stat['outstanding']):<15}")
            
        except Exception as e:
            print(f"\nError generating client summary: {e}")
        
        input("\nPress Enter to continue...")
    
    def _project_summary(self):
        """Display project summary report."""
        print("\n--- Project Summary ---")
        try:
            projects = self.project_service.get_all_projects()
            
            if not projects:
                print("No projects found.")
                input("\nPress Enter to continue...")
                return
            
            # Categorize projects by status
            status_counts = {}
            total_hours = 0
            total_earned = 0
            
            for project in projects:
                status = project.status
                status_counts[status] = status_counts.get(status, 0) + 1
                total_hours += project.hours_worked
                
                if project.hourly_rate:
                    total_earned += project.hourly_rate * project.hours_worked
                elif project.fixed_rate:
                    total_earned += project.fixed_rate
            
            print(f"\n{'='*60}")
            print("PROJECT OVERVIEW")
            print(f"{'='*60}")
            print(f"Total Projects:       {len(projects)}")
            print(f"Total Hours Logged:   {total_hours:.1f}")
            print(f"Total Project Value:  {Formatters.format_currency(total_earned)}")
            
            print(f"\n{'PROJECT STATUS BREAKDOWN'}")
            print(f"{'-'*40}")
            for status, count in status_counts.items():
                print(f"{Formatters.format_status(status).ljust(15)}: {count}")
            
            # Top projects by hours/value
            print(f"\n{'TOP PROJECTS BY HOURS'}")
            print(f"{'-'*70}")
            print(f"{'Project':<25} {'Client':<20} {'Hours':<10} {'Value':<12}")
            print(f"{'-'*70}")
            
            # Sort by hours worked
            top_projects = sorted(projects, key=lambda x: x.hours_worked, reverse=True)[:10]
            
            for project in top_projects:
                try:
                    client = self.client_service.get_client(project.client_id)
                    client_name = client.name[:19] if client else 'Unknown'
                    
                    if project.hourly_rate:
                        value = project.hourly_rate * project.hours_worked
                    else:
                        value = project.fixed_rate or 0
                    
                    print(f"{project.name[:24]:<25} {client_name:<20} {project.hours_worked:<10.1f} "
                          f"{Formatters.format_currency_simple(value):<12}")
                except:
                    continue
            
        except Exception as e:
            print(f"\nError generating project summary: {e}")
        
        input("\nPress Enter to continue...")
    
    def _invoice_status_report(self):
        """Display invoice status breakdown."""
        print("\n--- Invoice Status Report ---")
        try:
            invoices = self.invoice_service.get_all_invoices()
            
            if not invoices:
                print("No invoices found.")
                input("\nPress Enter to continue...")
                return
            
            # Group by status
            status_groups = {}
            for invoice in invoices:
                status = invoice.status
                if status not in status_groups:
                    status_groups[status] = []
                status_groups[status].append(invoice)
            
            print(f"\n{'='*80}")
            print("INVOICE STATUS BREAKDOWN")
            print(f"{'='*80}")
            
            for status, status_invoices in status_groups.items():
                total_amount = sum(inv.total_amount for inv in status_invoices)
                print(f"\n{Formatters.format_status(status).upper()} ({len(status_invoices)} invoices)")
                print(f"Amount: {Formatters.format_currency(total_amount)}")
                
                if len(status_invoices) <= 5:  # Show details for small groups
                    for inv in status_invoices:
                        try:
                            client = self.client_service.get_client(inv.client_id)
                            client_name = client.name if client else 'Unknown'
                            print(f"  {inv.invoice_number} - {client_name} - {Formatters.format_currency_simple(inv.total_amount)}")
                        except:
                            continue
            
        except Exception as e:
            print(f"\nError generating invoice status report: {e}")
        
        input("\nPress Enter to continue...")
    
    def _outstanding_invoices(self):
        """Display outstanding invoices report."""
        print("\n--- Outstanding Invoices ---")
        try:
            outstanding = self.report_service.get_outstanding_invoices()
            
            if not outstanding:
                print("No outstanding invoices found.")
                input("\nPress Enter to continue...")
                return
            
            total_outstanding = sum(inv.total_amount for inv in outstanding)
            
            print(f"\n{'='*90}")
            print(f"OUTSTANDING INVOICES - Total: {Formatters.format_currency(total_outstanding)}")
            print(f"{'='*90}")
            
            # Categorize by age
            today = date.today()
            current = []
            overdue_30 = []
            overdue_60 = []
            overdue_90_plus = []
            
            for invoice in outstanding:
                days_overdue = (today - invoice.due_date).days
                if days_overdue <= 0:
                    current.append(invoice)
                elif days_overdue <= 30:
                    overdue_30.append(invoice)
                elif days_overdue <= 60:
                    overdue_60.append(invoice)
                else:
                    overdue_90_plus.append(invoice)
            
            categories = [
                ("Current (Not Yet Due)", current),
                ("1-30 Days Overdue", overdue_30),
                ("31-60 Days Overdue", overdue_60),
                ("60+ Days Overdue", overdue_90_plus)
            ]
            
            for category_name, category_invoices in categories:
                if category_invoices:
                    category_total = sum(inv.total_amount for inv in category_invoices)
                    print(f"\n{category_name} ({len(category_invoices)} invoices)")
                    print(f"Amount: {Formatters.format_currency(category_total)}")
                    print(f"{'-'*80}")
                    print(f"{'Invoice':<15} {'Client':<20} {'Due Date':<12} {'Amount':<12} {'Days':<8}")
                    print(f"{'-'*80}")
                    
                    for inv in category_invoices:
                        try:
                            client = self.client_service.get_client(inv.client_id)
                            client_name = client.name[:19] if client else 'Unknown'
                            days_overdue = (today - inv.due_date).days
                            days_str = f"{days_overdue}d" if days_overdue > 0 else "Current"
                            
                            print(f"{inv.invoice_number[:14]:<15} {client_name:<20} "
                                  f"{Formatters.format_date(inv.due_date, 'short'):<12} "
                                  f"{Formatters.format_currency_simple(inv.total_amount):<12} {days_str:<8}")
                        except:
                            continue
            
        except Exception as e:
            print(f"\nError generating outstanding invoices report: {e}")
        
        input("\nPress Enter to continue...")
    
    def _monthly_revenue(self):
        """Display monthly revenue report."""
        print("\n--- Monthly Revenue Report ---")
        try:
            print("\nEnter date range (or press Enter for last 12 months):")
            start_date_input = input("Start date (YYYY-MM-DD): ").strip()
            end_date_input = input("End date (YYYY-MM-DD): ").strip()
            
            if start_date_input and end_date_input:
                start_date = datetime.strptime(start_date_input, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date_input, "%Y-%m-%d").date()
            else:
                end_date = date.today()
                start_date = end_date - timedelta(days=365)
            
            monthly_data = self.report_service.get_monthly_revenue(start_date, end_date)
            
            if not monthly_data:
                print("No revenue data found for the specified period.")
                input("\nPress Enter to continue...")
                return
            
            print(f"\n{'='*60}")
            print(f"MONTHLY REVENUE: {Formatters.format_date(start_date)} to {Formatters.format_date(end_date)}")
            print(f"{'='*60}")
            print(f"{'Month':<15} {'Revenue':<15} {'Invoices':<10} {'Avg Invoice':<15}")
            print(f"{'-'*60}")
            
            total_revenue = 0
            total_invoices = 0
            
            for month_data in monthly_data:
                total_revenue += month_data['revenue']
                total_invoices += month_data['invoice_count']
                avg_invoice = month_data['revenue'] / month_data['invoice_count'] if month_data['invoice_count'] > 0 else 0
                
                print(f"{month_data['month']:<15} {Formatters.format_currency_simple(month_data['revenue']):<15} "
                      f"{month_data['invoice_count']:<10} {Formatters.format_currency_simple(avg_invoice):<15}")
            
            print(f"{'-'*60}")
            avg_monthly = total_revenue / len(monthly_data) if monthly_data else 0
            print(f"{'TOTALS':<15} {Formatters.format_currency_simple(total_revenue):<15} {total_invoices:<10} "
                  f"{Formatters.format_currency_simple(avg_monthly):<15}")
            
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
        except Exception as e:
            print(f"\nError generating monthly revenue report: {e}")
        
        input("\nPress Enter to continue...")
    
    def _client_revenue(self):
        """Display revenue by client report."""
        print("\n--- Revenue by Client ---")
        try:
            client_revenue = self.report_service.get_client_revenue()
            
            if not client_revenue:
                print("No revenue data found.")
                input("\nPress Enter to continue...")
                return
            
            print(f"\n{'='*80}")
            print("REVENUE BY CLIENT")
            print(f"{'='*80}")
            print(f"{'Client':<25} {'Paid':<15} {'Outstanding':<15} {'Total':<15} {'Invoices':<10}")
            print(f"{'-'*80}")
            
            grand_total_paid = 0
            grand_total_outstanding = 0
            
            for client_data in client_revenue:
                grand_total_paid += client_data['paid_revenue']
                grand_total_outstanding += client_data['outstanding']
                total_revenue = client_data['paid_revenue'] + client_data['outstanding']
                
                print(f"{client_data['client_name'][:24]:<25} "
                      f"{Formatters.format_currency_simple(client_data['paid_revenue']):<15} "
                      f"{Formatters.format_currency_simple(client_data['outstanding']):<15} "
                      f"{Formatters.format_currency_simple(total_revenue):<15} "
                      f"{client_data['invoice_count']:<10}")
            
            print(f"{'-'*80}")
            grand_total = grand_total_paid + grand_total_outstanding
            print(f"{'TOTALS':<25} {Formatters.format_currency_simple(grand_total_paid):<15} "
                  f"{Formatters.format_currency_simple(grand_total_outstanding):<15} "
                  f"{Formatters.format_currency_simple(grand_total):<15}")
            
        except Exception as e:
            print(f"\nError generating client revenue report: {e}")
        
        input("\nPress Enter to continue...")
    
    def _time_tracking_report(self):
        """Display time tracking report."""
        print("\n--- Time Tracking Report ---")
        try:
            projects = self.project_service.get_all_projects()
            
            if not projects:
                print("No projects found.")
                input("\nPress Enter to continue...")
                return
            
            # Filter projects with logged hours
            tracked_projects = [p for p in projects if p.hours_worked > 0]
            
            if not tracked_projects:
                print("No time tracking data found.")
                input("\nPress Enter to continue...")
                return
            
            total_hours = sum(p.hours_worked for p in tracked_projects)
            total_value = 0
            
            print(f"\n{'='*90}")
            print("TIME TRACKING SUMMARY")
            print(f"{'='*90}")
            print(f"Total Projects with Time: {len(tracked_projects)}")
            print(f"Total Hours Logged:       {total_hours:.1f}")
            
            print(f"\n{'='*90}")
            print("PROJECT TIME DETAILS")
            print(f"{'='*90}")
            print(f"{'Project':<25} {'Client':<20} {'Hours':<10} {'Rate':<12} {'Value':<12}")
            print(f"{'-'*90}")
            
            # Sort by hours (highest first)
            tracked_projects.sort(key=lambda x: x.hours_worked, reverse=True)
            
            for project in tracked_projects:
                try:
                    client = self.client_service.get_client(project.client_id)
                    client_name = client.name[:19] if client else 'Unknown'
                    
                    if project.hourly_rate:
                        rate_str = f"₹{project.hourly_rate:.0f}/hr"
                        value = project.hourly_rate * project.hours_worked
                    else:
                        rate_str = "Fixed Rate"
                        value = project.fixed_rate or 0
                    
                    total_value += value
                    
                    print(f"{project.name[:24]:<25} {client_name:<20} {project.hours_worked:<10.1f} "
                          f"{rate_str:<12} {Formatters.format_currency_simple(value):<12}")
                except:
                    continue
            
            print(f"{'-'*90}")
            avg_rate = total_value / total_hours if total_hours > 0 else 0
            print(f"{'TOTALS':<25} {'':<20} {total_hours:<10.1f} "
                  f"₹{avg_rate:.0f}/hr avg {Formatters.format_currency_simple(total_value):<12}")
            
        except Exception as e:
            print(f"\nError generating time tracking report: {e}")
        
        input("\nPress Enter to continue...")
    
    def _export_data(self):
        """Export data to CSV files."""
        print("\n--- Export Data ---")
        try:
            print("Available export options:")
            print("1. Clients")
            print("2. Projects")
            print("3. Invoices")
            print("4. All Data")
            
            choice = input("Choose export option (1-4): ").strip()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_dir = f"exports/export_{timestamp}"
            os.makedirs(export_dir, exist_ok=True)
            
            exported_files = []
            
            if choice in ['1', '4']:
                clients_file = self._export_clients(export_dir)
                if clients_file:
                    exported_files.append(clients_file)
            
            if choice in ['2', '4']:
                projects_file = self._export_projects(export_dir)
                if projects_file:
                    exported_files.append(projects_file)
            
            if choice in ['3', '4']:
                invoices_file = self._export_invoices(export_dir)
                if invoices_file:
                    exported_files.append(invoices_file)
            
            if exported_files:
                print(f"\nExport completed! Files saved to: {export_dir}")
                for file in exported_files:
                    print(f"  - {file}")
            else:
                print("\nNo data to export or export failed.")
            
        except Exception as e:
            print(f"\nError during export: {e}")
        
        input("\nPress Enter to continue...")
    
    def _export_clients(self, export_dir):
        """Export clients to CSV."""
        try:
            import csv
            clients = self.client_service.get_all_clients()
            
            if not clients:
                return None
            
            filename = os.path.join(export_dir, "clients.csv")
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['ID', 'Name', 'Email', 'Phone', 'Company', 'Address', 'Created Date'])
                
                for client in clients:
                    writer.writerow([
                        client.id,
                        client.name,
                        client.email,
                        client.phone or '',
                        client.company or '',
                        client.address or '',
                        client.created_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(client, 'created_at') else ''
                    ])
            
            return filename
        except Exception as e:
            print(f"Error exporting clients: {e}")
            return None
    
    def _export_projects(self, export_dir):
        """Export projects to CSV."""
        try:
            import csv
            projects = self.project_service.get_all_projects()
            
            if not projects:
                return None
            
            filename = os.path.join(export_dir, "projects.csv")
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['ID', 'Name', 'Client ID', 'Client Name', 'Description', 'Status', 
                               'Hourly Rate', 'Fixed Rate', 'Hours Worked', 'Created Date'])
                
                for project in projects:
                    try:
                        client = self.client_service.get_client(project.client_id)
                        client_name = client.name if client else 'Unknown'
                    except:
                        client_name = 'Unknown'
                    
                    writer.writerow([
                        project.id,
                        project.name,
                        project.client_id,
                        client_name,
                        project.description or '',
                        project.status,
                        project.hourly_rate or '',
                        project.fixed_rate or '',
                        project.hours_worked,
                        project.created_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(project, 'created_at') else ''
                    ])
            
            return filename
        except Exception as e:
            print(f"Error exporting projects: {e}")
            return None
    
    def _export_invoices(self, export_dir):
        """Export invoices to CSV."""
        try:
            import csv
            invoices = self.invoice_service.get_all_invoices()
            
            if not invoices:
                return None
            
            filename = os.path.join(export_dir, "invoices.csv")
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['ID', 'Invoice Number', 'Client ID', 'Client Name', 'Project ID', 
                               'Issue Date', 'Due Date', 'Status', 'Subtotal', 'Tax Amount', 'Total Amount', 'Notes'])
                
                for invoice in invoices:
                    try:
                        client = self.client_service.get_client(invoice.client_id)
                        client_name = client.name if client else 'Unknown'
                    except:
                        client_name = 'Unknown'
                    
                    writer.writerow([
                        invoice.id,
                        invoice.invoice_number,
                        invoice.client_id,
                        client_name,
                        invoice.project_id or '',
                        invoice.issue_date.strftime('%Y-%m-%d'),
                        invoice.due_date.strftime('%Y-%m-%d'),
                        invoice.status,
                        invoice.subtotal,
                        invoice.tax_amount,
                        invoice.total_amount,
                        invoice.notes or ''
                    ])
            
            return filename
        except Exception as e:
            print(f"Error exporting invoices: {e}")
            return None
from services.project_service import ProjectService
from services.client_service import ClientService
from Utils.exceptions import ProjectNotFoundError, ClientNotFoundError, ValidationError
from Utils.formatters import Formatters

class ProjectMenu:
    """CLI menu for project management."""
    
    def __init__(self):
        self.project_service = ProjectService()
        self.client_service = ClientService()
    
    def show_menu(self):
        """Display project management menu."""
        while True:
            self._display_menu()
            choice = input("\nEnter your choice (1-7): ").strip()
            
            if choice == '1':
                self._add_project()
            elif choice == '2':
                self._view_all_projects()
            elif choice == '3':
                self._view_client_projects()
            elif choice == '4':
                self._update_project()
            elif choice == '5':
                self._log_hours()
            elif choice == '6':
                self._delete_project()
            elif choice == '7':
                break
            else:
                print("Invalid choice. Please try again.")
                input("Press Enter to continue...")
    
    def _display_menu(self):
        """Display project menu options."""
        print("\n" + "-"*40)
        print("        PROJECT MANAGEMENT")
        print("-"*40)
        print("1. Add New Project")
        print("2. View All Projects")
        print("3. View Projects by Client")
        print("4. Update Project")
        print("5. Log Hours")
        print("6. Delete Project")
        print("7. Back to Main Menu")
    
    def _add_project(self):
        """Add a new project."""
        print("\n--- Add New Project ---")
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
            name = input("Project Name (required): ").strip()
            description = input("Description (optional): ").strip() or None
            
            print("\nProject type:")
            print("1. Hourly Rate")
            print("2. Fixed Rate")
            rate_type = input("Choose rate type (1-2): ").strip()
            
            hourly_rate = None
            fixed_rate = None
            
            if rate_type == '1':
                hourly_rate = float(input("Hourly Rate (₹): "))
            elif rate_type == '2':
                fixed_rate = float(input("Fixed Rate (₹): "))
            else:
                print("Invalid rate type. Defaulting to hourly rate.")
                hourly_rate = float(input("Hourly Rate (₹): "))
            
            project = self.project_service.create_project(
                client_id, name, description, hourly_rate, fixed_rate
            )
            
            print(f"\nProject '{project.name}' created successfully!")
            print(f"Project ID: {project.id}")
            
        except (ValueError, ValidationError, ClientNotFoundError) as e:
            print(f"\nError: {e}")
        
        input("Press Enter to continue...")
    
    def _view_all_projects(self):
        """View all projects."""
        print("\n--- All Projects ---")
        projects = self.project_service.get_all_projects()
        
        if not projects:
            print("No projects found.")
        else:
            print(f"\nFound {len(projects)} project(s):")
            self._display_projects_table(projects)
        
        input("\nPress Enter to continue...")
    
    def _view_client_projects(self):
        """View projects for a specific client."""
        print("\n--- Projects by Client ---")
        try:
            client_id = int(input("Enter Client ID: "))
            client = self.client_service.get_client(client_id)
            projects = self.project_service.get_projects_by_client(client_id)
            
            print(f"\nProjects for: {client.display_name()}")
            
            if not projects:
                print("No projects found for this client.")
            else:
                self._display_projects_table(projects)
                
        except (ValueError, ClientNotFoundError) as e:
            print(f"\nError: {e}")
        
        input("\nPress Enter to continue...")
    
    def _update_project(self):
        """Update existing project."""
        print("\n--- Update Project ---")
        try:
            project_id = int(input("Enter Project ID: "))
            project = self.project_service.get_project(project_id)
            
            print(f"\nCurrent details for: {project.name}")
            print(f"Description: {project.description or 'Not set'}")
            print(f"Status: {Formatters.format_status(project.status)}")
            if project.hourly_rate:
                print(f"Hourly Rate: {Formatters.format_currency(project.hourly_rate)}")
            if project.fixed_rate:
                print(f"Fixed Rate: {Formatters.format_currency(project.fixed_rate)}")
            print(f"Hours Worked: {project.hours_worked}")
            
            print("\nEnter new values (press Enter to keep current):")
            name = input(f"Name [{project.name}]: ").strip()
            description = input(f"Description [{project.description or ''}]: ").strip()
            
            print("\nStatus options: active, completed, on_hold, cancelled")
            status = input(f"Status [{project.status}]: ").strip()
            
            updated_project = self.project_service.update_project(
                project_id,
                name if name else None,
                description if description else None,
                status if status else None
            )
            
            print(f"\nProject '{updated_project.name}' updated successfully!")
            
        except (ValueError, ProjectNotFoundError, ValidationError) as e:
            print(f"\nError: {e}")
        
        input("Press Enter to continue...")
    
    def _log_hours(self):
        """Log hours for a project."""
        print("\n--- Log Hours ---")
        try:
            project_id = int(input("Enter Project ID: "))
            project = self.project_service.get_project(project_id)
            
            print(f"Project: {project.name}")
            print(f"Current Hours: {project.hours_worked}")
            
            hours = float(input("Hours to add: "))
            description = input("Work description (optional): ").strip() or None
            
            updated_project = self.project_service.log_hours(project_id, hours, description)
            
            print(f"\nLogged {hours} hours successfully!")
            print(f"Total Hours: {updated_project.hours_worked}")
            
        except (ValueError, ProjectNotFoundError) as e:
            print(f"\nError: {e}")
        
        input("Press Enter to continue...")
    
    def _delete_project(self):
        """Delete a project."""
        print("\n--- Delete Project ---")
        try:
            project_id = int(input("Enter Project ID: "))
            project = self.project_service.get_project(project_id)
            
            print(f"\nProject to delete: {project.name}")
            print("WARNING: This will also delete all invoices for this project.")
            confirm = input("Are you sure? This action cannot be undone (y/N): ").strip().lower()
            
            if confirm == 'y':
                if self.project_service.delete_project(project_id):
                    print(f"\nProject '{project.name}' deleted successfully!")
                else:
                    print("\nFailed to delete project.")
            else:
                print("Deletion cancelled.")
                
        except (ValueError, ProjectNotFoundError) as e:
            print(f"\nError: {e}")
        
        input("Press Enter to continue...")
    
    def _display_projects_table(self, projects):
        """Display projects in a formatted table."""
        print("-" * 100)
        print(f"{'ID':<4} {'Name':<20} {'Client':<15} {'Status':<12} {'Rate':<15} {'Hours':<8} {'Earned':<12}")
        print("-" * 100)
        
        for project in projects:
            client = self.client_service.get_client(project.client_id)
            client_name = client.name[:14] if client else 'Unknown'
            
            if project.hourly_rate:
                rate = f"₹{project.hourly_rate:.0f}/hr"
                earned = project.hourly_rate * project.hours_worked
            else:
                rate = f"₹{project.fixed_rate:.0f} fixed"
                earned = project.fixed_rate or 0
            
            print(f"{project.id:<4} {project.name[:19]:<20} {client_name:<15} "
                  f"{Formatters.format_status(project.status)[:11]:<12} "
                  f"{rate[:14]:<15} {project.hours_worked:<8.1f} "
                  f"{Formatters.format_currency_simple(earned):<12}")

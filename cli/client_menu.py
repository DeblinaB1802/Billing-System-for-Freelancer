from services.client_service import ClientService
from Utils.exceptions import ClientNotFoundError, ValidationError

class ClientMenu:
    """CLI menu for client management."""
    
    def __init__(self):
        self.client_service = ClientService()
    
    def show_menu(self):
        """Display client management menu."""
        while True:
            self._display_menu()
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == '1':
                self._add_client()
            elif choice == '2':
                self._view_all_clients()
            elif choice == '3':
                self._search_clients()
            elif choice == '4':
                self._update_client()
            elif choice == '5':
                self._delete_client()
            elif choice == '6':
                break
            else:
                print("Invalid choice. Please try again.")
                input("Press Enter to continue...")
    
    def _display_menu(self):
        """Display client menu options."""
        print("\n" + "-"*40)
        print("         CLIENT MANAGEMENT")
        print("-"*40)
        print("1. Add New Client")
        print("2. View All Clients")
        print("3. Search Clients")
        print("4. Update Client")
        print("5. Delete Client")
        print("6. Back to Main Menu")
    
    def _add_client(self):
        """Add a new client."""
        print("\n--- Add New Client ---")
        try:
            name = input("Client Name (required): ").strip()
            email = input("Email (required): ").strip()
            phone = input("Phone (optional): ").strip() or None
            company = input("Company (optional): ").strip() or None
            address = input("Address (optional): ").strip() or None
            
            client = self.client_service.create_client(name, email, phone, company, address)
            print(f"\nClient '{client.display_name()}' added successfully!")
            print(f"Client ID: {client.id}")
            
        except ValidationError as e:
            print(f"\nValidation Error: {e}")
        except Exception as e:
            print(f"\nError: {e}")
        
        input("Press Enter to continue...")
    
    def _view_all_clients(self):
        """View all clients."""
        print("\n--- All Clients ---")
        clients = self.client_service.get_all_clients()
        
        if not clients:
            print("No clients found.")
        else:
            print(f"\nFound {len(clients)} client(s):")
            print("-" * 80)
            print(f"{'ID':<5} {'Name':<20} {'Company':<20} {'Email':<25} {'Phone':<15}")
            print("-" * 80)
            
            for client in clients:
                print(f"{client.id:<5} {client.name[:19]:<20} "
                      f"{(client.company or '')[:19]:<20} "
                      f"{client.email[:24]:<25} {client.phone or '':<15}")
        
        input("\nPress Enter to continue...")
    
    def _search_clients(self):
        """Search clients."""
        print("\n--- Search Clients ---")
        query = input("Enter search term (name or company): ").strip()
        
        if not query:
            print("Search term cannot be empty.")
            input("Press Enter to continue...")
            return
        
        clients = self.client_service.search_clients(query)
        
        if not clients:
            print(f"No clients found matching '{query}'.")
        else:
            print(f"\nFound {len(clients)} client(s) matching '{query}':")
            self._display_clients_table(clients)
        
        input("\nPress Enter to continue...")
    
    def _update_client(self):
        """Update existing client."""
        print("\n--- Update Client ---")
        try:
            client_id = int(input("Enter Client ID: "))
            client = self.client_service.get_client(client_id)
            
            print(f"\nCurrent details for: {client.display_name()}")
            print(f"Name: {client.name}")
            print(f"Email: {client.email}")
            print(f"Phone: {client.phone or 'Not set'}")
            print(f"Company: {client.company or 'Not set'}")
            print(f"Address: {client.address or 'Not set'}")
            
            print("\nEnter new values (press Enter to keep current):")
            name = input(f"Name [{client.name}]: ").strip()
            email = input(f"Email [{client.email}]: ").strip()
            phone = input(f"Phone [{client.phone or ''}]: ").strip()
            company = input(f"Company [{client.company or ''}]: ").strip()
            address = input(f"Address [{client.address or ''}]: ").strip()
            
            # Only update if values were provided
            updated_client = self.client_service.update_client(
                client_id,
                name if name else None,
                email if email else None,
                phone if phone else None,
                company if company else None,
                address if address else None
            )
            
            print(f"\nClient '{updated_client.display_name()}' updated successfully!")
            
        except (ValueError, ClientNotFoundError, ValidationError) as e:
            print(f"\nError: {e}")
        
        input("Press Enter to continue...")
    
    def _delete_client(self):
        """Delete a client."""
        print("\n--- Delete Client ---")
        try:
            client_id = int(input("Enter Client ID: "))
            client = self.client_service.get_client(client_id)
            
            print(f"\nClient to delete: {client.display_name()}")
            confirm = input("Are you sure? This action cannot be undone (y/N): ").strip().lower()
            
            if confirm == 'y':
                if self.client_service.delete_client(client_id):
                    print(f"\nClient '{client.display_name()}' deleted successfully!")
                else:
                    print("\nFailed to delete client.")
            else:
                print("Deletion cancelled.")
                
        except (ValueError, ClientNotFoundError) as e:
            print(f"\nError: {e}")
        
        input("Press Enter to continue...")
    
    def _display_clients_table(self, clients):
        """Display clients in a formatted table."""
        print("-" * 80)
        print(f"{'ID':<5} {'Name':<20} {'Company':<20} {'Email':<25} {'Phone':<15}")
        print("-" * 80)
        
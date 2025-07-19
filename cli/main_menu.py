import sys
from typing import Dict, Callable
from .client_menu import ClientMenu
from .invoice_menu import InvoiceMenu
from .report_menu import ReportMenu
from config.database import db_manager

class MainMenu:
    """Main CLI menu for the billing system."""
    
    def __init__(self):
        self.client_menu = ClientMenu()
        self.invoice_menu = InvoiceMenu()
        self.report_menu = ReportMenu()
        
        self.menu_options: Dict[str, Callable] = {
            '1': self.client_menu.show_menu,
            '2': self.invoice_menu.show_menu,
            '3': self.report_menu.show_menu,
            '4': self._backup_database,
            '5': sys.exit
        }
    
    def show_menu(self):
        """Display main menu and handle user input."""
        # Initialize database on first run
        db_manager.initialize_database()
        
        while True:
            self._display_header()
            self._display_options()
            
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice in self.menu_options:
                try:
                    self.menu_options[choice]()
                except KeyboardInterrupt:
                    print("\n\nOperation cancelled.")
                except Exception as e:
                    print(f"\nError: {e}")
                    input("Press Enter to continue...")
            else:
                print("Invalid choice. Please try again.")
                input("Press Enter to continue...")
    
    def _display_header(self):
        """Display application header."""
        print("\n" + "="*60)
        print("           FREELANCE BILLING SYSTEM")
        print("="*60)
    
    def _display_options(self):
        """Display menu options."""
        print("\n1. Client Management")
        print("2. Invoice Management")  
        print("3. Reports & Analytics")
        print("4. Backup Database")
        print("5. Exit")
    
    def _backup_database(self):
        """Create database backup."""
        from datetime import datetime
        import shutil
        import os
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"billing_backup_{timestamp}.db"
            backup_path = os.path.join("data/backups", backup_filename)
            
            os.makedirs("data/backups", exist_ok=True)
            shutil.copy2(db_manager.db_path, backup_path)
            
            print(f"\nDatabase backed up successfully to: {backup_path}")
        except Exception as e:
            print(f"\nBackup failed: {e}")
        
        input("Press Enter to continue...")

def main():
    """Entry point for the CLI application."""
    try:
        menu = MainMenu()
        menu.show_menu()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()
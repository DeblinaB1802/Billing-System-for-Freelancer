import os
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    path: str = "data/billing_system.db"
    backup_path: str = "data/backups/"
    
@dataclass
class InvoiceConfig:
    """Invoice configuration settings."""
    tax_rate: float = 0.18  # 18% tax rate
    currency: str = "INR"
    invoice_prefix: str = "INV"
    
@dataclass
class PDFConfig:
    """PDF generation configuration."""
    template_path: str = "templates/"
    output_path: str = "invoices/"
    company_logo: str = "assets/logo.png"

class Settings:
    """Central settings management."""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.database = DatabaseConfig()
        self.invoice = InvoiceConfig()
        self.pdf = PDFConfig()
        
        # Ensure directories exist
        self._create_directories()
    
    def _create_directories(self):
        """Create necessary directories."""
        dirs = [
            self.database.backup_path,
            self.pdf.template_path,
            self.pdf.output_path,
            "data"
        ]
        
        for dir_path in dirs:
            Path(self.base_dir / dir_path).mkdir(parents=True, exist_ok=True)
    
    def get_database_path(self) -> str:
        """Get full database path."""
        return str(self.base_dir / self.database.path)

# Global settings instance
settings = Settings()
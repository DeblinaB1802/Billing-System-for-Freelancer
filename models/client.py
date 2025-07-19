from dataclasses import dataclass
from typing import Dict, Any, Optional
from .base import BaseModel
from Utils.exceptions import ValidationError

@dataclass
class Client(BaseModel):
    """Client model representing a freelancer's client."""
    name: str = ""
    email: str = ""
    phone: Optional[str] = None
    company: Optional[str] = None
    address: Optional[str] = None
    
    def __post_init__(self):
        """Validate client data after initialization."""
        if not self.name.strip():
            raise ValidationError("Client name is required")
        if not self.email.strip():
            raise ValidationError("Client email is required")
        if "@" not in self.email:
            raise ValidationError("Invalid email format")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Client':
        """Create Client instance from dictionary."""
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            email=data.get('email', ''),
            phone=data.get('phone'),
            company=data.get('company'),
            address=data.get('address'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def display_name(self) -> str:
        """Get display name for the client."""
        return f"{self.name} ({self.company})" if self.company else self.name
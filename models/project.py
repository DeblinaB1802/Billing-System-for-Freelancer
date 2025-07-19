from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum
from .base import BaseModel
from Utils.exceptions import ValidationError

class ProjectStatus(Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"

@dataclass
class Project(BaseModel):
    """Project model representing billable work."""
    client_id: int = 0
    name: str = ""
    description: Optional[str] = None
    hourly_rate: Optional[float] = None
    fixed_rate: Optional[float] = None
    hours_worked: float = 0.0
    status: ProjectStatus = ProjectStatus.ACTIVE
    
    def __post_init__(self):
        """Validate project data after initialization."""
        if not self.name.strip():
            raise ValidationError("Project name is required")
        if self.client_id <= 0:
            raise ValidationError("Valid client ID is required")
        if not self.hourly_rate and not self.fixed_rate:
            raise ValidationError("Either hourly rate or fixed rate must be specified")
        if self.hourly_rate and self.hourly_rate < 0:
            raise ValidationError("Hourly rate must be positive")
        if self.fixed_rate and self.fixed_rate < 0:
            raise ValidationError("Fixed rate must be positive")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        """Create Project instance from dictionary."""
        status = data.get('status', 'active')
        if isinstance(status, str):
            status = ProjectStatus(status)
        
        return cls(
            id=data.get('id'),
            client_id=data.get('client_id', 0),
            name=data.get('name', ''),
            description=data.get('description'),
            hourly_rate=data.get('hourly_rate'),
            fixed_rate=data.get('fixed_rate'),
            hours_worked=data.get('hours_worked', 0.0),
            status=status,
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def calculate_amount(self) -> float:
        """Calculate total amount for the project."""
        if self.fixed_rate:
            return self.fixed_rate
        elif self.hourly_rate:
            return self.hourly_rate * self.hours_worked
        return 0.0
    
    def add_hours(self, hours: float):
        """Add worked hours to the project."""
        if hours < 0:
            raise ValidationError("Hours must be positive")
        self.hours_worked += hours
        self.update_timestamp()
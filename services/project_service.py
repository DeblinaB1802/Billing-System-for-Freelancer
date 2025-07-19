from typing import List, Optional
import logging
from models.project import Project, ProjectStatus
from repositories.project_repository import ProjectRepository
from repositories.client_repository import ClientRepository
from Utils.exceptions import ProjectNotFoundError, ClientNotFoundError, ValidationError

logger = logging.getLogger(__name__)

class ProjectService:
    """Service for project business logic."""
    
    def __init__(self):
        self.repository = ProjectRepository()
        self.client_repository = ClientRepository()
    
    def create_project(self, client_id: int, name: str, description: str = None,
                      hourly_rate: float = None, fixed_rate: float = None) -> Project:
        """Create a new project."""
        # Validate client exists
        client = self.client_repository.find_by_id(client_id)
        if not client:
            raise ClientNotFoundError(f"Client with ID {client_id} not found")
        
        # Validate pricing model
        if not hourly_rate and not fixed_rate:
            raise ValidationError("Either hourly_rate or fixed_rate must be specified")
        
        if hourly_rate and fixed_rate:
            raise ValidationError("Cannot specify both hourly_rate and fixed_rate")
        
        if hourly_rate and hourly_rate <= 0:
            raise ValidationError("Hourly rate must be positive")
        
        if fixed_rate and fixed_rate <= 0:
            raise ValidationError("Fixed rate must be positive")
        
        project = Project(
            client_id=client_id,
            name=name.strip(),
            description=description.strip() if description else None,
            hourly_rate=hourly_rate,
            fixed_rate=fixed_rate,
            status=ProjectStatus.ACTIVE
        )
        
        created_project = self.repository.create(project)
        logger.info(f"Created project '{created_project.name}' for client {client.display_name()}")
        return created_project
    
    def update_project(self, project_id: int, name: str = None, 
                      description: str = None, hourly_rate: float = None,
                      fixed_rate: float = None, status: ProjectStatus = None) -> Project:
        """Update an existing project."""
        project = self.repository.find_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(f"Project with ID {project_id} not found")
        
        # Update provided fields
        if name is not None:
            project.name = name.strip()
        if description is not None:
            project.description = description.strip() if description else None
        if hourly_rate is not None:
            if hourly_rate <= 0:
                raise ValidationError("Hourly rate must be positive")
            project.hourly_rate = hourly_rate
            project.fixed_rate = None  # Clear fixed rate
        if fixed_rate is not None:
            if fixed_rate <= 0:
                raise ValidationError("Fixed rate must be positive")
            project.fixed_rate = fixed_rate
            project.hourly_rate = None  # Clear hourly rate
        if status is not None:
            project.status = status
        
        project.update_timestamp()
        updated_project = self.repository.update(project)
        logger.info(f"Updated project '{updated_project.name}'")
        return updated_project
    
    def add_hours_to_project(self, project_id: int, hours: float, 
                           description: str = None) -> Project:
        """Add hours worked to a project."""
        project = self.repository.find_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(f"Project with ID {project_id} not found")
        
        if not project.hourly_rate:
            raise ValidationError("Cannot add hours to a fixed-rate project")
        
        if hours <= 0:
            raise ValidationError("Hours must be positive")
        
        if project.status != ProjectStatus.ACTIVE:
            raise ValidationError("Cannot add hours to inactive project")
        
        self.repository.update_hours_worked(project_id, hours)
        updated_project = self.repository.find_by_id(project_id)
        
        logger.info(f"Added {hours} hours to project '{project.name}' "
                   f"(total: {updated_project.hours_worked} hours)")
        return updated_project
    
    def complete_project(self, project_id: int) -> Project:
        """Mark project as completed."""
        project = self.repository.find_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(f"Project with ID {project_id} not found")
        
        if project.status == ProjectStatus.COMPLETED:
            raise ValidationError("Project is already completed")
        
        project.status = ProjectStatus.COMPLETED
        project.update_timestamp()
        updated_project = self.repository.update(project)
        
        logger.info(f"Marked project '{project.name}' as completed")
        return updated_project
    
    def pause_project(self, project_id: int) -> Project:
        """Pause an active project."""
        project = self.repository.find_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(f"Project with ID {project_id} not found")
        
        if project.status != ProjectStatus.ACTIVE:
            raise ValidationError("Can only pause active projects")
        
        project.status = ProjectStatus.ON_HOLD
        project.update_timestamp()
        updated_project = self.repository.update(project)
        
        logger.info(f"Paused project '{project.name}'")
        return updated_project
    
    def resume_project(self, project_id: int) -> Project:
        """Resume a paused project."""
        project = self.repository.find_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(f"Project with ID {project_id} not found")
        
        if project.status != ProjectStatus.ON_HOLD:
            raise ValidationError("Can only resume paused projects")
        
        project.status = ProjectStatus.ACTIVE
        project.update_timestamp()
        updated_project = self.repository.update(project)
        
        logger.info(f"Resumed project '{project.name}'")
        return updated_project
    
    def delete_project(self, project_id: int) -> bool:
        """Delete a project."""
        project = self.repository.find_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(f"Project with ID {project_id} not found")
        
        # TODO: Check if project has invoices and handle appropriately
        success = self.repository.delete(project_id)
        if success:
            logger.info(f"Deleted project '{project.name}'")
        return success
    
    def get_project(self, project_id: int) -> Project:
        """Get project by ID."""
        project = self.repository.find_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(f"Project with ID {project_id} not found")
        return project
    
    def get_all_projects(self) -> List[Project]:
        """Get all projects."""
        return self.repository.find_all()
    
    def get_client_projects(self, client_id: int) -> List[Project]:
        """Get projects for a specific client."""
        return self.repository.find_by_client(client_id)
    
    def get_active_projects(self) -> List[Project]:
        """Get all active projects."""
        return self.repository.find_active_projects()
    
    def search_projects(self, query: str) -> List[Project]:
        """Search projects by name or description."""
        return self.repository.search(query)
    
    def get_project_earnings(self, project_id: int) -> float:
        """Get total earnings for a project."""
        return self.repository.get_project_earnings(project_id)
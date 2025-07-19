from typing import List, Optional
import sqlite3
from models.project import Project, ProjectStatus
from .base_repository import BaseRepository
from Utils.exceptions import DatabaseError

class ProjectRepository(BaseRepository[Project]):
    """Repository for project data access."""
    
    def __init__(self):
        super().__init__("projects")
    
    def _row_to_model(self, row: sqlite3.Row) -> Project:
        """Convert database row to Project model."""
        return Project.from_dict(dict(row))
    
    def create(self, project: Project) -> Project:
        """Create new project."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO projects (client_id, name, description, hourly_rate, 
                                    fixed_rate, hours_worked, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (project.client_id, project.name, project.description, 
                  project.hourly_rate, project.fixed_rate, project.hours_worked, 
                  project.status.value))
            
            project.id = cursor.lastrowid
            conn.commit()
            return project
    
    def update(self, project: Project) -> Project:
        """Update existing project."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE projects 
                SET name = ?, description = ?, hourly_rate = ?, fixed_rate = ?, 
                    hours_worked = ?, status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (project.name, project.description, project.hourly_rate,
                  project.fixed_rate, project.hours_worked, project.status.value,
                  project.id))
            
            conn.commit()
            if cursor.rowcount == 0:
                raise DatabaseError(f"Project with ID {project.id} not found")
            return project
    
    def find_by_client(self, client_id: int) -> List[Project]:
        """Find projects by client ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM projects 
                WHERE client_id = ? 
                ORDER BY created_at DESC
            ''', (client_id,))
            rows = cursor.fetchall()
            return [self._row_to_model(row) for row in rows]
    
    def find_active_projects(self) -> List[Project]:
        """Find all active projects."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM projects 
                WHERE status = 'active'
                ORDER BY name
            ''', )
            rows = cursor.fetchall()
            return [self._row_to_model(row) for row in rows]
    
    def update_hours_worked(self, project_id: int, hours: float) -> bool:
        """Update hours worked for a project."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE projects 
                SET hours_worked = hours_worked + ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (hours, project_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_project_earnings(self, project_id: int) -> float:
        """Calculate total earnings for a project."""
        project = self.find_by_id(project_id)
        if not project:
            return 0.0
        
        if project.fixed_rate:
            return project.fixed_rate
        elif project.hourly_rate:
            return project.hourly_rate * project.hours_worked
        return 0.0
    
    def search(self, query: str) -> List[Project]:
        """Search projects by name or description."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            search_pattern = f"%{query}%"
            cursor.execute('''
                SELECT * FROM projects 
                WHERE name LIKE ? OR description LIKE ?
                ORDER BY name
            ''', (search_pattern, search_pattern))
            rows = cursor.fetchall()
            return [self._row_to_model(row) for row in rows]
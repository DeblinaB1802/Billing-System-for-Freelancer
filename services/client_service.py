from typing import List, Optional
import logging
from models.client import Client
from repositories.client_repository import ClientRepository
from Utils.exceptions import ClientNotFoundError, ValidationError

logger = logging.getLogger(__name__)

class ClientService:
    """Service for client business logic."""
    
    def __init__(self):
        self.repository = ClientRepository()
    
    def create_client(self, name: str, email: str, phone: str = None, 
                     company: str = None, address: str = None) -> Client:
        """Create a new client."""
        # Check if client with email already exists
        existing = self.repository.find_by_email(email)
        if existing:
            raise ValidationError(f"Client with email {email} already exists")
        
        client = Client(
            name=name.strip(),
            email=email.strip().lower(),
            phone=phone.strip() if phone else None,
            company=company.strip() if company else None,
            address=address.strip() if address else None
        )
        
        created_client = self.repository.create(client)
        logger.info(f"Created client: {created_client.display_name()}")
        return created_client
    
    def update_client(self, client_id: int, name: str = None, email: str = None,
                     phone: str = None, company: str = None, address: str = None) -> Client:
        """Update an existing client."""
        client = self.repository.find_by_id(client_id)
        if not client:
            raise ClientNotFoundError(f"Client with ID {client_id} not found")
        
        # Update only provided fields
        if name is not None:
            client.name = name.strip()
        if email is not None:
            # Check if new email conflicts with existing client
            existing = self.repository.find_by_email(email.strip().lower())
            if existing and existing.id != client_id:
                raise ValidationError(f"Client with email {email} already exists")
            client.email = email.strip().lower()
        if phone is not None:
            client.phone = phone.strip() if phone else None
        if company is not None:
            client.company = company.strip() if company else None
        if address is not None:
            client.address = address.strip() if address else None
        
        client.update_timestamp()
        updated_client = self.repository.update(client)
        logger.info(f"Updated client: {updated_client.display_name()}")
        return updated_client
    
    def delete_client(self, client_id: int) -> bool:
        """Delete a client."""
        client = self.repository.find_by_id(client_id)
        if not client:
            raise ClientNotFoundError(f"Client with ID {client_id} not found")
        
        # TODO: Check if client has invoices and handle appropriately
        success = self.repository.delete(client_id)
        if success:
            logger.info(f"Deleted client: {client.display_name()}")
        return success
    
    def get_client(self, client_id: int) -> Client:
        """Get client by ID."""
        client = self.repository.find_by_id(client_id)
        if not client:
            raise ClientNotFoundError(f"Client with ID {client_id} not found")
        return client
    
    def get_all_clients(self) -> List[Client]:
        """Get all clients."""
        return self.repository.find_all()
    
    def search_clients(self, query: str) -> List[Client]:
        """Search clients by name or company."""
        return self.repository.search(query)
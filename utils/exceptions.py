class BillingSystemException(Exception):
    """Base exception for billing system."""
    pass

class ValidationError(BillingSystemException):
    """Raised when data validation fails."""
    pass

class ClientNotFoundError(BillingSystemException):
    """Raised when client is not found."""
    pass

class ProjectNotFoundError(BillingSystemException):
    """Raised when project is not found."""
    pass

class InvoiceNotFoundError(BillingSystemException):
    """Raised when invoice is not found."""
    pass

class DatabaseError(BillingSystemException):
    """Raised when database operation fails."""
    pass
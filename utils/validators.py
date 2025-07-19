import re
from typing import Optional, Union
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from Utils.exceptions import ValidationError

class Validators:
    """Input validation utilities for the billing system."""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        if not email:
            return False
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format (Indian format)."""
        if not phone:
            return False
        
        # Remove spaces, dashes, and parentheses
        clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
        
        # Indian phone number patterns
        patterns = [
            r'^\+91[6-9]\d{9}$',  # +91 format
            r'^91[6-9]\d{9}$',    # 91 format
            r'^[6-9]\d{9}$'       # 10 digit format
        ]
        
        return any(re.match(pattern, clean_phone) for pattern in patterns)
    
    @staticmethod
    def validate_required_string(value: str, field_name: str) -> str:
        """Validate required string field."""
        if not value or not value.strip():
            raise ValidationError(f"{field_name} is required")
        
        if len(value.strip()) > 255:
            raise ValidationError(f"{field_name} must be less than 255 characters")
        
        return value.strip()
    
    @staticmethod
    def validate_optional_string(value: Optional[str], field_name: str, max_length: int = 255) -> Optional[str]:
        """Validate optional string field."""
        if not value:
            return None
        
        if len(value.strip()) > max_length:
            raise ValidationError(f"{field_name} must be less than {max_length} characters")
        
        return value.strip()
    
    @staticmethod
    def validate_amount(amount: Union[str, float, Decimal], field_name: str = "Amount") -> Decimal:
        """Validate monetary amount."""
        try:
            if isinstance(amount, str):
                # Remove currency symbols and spaces
                clean_amount = re.sub(r'[₹$,\s]', '', amount)
                decimal_amount = Decimal(clean_amount)
            else:
                decimal_amount = Decimal(str(amount))
        except (InvalidOperation, ValueError):
            raise ValidationError(f"{field_name} must be a valid number")
        
        if decimal_amount < 0:
            raise ValidationError(f"{field_name} cannot be negative")
        
        if decimal_amount > Decimal('999999.99'):
            raise ValidationError(f"{field_name} cannot exceed ₹999,999.99")
        
        # Ensure only 2 decimal places
        return decimal_amount.quantize(Decimal('0.01'))
    
    @staticmethod
    def validate_quantity(quantity: Union[str, float, int], field_name: str = "Quantity") -> float:
        """Validate quantity field."""
        try:
            qty = float(quantity)
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} must be a valid number")
        
        if qty <= 0:
            raise ValidationError(f"{field_name} must be greater than zero")
        
        if qty > 9999:
            raise ValidationError(f"{field_name} cannot exceed 9,999")
        
        return qty
    
    @staticmethod
    def validate_date(date_value: Union[str, date, datetime], field_name: str) -> date:
        """Validate date field."""
        if isinstance(date_value, datetime):
            return date_value.date()
        
        if isinstance(date_value, date):
            return date_value
        
        if isinstance(date_value, str):
            # Try common date formats
            date_formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d']
            
            for fmt in date_formats:
                try:
                    return datetime.strptime(date_value, fmt).date()
                except ValueError:
                    continue
            
            raise ValidationError(f"{field_name} must be in format YYYY-MM-DD")
        
        raise ValidationError(f"{field_name} must be a valid date")
    
    @staticmethod
    def validate_invoice_number(invoice_number: str) -> str:
        """Validate invoice number format."""
        if not invoice_number or not invoice_number.strip():
            raise ValidationError("Invoice number is required")
        
        invoice_number = invoice_number.strip()
        
        # Allow alphanumeric characters, dashes, and underscores
        if not re.match(r'^[A-Za-z0-9\-_]+$', invoice_number):
            raise ValidationError("Invoice number can only contain letters, numbers, dashes, and underscores")
        
        if len(invoice_number) > 50:
            raise ValidationError("Invoice number must be less than 50 characters")
        
        return invoice_number
    
    @staticmethod
    def validate_tax_rate(tax_rate: Union[str, float, Decimal]) -> Decimal:
        """Validate tax rate (as percentage)."""
        try:
            if isinstance(tax_rate, str):
                # Remove percentage symbol if present
                clean_rate = tax_rate.replace('%', '').strip()
                rate = Decimal(clean_rate)
            else:
                rate = Decimal(str(tax_rate))
        except (InvalidOperation, ValueError):
            raise ValidationError("Tax rate must be a valid number")
        
        if rate < 0:
            raise ValidationError("Tax rate cannot be negative")
        
        if rate > 100:
            raise ValidationError("Tax rate cannot exceed 100%")
        
        return rate / 100 if rate > 1 else rate
    
    @staticmethod
    def validate_project_status(status: str) -> str:
        """Validate project status."""
        valid_statuses = ['active', 'completed', 'on_hold', 'cancelled']
        
        if not status:
            raise ValidationError("Project status is required")
        
        status = status.lower().strip()
        
        if status not in valid_statuses:
            raise ValidationError(f"Project status must be one of: {', '.join(valid_statuses)}")
        
        return status
    
    @staticmethod
    def validate_invoice_status(status: str) -> str:
        """Validate invoice status."""
        valid_statuses = ['draft', 'sent', 'paid', 'overdue', 'cancelled']
        
        if not status:
            raise ValidationError("Invoice status is required")
        
        status = status.lower().strip()
        
        if status not in valid_statuses:
            raise ValidationError(f"Invoice status must be one of: {', '.join(valid_statuses)}")
        
        return status
    
    @staticmethod
    def validate_payment_method(method: str) -> str:
        """Validate payment method."""
        valid_methods = ['cash', 'bank_transfer', 'cheque', 'upi', 'card', 'other']
        
        if not method:
            raise ValidationError("Payment method is required")
        
        method = method.lower().strip()
        
        if method not in valid_methods:
            raise ValidationError(f"Payment method must be one of: {', '.join(valid_methods)}")
        
        return method
    
    @staticmethod
    def validate_gst_number(gst_number: Optional[str]) -> Optional[str]:
        """Validate Indian GST number format."""
        if not gst_number:
            return None
        
        gst_number = gst_number.strip().upper()
        
        # GST format: 2 digits state code + 10 chars PAN + 1 digit entity number + 1 digit Z + 1 check digit
        gst_pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
        
        if not re.match(gst_pattern, gst_number):
            raise ValidationError("Invalid GST number format")
        
        return gst_number
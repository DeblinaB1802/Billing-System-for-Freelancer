from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Union, List, Dict, Any
import re

class Formatters:
    """Data formatting utilities for the billing system."""
    
    @staticmethod
    def format_currency(amount: Union[Decimal, float, int], currency_symbol: str = "₹") -> str:
        """Format amount as currency with Indian number formatting."""
        if amount is None:
            return f"{currency_symbol}0.00"
        
        try:
            decimal_amount = Decimal(str(amount))
        except:
            return f"{currency_symbol}0.00"
        
        # Convert to float for formatting
        float_amount = float(decimal_amount)
        
        # Format with 2 decimal places
        formatted = f"{float_amount:,.2f}"
        
        # Convert to Indian number system (lakhs, crores)
        if float_amount >= 10000000:  # 1 crore
            crores = float_amount / 10000000
            return f"{currency_symbol}{crores:,.2f} Cr"
        elif float_amount >= 100000:  # 1 lakh
            lakhs = float_amount / 100000
            return f"{currency_symbol}{lakhs:,.2f} L"
        
        return f"{currency_symbol}{formatted}"
    
    @staticmethod
    def format_currency_simple(amount: Union[Decimal, float, int], currency_symbol: str = "₹") -> str:
        """Format amount as simple currency without lakhs/crores."""
        if amount is None:
            return f"{currency_symbol}0.00"
        
        try:
            decimal_amount = Decimal(str(amount))
            return f"{currency_symbol}{decimal_amount:,.2f}"
        except:
            return f"{currency_symbol}0.00"
    
    @staticmethod
    def format_date(date_value: Union[date, datetime, str], format_type: str = "display") -> str:
        """Format date for display or storage."""
        if not date_value:
            return ""
        
        # Convert string to date if needed
        if isinstance(date_value, str):
            try:
                date_value = datetime.strptime(date_value, "%Y-%m-%d").date()
            except ValueError:
                return date_value
        
        # Convert datetime to date if needed
        if isinstance(date_value, datetime):
            date_value = date_value.date()
        
        if format_type == "display":
            return date_value.strftime("%B %d, %Y")  # January 15, 2024
        elif format_type == "short":
            return date_value.strftime("%d/%m/%Y")   # 15/01/2024
        elif format_type == "iso":
            return date_value.strftime("%Y-%m-%d")   # 2024-01-15
        elif format_type == "filename":
            return date_value.strftime("%Y%m%d")     # 20240115
        else:
            return date_value.strftime("%B %d, %Y")
    
    @staticmethod
    def format_phone(phone: Optional[str]) -> Optional[str]:
        """Format phone number for display."""
        if not phone:
            return None
        
        # Remove all non-digit characters except +
        clean_phone = re.sub(r'[^\d+]', '', phone)
        
        # Handle Indian phone numbers
        if clean_phone.startswith('+91'):
            number = clean_phone[3:]
            if len(number) == 10:
                return f"+91 {number[:5]} {number[5:]}"
        elif clean_phone.startswith('91') and len(clean_phone) == 12:
            number = clean_phone[2:]
            return f"+91 {number[:5]} {number[5:]}"
        elif len(clean_phone) == 10:
            return f"+91 {clean_phone[:5]} {clean_phone[5:]}"
        
        return phone  # Return original if can't format
    
    @staticmethod
    def format_invoice_number(invoice_number: str, prefix: Optional[str] = None) -> str:
        """Format invoice number with optional prefix."""
        if not invoice_number:
            return ""
        
        if prefix:
            return f"{prefix}-{invoice_number}"
        
        return invoice_number.upper()
    
    @staticmethod
    def format_percentage(value: Union[Decimal, float, int], decimal_places: int = 2) -> str:
        """Format value as percentage."""
        if value is None:
            return "0%"
        
        try:
            decimal_value = Decimal(str(value))
            # If value is less than 1, assume it's already a decimal (e.g., 0.18 for 18%)
            if decimal_value < 1:
                percentage = decimal_value * 100
            else:
                percentage = decimal_value
            
            return f"{percentage:.{decimal_places}f}%"
        except:
            return "0%"
    
    @staticmethod
    def format_quantity(quantity: Union[float, int, Decimal], unit: Optional[str] = None) -> str:
        """Format quantity with optional unit."""
        if quantity is None:
            return "0"
        
        try:
            # Remove trailing zeros after decimal point
            if isinstance(quantity, Decimal):
                formatted = f"{quantity:f}".rstrip('0').rstrip('.')
            else:
                formatted = f"{float(quantity):g}"
            
            if unit:
                return f"{formatted} {unit}"
            
            return formatted
        except:
            return "0"
    
    @staticmethod
    def format_status(status: str) -> str:
        """Format status for display."""
        if not status:
            return ""
        
        # Replace underscores with spaces and title case
        return status.replace('_', ' ').title()
    
    @staticmethod
    def format_address(address_dict: Dict[str, Any]) -> str:
        """Format address dictionary into a single string."""
        if not address_dict:
            return ""
        
        parts = []
        
        # Common address fields
        fields = ['street', 'city', 'state', 'postal_code', 'country']
        
        for field in fields:
            value = address_dict.get(field)
            if value and str(value).strip():
                parts.append(str(value).strip())
        
        return ', '.join(parts)
    
    @staticmethod
    def format_name(first_name: Optional[str], last_name: Optional[str]) -> str:
        """Format full name from first and last name."""
        parts = []
        
        if first_name and first_name.strip():
            parts.append(first_name.strip())
        
        if last_name and last_name.strip():
            parts.append(last_name.strip())
        
        return ' '.join(parts)
    
    @staticmethod
    def format_table_row(data: List[Any], widths: List[int], alignment: List[str] = None) -> str:
        """Format a table row with specified column widths and alignment."""
        if not data or not widths:
            return ""
        
        if alignment is None:
            alignment = ['left'] * len(data)
        
        formatted_cells = []
        
        for i, (value, width) in enumerate(zip(data, widths)):
            str_value = str(value) if value is not None else ""
            align = alignment[i] if i < len(alignment) else 'left'
            
            if align == 'right':
                cell = str_value.rjust(width)
            elif align == 'center':
                cell = str_value.center(width)
            else:  # left
                cell = str_value.ljust(width)
            
            # Truncate if too long
            if len(cell) > width:
                cell = cell[:width-3] + "..."
            
            formatted_cells.append(cell)
        
        return " | ".join(formatted_cells)
    
    @staticmethod
    def format_duration_days(start_date: date, end_date: Optional[date] = None) -> str:
        """Format duration in days between two dates."""
        if not start_date:
            return "N/A"
        
        if not end_date:
            end_date = date.today()
        
        duration = (end_date - start_date).days
        
        if duration == 0:
            return "Today"
        elif duration == 1:
            return "1 day"
        elif duration < 30:
            return f"{duration} days"
        elif duration < 365:
            months = duration // 30
            remaining_days = duration % 30
            if remaining_days == 0:
                return f"{months} month{'s' if months > 1 else ''}"
            else:
                return f"{months} month{'s' if months > 1 else ''}, {remaining_days} day{'s' if remaining_days > 1 else ''}"
        else:
            years = duration // 365
            remaining_days = duration % 365
            months = remaining_days // 30
            if months == 0:
                return f"{years} year{'s' if years > 1 else ''}"
            else:
                return f"{years} year{'s' if years > 1 else ''}, {months} month{'s' if months > 1 else ''}"
    
    @staticmethod
    def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
        """Truncate text to specified length with suffix."""
        if not text:
            return ""
        
        if len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human readable format."""
        if size_bytes == 0:
            return "0 B"
        
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0
        size = float(size_bytes)
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        return f"{size:.1f} {units[unit_index]}"
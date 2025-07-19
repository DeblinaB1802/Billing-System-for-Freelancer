# Freelance Billing System - Professional Modular Architecture

## Project Structure
```
freelance_billing_system/
├── main.py                     # Entry point
├── config/
│   ├── __init__.py
│   ├── settings.py            # Configuration settings
│   └── database.py            # Database configuration
├── models/
│   ├── __init__.py
│   ├── base.py               # Base model class
│   ├── client.py             # Client model
│   ├── project.py            # Project model
│   ├── invoice.py            # Invoice model
│   └── payment.py            # Payment model
├── services/
│   ├── __init__.py
│   ├── client_service.py     # Client business logic
│   ├── project_service.py    # Project business logic
│   ├── invoice_service.py    # Invoice business logic
│   ├── payment_service.py    # Payment business logic
│   └── report_service.py     # Report generation
├── repositories/
│   ├── __init__.py
│   ├── base_repository.py    # Base repository pattern
│   ├── client_repository.py  # Client data access
│   ├── project_repository.py # Project data access
│   ├── invoice_repository.py # Invoice data access
│   └── payment_repository.py # Payment data access
├── utils/
│   ├── __init__.py
│   ├── validators.py         # Input validation
│   ├── formatters.py         # Data formatting
│   ├── pdf_generator.py      # PDF generation
│   └── exceptions.py         # Custom exceptions
├── cli/
│   ├── __init__.py
│   ├── main_menu.py         # Main CLI interface
│   ├── client_menu.py       # Client management CLI
│   ├── project_menu.py      # Project management CLI
│   ├── invoice_menu.py      # Invoice management CLI
│   └── report_menu.py       # Report generation CLI
└── tests/
    ├── __init__.py
    ├── test_models.py
    ├── test_services.py
    └── test_repositories.py
```
"""
Modular Monolith Architecture Structure

This file documents the folder hierarchy and architecture patterns.
Run this file to see the structure visualization.
"""

STRUCTURE = """
app/
├── modules/                          # Domain modules (microservice-ready)
│   ├── __init__.py
│   │
│   ├── auth/                         # Authentication Module
│   │   ├── __init__.py               # PUBLIC API - Only import from here
│   │   ├── entities/                 # Domain models (if any)
│   │   ├── repositories/             # Data access (uses users module)
│   │   ├── services/                 # Business logic
│   │   │   └── auth_service.py
│   │   ├── controllers/               # API endpoints (transport layer)
│   │   │   └── auth_controller.py
│   │   └── schemas/                  # Request/response models
│   │       └── auth_schemas.py
│   │
│   ├── users/                        # User Management Module
│   │   ├── __init__.py               # PUBLIC API
│   │   ├── entities/
│   │   │   └── user_entity.py
│   │   ├── repositories/
│   │   │   └── user_repository.py
│   │   ├── services/
│   │   │   └── user_service.py
│   │   ├── controllers/              # (to be created)
│   │   └── schemas/                  # (to be created)
│   │
│   ├── cases/                        # Cases Module
│   │   ├── __init__.py               # PUBLIC API
│   │   ├── entities/
│   │   │   ├── case_entity.py
│   │   │   └── case_status_history_entity.py
│   │   ├── repositories/
│   │   │   └── case_repository.py
│   │   ├── services/
│   │   │   └── case_service.py
│   │   ├── controllers/              # (to be created)
│   │   └── schemas/                  # (to be created)
│   │
│   ├── incidents/                    # Incidents Module
│   │   ├── __init__.py               # PUBLIC API
│   │   ├── entities/
│   │   │   └── incident_entity.py
│   │   ├── repositories/
│   │   │   └── incident_repository.py
│   │   ├── services/
│   │   │   └── incident_service.py
│   │   ├── controllers/              # (to be created)
│   │   └── schemas/                  # (to be created)
│   │
│   └── media/                        # Media Module
│       ├── __init__.py               # PUBLIC API
│       ├── entities/
│       │   └── media_entity.py
│       ├── repositories/
│       │   └── media_repository.py
│       ├── services/
│       │   └── media_service.py
│       ├── controllers/              # (to be created)
│       └── schemas/                  # (to be created)
│
├── shared/                           # Cross-cutting concerns
│   ├── __init__.py
│   │
│   ├── database/                     # Database configuration
│   │   ├── __init__.py
│   │   ├── dependencies.py           # get_db() dependency
│   │   └── migrations.py             # Migration utilities
│   │
│   ├── security/                     # Security utilities
│   │   └── __init__.py               # Password hashing, tokens
│   │
│   ├── exceptions/                   # Exception classes
│   │   └── __init__.py
│   │
│   ├── responses/                    # Response models
│   │   └── __init__.py
│   │
│   ├── constants/                    # Application constants
│   │   └── __init__.py
│   │
│   ├── types/                        # Type definitions
│   │   └── __init__.py
│   │
│   ├── utils/                        # Utility functions
│   │   └── __init__.py
│   │
│   ├── middleware/                   # Middleware components
│   │   ├── __init__.py
│   │   └── exception_handlers.py
│   │
│   └── communication/                # Inter-module communication
│       └── __init__.py               # Internal Service Bus
│
├── core/                             # Legacy core (being phased out)
│   ├── base.py                       # (moved to shared/database)
│   ├── database.py                   # (moved to shared/database)
│   ├── config.py
│   ├── dependencies.py               # (moved to shared/database/dependencies)
│   ├── exception_handlers.py         # (moved to shared/middleware)
│   ├── security.py                   # (moved to shared/security)
│   └── ...
│
├── common/                           # Legacy common (being phased out)
│   ├── constants.py                  # (moved to shared/constants)
│   ├── exceptions.py                 # (moved to shared/exceptions)
│   ├── responses.py                  # (moved to shared/responses)
│   └── ...
│
└── main.py                           # Application entry point
"""

ARCHITECTURE_RULES = """
ARCHITECTURE RULES:
==================

1. MODULE BOUNDARIES:
   - Modules CANNOT import directly from other modules' internal folders
   - Only import from module's __init__.py (public API)
   - Example: from app.modules.users import UserService (✅)
   - Example: from app.modules.users.services.user_service import UserService (❌)

2. BUSINESS LOGIC vs TRANSPORT LOGIC:
   - Business Logic: Lives in services/ (domain rules, validation, orchestration)
   - Transport Logic: Lives in controllers/ (HTTP handling, request/response mapping)
   - Entities: Pure domain models in entities/
   - Repositories: Data access abstraction in repositories/

3. INTER-MODULE COMMUNICATION:
   - Use Internal Service Bus (app.shared.communication)
   - Modules register their public services
   - Other modules access through service bus
   - Prevents tight coupling

4. DATABASE MIGRATIONS:
   - Each module can have its own migrations
   - When splitting to microservices, each module gets its own database
   - Migrations are organized by module in alembic/versions/

5. SHARED CODE:
   - Only truly cross-cutting concerns go in shared/
   - Database, security, exceptions, responses, constants
   - NO business logic in shared/

6. DEPENDENCY INJECTION:
   - Services receive repositories via constructor
   - Controllers receive services via FastAPI Depends()
   - Enables testing and loose coupling
"""

COMMUNICATION_PATTERN = """
INTER-MODULE COMMUNICATION PATTERN:
===================================

Example: Cases module needs to check if user exists

# In cases/services/case_service.py
from app.shared.communication import get_service_bus

class CaseService:
    async def create_case(self, db, user_id, ...):
        # Get user service through service bus
        service_bus = get_service_bus()
        user_service = service_bus.get_service("users")
        
        # Use user service (no direct import!)
        user = await user_service.get_user_by_id(db, user_id)
        ...

# In main.py (startup)
from app.shared.communication import get_service_bus
from app.modules.users import UserService, UserRepository

service_bus = get_service_bus()
user_repo = UserRepository()
user_service = UserService(user_repo)
service_bus.register_service("users", user_service)
"""

if __name__ == "__main__":
    print("=" * 60)
    print("MODULAR MONOLITH ARCHITECTURE STRUCTURE")
    print("=" * 60)
    print(STRUCTURE)
    print("\n")
    print(ARCHITECTURE_RULES)
    print("\n")
    print(COMMUNICATION_PATTERN)

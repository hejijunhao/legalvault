# LegalVault Backend Documentation

## Overview

The LegalVault backend is built as a modern, scalable API service that powers the AI-driven legal workstation. It follows domain-driven design principles with a clear separation of concerns and a layered architecture. The backend is designed to support multi-tenancy with enterprise-level data isolation at the schema level.

## Tech Stack

- **Framework**: FastAPI - A modern, high-performance web framework for building APIs with Python
- **Database**: PostgreSQL via Supabase with pgBouncer for connection pooling
- **ORM**: SQLAlchemy (async) for database interactions
- **Authentication**: JWT-based authentication with Supabase Auth integration
- **AI Components**: LangChain for orchestrating workflows, Perplexity Sonar API for research
- **Validation**: Pydantic for data validation and serialization
- **Async Programming**: Leverages Python's async capabilities for improved performance

## Directory Structure

```
backend/
├── api/
│   └── routes/           # FastAPI route definitions
│       ├── auth/         # Authentication endpoints
│       ├── research/     # Research feature endpoints
│       └── ...
├── core/                 # Core application components
│   ├── auth.py          # Authentication utilities
│   ├── config.py        # Application configuration
│   ├── database.py      # Database connection management
│   └── ...
├── models/              # Data models and business logic
│   ├── database/        # SQLAlchemy table definitions
│   ├── domain/          # Business logic and operations
│   ├── dtos/            # Data Transfer Objects
│   ├── enums/           # Enumeration definitions
│   └── schemas/         # Pydantic validation schemas
├── services/            # Service layer components
│   ├── workflow/        # Workflow orchestration
│   ├── initializer/     # System initialization
│   └── executor/        # Task execution services
├── scripts/             # Utility scripts
├── certs/               # SSL certificates
└── main.py              # Application entry point
```

## Core Components

### Database Configuration

The database connection is managed in `core/database.py` with the following key features:

- **Async Engine**: Uses SQLAlchemy's async engine with asyncpg driver
- **SSL Configuration**: Custom SSL context for secure database connections
- **pgBouncer Compatibility**: Special configuration to work with pgBouncer in transaction pooling mode
- **Connection Pooling**: Uses NullPool to delegate connection pooling to pgBouncer
- **Session Management**: Provides async session factories with proper error handling

Example of database session usage:

```python
from core.database import get_db

@router.get("/items")
async def get_items(session: AsyncSession = Depends(get_db)):
    # Use session for database operations
    result = await session.execute(select(Item))
    return result.scalars().all()
```

### Authentication

Authentication is implemented in `core/auth.py` with JWT tokens and integration with Supabase Auth:

- **Token Validation**: OAuth2PasswordBearer scheme with JWT decoding
- **User Retrieval**: Fetches user data from database with pgBouncer compatibility
- **Error Handling**: Comprehensive error handling for authentication failures

Example of protected endpoint:

```python
from core.auth import get_current_user

@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"user_id": current_user.id, "email": current_user.email}
```

## Domain Models

The application follows a domain-driven design approach with clear separation between:

1. **Database Models**: SQLAlchemy table definitions in `models/database/`
2. **Domain Models**: Business logic in `models/domain/`
3. **Domain Operations**: Complex queries and operations in `models/domain/*/operations.py`
4. **DTOs**: Data Transfer Objects in `models/dtos/` for API communication
5. **Schemas**: Pydantic validation schemas in `models/schemas/`

This separation ensures clean architecture and maintainable code.

## Multi-Tenant Architecture

LegalVault implements multi-tenancy with schema-level isolation:

- **Public Schema**: Contains cross-enterprise tables and shared resources
- **Enterprise Schemas**: Each enterprise has its own schema (`enterprise_*.*`) for data isolation
- **Abstract Base Classes**: Define shared structure without creating tables
- **Blueprint Classes**: Inherit from abstract classes for visualization and testing
- **Concrete Classes**: Enterprise-specific implementations in isolated schemas

## Research Feature

The Research feature is a core component of LegalVault, providing AI-powered legal research capabilities:

### Components

1. **Domain Models**:
   - `ResearchSearch`: Represents a search session with validation and categorization logic
   - `ResearchMessage`: Handles message validation, formatting, and categorization

2. **Database Models**:
   - `PublicSearch`: Stores metadata about search sessions
   - `PublicSearchMessage`: Stores individual messages within a conversation

3. **Operations**:
   - `ResearchOperations`: Manages persistence and retrieval for search sessions
   - `SearchMessageOperations`: Handles message-related database operations

4. **API Routes**:
   - `/api/research/searches`: Endpoints for managing search sessions
   - `/api/research/searches/{search_id}/continue`: Follow-up queries in a session
   - `/api/research/searches/{search_id}/messages`: Message management

5. **Workflow**:
   - `ResearchSearchWorkflow`: Orchestrates the interaction between domain models and external services
   - Handles query analysis, enhancement, and external API integration

### External API Integration

The Research feature integrates with Perplexity's Sonar API for legal research:

- **API Client**: Implemented in the workflow layer with proper error handling
- **Query Enhancement**: Uses LLMs to analyze and enhance legal queries
- **Response Processing**: Parses API responses and extracts citations

## Error Handling

The application implements comprehensive error handling:

1. **Domain-Specific Errors**: Custom error classes for different types of failures
2. **API Error Responses**: Structured error responses with appropriate HTTP status codes
3. **Database Error Handling**: Special handling for pgBouncer-related errors with retry logic
4. **Logging**: Detailed logging for debugging and monitoring

## Async Programming

LegalVault leverages Python's async capabilities for improved performance:

- **Async Database Operations**: All database interactions use SQLAlchemy's async API
- **Async API Endpoints**: FastAPI routes are implemented as async functions
- **Async External API Calls**: Integration with external services uses async HTTP clients

## Environment Configuration

The application uses environment variables for configuration, managed in `core/config.py`:

- **Database URLs**: Different URLs for transaction and session pooling modes
- **JWT Settings**: Secret key and token expiration
- **API Keys**: Keys for external services like Perplexity
- **CORS Settings**: Allowed origins for API access

## Development Guidelines

1. **Follow Domain-Driven Design**: Keep business logic in domain models, separate from API and database layers
2. **Use Async Properly**: Ensure all I/O operations are async and properly awaited
3. **Handle pgBouncer Compatibility**: Use the provided utilities for database operations
4. **Implement Proper Validation**: Use Pydantic schemas for request/response validation
5. **Document API Endpoints**: Add docstrings and type hints for clarity
6. **Write Unit Tests**: Ensure new features have appropriate test coverage

## Common Issues and Solutions

### pgBouncer Prepared Statement Errors

When using asyncpg with pgBouncer in transaction pooling mode, you may encounter prepared statement errors. To avoid these:

1. Use the provided `_execute_query` method in operation classes
2. Set `no_parameters=True` in execution options
3. Disable prepared statement caches

### Authentication Token Issues

If experiencing authentication problems:

1. Ensure the `tokenUrl` in `OAuth2PasswordBearer` matches the actual endpoint path
2. Check that JWT secret keys match between token creation and validation
3. Verify token expiration settings

## Deployment

The backend is deployed on Fly.io with the following considerations:

- **SSL Certificates**: Production certificates are stored in the `./certs/` directory
- **Environment Variables**: Set through Fly.io secrets management
- **Database Connection**: Uses pgBouncer for connection pooling
- **Scaling**: Horizontal scaling with multiple instances

## Future Enhancements

1. **Redis Integration**: For Virtual Paralegal short-term memory
2. **WebSocket Support**: For real-time features and notifications
3. **Vector Database**: For semantic search capabilities
4. **Caching Layer**: For frequently accessed data
5. **Migration to AWS**: Planned move to AWS Elastic Beanstalk
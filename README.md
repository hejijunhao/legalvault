
**TECH STACK**

Frontend Layer
* Framework: Next.js (React)
* Language: TypeScript
* UI Components: Tremor UI
* Styling: Tailwind CSS
* State/Data Management: Direct Supabase client integration

Backend Layer
* Framework: FastAPI (Python)
* Core Services:
   * LangChain for AI orchestration
   * HuggingFace for AI models
   * Workflow tracking service

Data Layer
* Database: Supabase (PostgreSQL)
* Authentication: Supabase Auth
* Vectorisation/Embedding: Supabase, Pinecone [in future]
* Conversation history: MongoDB [in future]
* Caching: Redis [in future]
* Real-time capabilities via WebSocket

Infrastructure Layer
* AWS EB for Backend
* Vercel for Frontend
* REST API endpoints with WebSocket support
* AI/ML service orchestration

Development Layer
* Type safety with TypeScript & Pydantic
* Database: SQLModel/Alembic migrations, Supabase Dashboard
* API: FastAPI CRUD endpoints
* Error handling & fallback strategies
* Custom React hooks
* Logging & caching utilities

Database Structure
* User -> VirtualParalegal relationship (bi-directional)
* VirtualParalegal -> Abilities -> UniqueAbility hierarchy
* First ability: TaskManagementAbility (JSONB schemas/workflows)
* SQLModel/PostgreSQL with validated Alembic migrations


**APPLICATION ARCHITECTURE**

LegalVault/
├── backend/
│   ├── admin/            # Admin configurations
│   ├── alembic/          # Database migrations
│   │   ├── versions/     # Migration version files
│   │   ├── env.py       # Alembic environment configuration
│   │   └── alembic.ini  # Alembic configuration file
│   ├── api/             # API endpoints/routes
│   │   └── routes/      # Routes directory
│   │       ├── taskmanagement.py  # TaskManagement routes
│   │       ├── receiveemail.py    # Email handling routes
│   │       └── profile_pictures.py # Profile picture routes
│   ├── core/            # Core application logic
│   │   ├── __init__.py
│   │   ├── database.py  # Supabase/Database setup
│   │   ├── orchestrator.py  # Main orchestrator logic
│   │   ├── llm/         # LLM components
│   │   │   ├── __init__.py
│   │   │   ├── base.py  # Base LLM configurations
│   │   │   ├── orchestrator.py  # Intent classification LLM
│   │   │   └── abilities/      # Ability-specific LLM logic
│   │   │       ├── __init__.py
│   │   │       └── taskmanager.py
│   ├── models/          # Data models layer
│   │   ├── database/    # Database models (SQLModel)
│   │   │   ├── __init__.py
│   │   │   ├── ability.py
│   │   │   ├── behaviour.py
│   │   │   ├── paralegal.py
│   │   │   ├── profile_picture.py
│   │   │   ├── ability_taskmanagement.py
│   │   │   ├── ability_receiveemail.py
│   │   │   └── user.py
│   │   ├── domain/      # Business logic models
│   │   │   ├── __init__.py
│   │   │   ├── ability.py
│   │   │   ├── behaviour.py
│   │   │   ├── paralegal.py
│   │   │   ├── ability_taskmanagement.py
│   │   │   ├── ability_receiveemail.py
│   │   │   ├── operations_taskmanagement.py
│   │   │   ├── operations_receiveemail.py
│   │   │   └── user.py
│   │   └── schemas/     # API schemas (Pydantic)
│   │       ├── __init__.py
│   │       ├── ability.py
│   │       ├── behavior.py
│   │       ├── paralegal.py
│   │       ├── profile_picture.py
│   │       ├── ability_taskmanagement.py
│   │       ├── ability_receiveemail.py
│   │       └── user.py
│   ├── scripts/         # Scripts directory
│   │   ├── initialize_taskmanagement_abilities.py
│   │   ├── initialize_receiveemail_abilities.py
│   │   └── initialize_profile_pictures.py
│   ├── services/        # Business logic services
│   │   ├── __init__.py
│   │   ├── initializers/  # Operation initializers
│   │   │   ├── __init__.py
│   │   │   ├── op_taskmanagement_initializer.py
│   │   │   └── op_receiveemail_initializer.py
│   │   ├── executors/   # Executors directory
│   │   │   ├── __init__.py
│   │   │   ├── taskmanagement_executor.py
│   │   │   └── receiveemail_executor.py
│   │   ├── workflow/    # Workflow directory
│   │   │   ├── __init__.py
│   │   │   ├── taskmanagement_workflow.py
│   │   │   └── receiveemail_workflow.py
│   │   └── workflow_tracker.py
│   ├── tests/           # Test directory
│   │   ├── __init__.py
│   │   ├── conftest.py  # pytest configuration
│   │   ├── test_database.py
│   │   └── test_models.py
│   ├── utils/           # Utility functions
│   │   ├── cache.py     # Caching utilities
│   │   ├── fallback.py  # Fallback strategies
│   │   └── logging.py   # Basic monitoring
│   ├── .env             # Environment variables
│   ├── alembic.ini      # Alembic configuration
│   ├── __init__.py
│   ├── main.py         # FastAPI entry point
│   └── requirements.txt
│
├── frontend/           # Next.js frontend
│   ├── public/
│   │   ├── fonts/
│   │   └── images/
│   │       └── vp/
│   │           ├── professional.png
│   │           ├── casual.png
│   │           ├── modern.png
│   │           ├── traditional.png
│   │           └── creative.png
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── lib/
│   │   │   ├── api.ts
│   │   │   └── supabase.ts
│   │   ├── styles/
│   │   └── types/
│   ├── .env.local
│   └── tailwind.config.ts
│
├── .gitignore
├── README.md
└── requirements.txt

**ADDING/MANAGING ABILITIES**

For each new Ability, you need:
1. `NewAbility.py` files in all three folders:
    - `models/database/` - SQLModel for database structure (How the car specs are stored in manufacturer's database)
    - `models/domain/` - Business logic and behavior (What this car model is and how it should behave)
    - `models/schemas/` - Pydantic models for API validation (Rules for validating car operations and user inputs)
2. `operations_newability.py` in `models/domain/`:
    - What operations exist
    - Their structure via input/output schemas (What inputs each function accepts, like pedal pressure)
    - Their workflows
    - Their constraints
    - Their permissions (Who can use which functions, like license requirements)
3. `op_newability_initializer.py` in `services/initializers/`:
    - Takes function descriptions and formats them for database
    - Handles CRUD operations for these operations (adding/updating/removing)
    - Manages updates when operations change (Updates documentation when functions change)
4. `initialize_newability_abilities.py` in `scripts/`:
    - Provides the entry point to run the initializer (Controls when to publish/update)
    - Used in deployment scripts (Used during initial setup)
    - Used for maintenance/updates (Manages maintenance of function documentation)
5. `newability_executor.py` in `services/executors/`:
    - Implements actual operation logic (The driver who actually operates the functions)
    - Handles API calls and integrations (Knows how to physically operate each control)
    - Manages error handling (Knows what to do if something fails)
6. `newability_workflow.py` in `services/workflow/`:
    - Orchestrates operation execution (GPS system planning the route)
    - Validates inputs and conditions (Driving instructor checking conditions)
    - Manages operation flow (Ensures functions are used in correct order)
7. API routes in `api/routes/newability.py`:
    - Defines endpoints and routes (Road infrastructure)
    - Handles request/response (Traffic control)
    - Manages authentication/authorization (Road access and rules)

This structure separates:
- Domain logic - What things are (What the car is)
- Infrastructure concerns - How things are stored (How car specs are recorded)
- Application services - How things change (How to drive the car)
- Scripts - When things change (When to update the manual)
- Execution - What actually happens (Actually driving the car)
- Orchestration - How things flow (Navigation and instruction)
- Access - How things are reached (Roads and traffic control)
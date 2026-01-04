# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LegalVault is an AI-powered legal research platform focused on Singapore law. The Research feature is fully operational; Workspace, Library, and Virtual Paralegal features are in development.

## Common Commands

### Backend (FastAPI)

```bash
cd backend
source venv/bin/activate        # Activate virtual environment
uvicorn main:app --reload       # Run development server (port 8000)
pytest                          # Run all tests
pytest tests/test_file.py       # Run single test file
pytest tests/test_file.py::test_function  # Run single test
alembic upgrade head            # Run database migrations
alembic revision --autogenerate -m "description"  # Create new migration
```

### Frontend (Next.js)

```bash
cd frontend
npm run dev      # Run development server (port 3000)
npm run build    # Production build
npm run lint     # ESLint
npm run format   # Prettier
```

## Architecture

### Backend - Clean Domain-Driven Design

The backend follows a strict three-layer architecture:

1. **API Layer** (`api/routes/`) - FastAPI endpoints with Pydantic validation
2. **Domain Layer** (`models/domain/`) - Business logic in Operation classes (e.g., `search_operations.py`, `operations_client.py`)
3. **Data Layer** (`models/database/`) - SQLModel ORM models
4. **Service Layer** (`services/`) - Orchestrates complex workflows
   - `executors/` - Execute single operations
   - `workflow/` - Orchestrate multi-step processes (e.g., `search_workflow.py`)
   - `initializers/` - Data initialization

Key patterns:
- DTOs in `models/dtos/` for API request/response schemas
- Enums in `models/enums/` shared across layers
- Database uses multi-schema architecture (public, vault)

### Frontend - Next.js App Router

```
frontend/src/
├── app/
│   ├── (app)/       # Protected routes (research, workspace, library, paralegal)
│   └── (auth)/      # Authentication routes
├── components/      # React components (ui/ for primitives)
├── contexts/        # React Context providers
├── hooks/           # Custom React hooks
├── lib/             # Utilities and helpers
├── services/        # API integration layer
├── store/           # Zustand global state
└── types/           # TypeScript definitions
```

Key patterns:
- Radix UI primitives with Tailwind CSS styling
- React Context for feature-specific state, Zustand for global state
- Centralized API client with auth in `services/`

### Research Feature Flow

The core research flow uses:
1. `api/routes/research/search.py` - API endpoint
2. `services/workflow/research/search_workflow.py` - Orchestrates:
   - GPT-4o-mini for query analysis and classification
   - Perplexity Sonar Pro for legal search with Singapore law prioritization
3. `models/domain/research/search_operations.py` - Database persistence

## Key Integrations

- **Auth**: Supabase Auth with JWT
- **Database**: PostgreSQL via Supabase (asyncpg + SQLModel)
- **AI**: OpenAI (GPT-4o-mini), Perplexity (Sonar Pro)
- **Hosting**: Backend on AWS Elastic Beanstalk, Frontend on Vercel

## Environment Variables

Backend requires: `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `OPENAI_API_KEY`, `PERPLEXITY_API_KEY`, `SUPABASE_JWT_SECRET`

Frontend requires: `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `NEXT_PUBLIC_API_URL`

## Refactoring Documentation

See `docs/refactoring-*.md` for comprehensive proposals to simplify the codebase:
- `refactoring-overview.md` - Summary and priority matrix
- `refactoring-backend.md` - Backend simplification (potential 66% reduction)
- `refactoring-frontend.md` - Frontend consolidation proposals

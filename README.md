# LegalVault - AI-Powered Legal Research Platform

LegalVault is a comprehensive legal technology platform designed to revolutionize how legal professionals conduct research, manage documents, and interact with AI-powered virtual assistants. Built with a focus on Singapore's legal ecosystem, the platform combines advanced AI capabilities with intuitive user interfaces to streamline legal workflows.

## 🚀 Overview

LegalVault is currently in **version 1.0.8-beta** with the Research feature fully operational, while Workspace, Library, and Virtual Paralegal features are in advanced stages of development.

### Key Features

- **🔍 AI-Powered Legal Research** (Fully Implemented)
  - Intelligent query analysis and categorization
  - Singapore law prioritization with case hierarchy
  - Real-time streaming responses with citations
  - Conversation threading for follow-up questions
  
- **📚 Document Library** (72% Complete)
  - Smart document storage and understanding
  - Collections management (ClauseBank, Templates, Precedents)
  - Context-aware insights and relationships
  
- **💼 Workspace** (65% Complete)
  - Client matter management
  - Project and task tracking
  - Document drafting capabilities
  
- **🤖 Virtual Paralegal** (68% Complete)
  - Customizable AI assistants
  - Task management abilities
  - Long-term memory and learning

## 🛠️ Technology Stack

### Frontend
- **Framework**: Next.js 15.2.3 (React 18.2.0)
- **Language**: TypeScript
- **UI Framework**: Radix UI primitives with custom components
- **Styling**: Tailwind CSS with CSS-in-JS utilities
- **State Management**: 
  - React Context API (Auth, Research)
  - Zustand for global state
- **Form Handling**: React Hook Form with Zod validation
- **Data Fetching**: Custom API layer with caching

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL (via Supabase)
- **ORM**: SQLModel with Alembic migrations
- **Authentication**: Supabase Auth with JWT
- **AI/ML Integration**:
  - OpenAI GPT-4o-mini for query analysis
  - Perplexity Sonar Pro for legal search
  - LangChain for orchestration (prepared)
- **Architecture**: Clean Domain-Driven Design

### Infrastructure
- **Backend Hosting**: AWS Elastic Beanstalk
- **Frontend Hosting**: Vercel
- **Database**: Supabase (PostgreSQL with pgBouncer)
- **Authentication**: Supabase Auth
- **File Storage**: Supabase Storage (planned)

## 📁 Project Structure

```
LegalVault/
├── backend/
│   ├── alembic/             # Database migrations
│   ├── api/                 # API routes and endpoints
│   │   └── routes/
│   │       ├── auth/        # Authentication endpoints
│   │       ├── research/    # Research feature endpoints
│   │       ├── workspace/   # Workspace management
│   │       └── paralegal/   # Virtual paralegal endpoints
│   ├── core/                # Core application logic
│   │   ├── auth.py          # Authentication logic
│   │   ├── config.py        # Configuration management
│   │   ├── database.py      # Database connections
│   │   └── llm.py           # LLM integrations
│   ├── models/              # Three-layer model architecture
│   │   ├── database/        # SQLModel database models
│   │   ├── domain/          # Business logic and operations
│   │   ├── schemas/         # Pydantic API schemas
│   │   ├── dtos/            # Data transfer objects
│   │   └── enums/           # Shared enumerations
│   ├── services/            # Business logic services
│   │   ├── executors/       # Operation executors
│   │   ├── workflow/        # Workflow orchestration
│   │   └── initializers/    # Data initializers
│   └── main.py              # FastAPI application entry
│
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js App Router
│   │   │   ├── (app)/       # Protected app routes
│   │   │   ├── (auth)/      # Authentication routes
│   │   │   └── layout.tsx   # Root layout
│   │   ├── components/      # React components
│   │   │   ├── ui/          # Reusable UI primitives
│   │   │   ├── research/    # Research feature components
│   │   │   ├── library/     # Library components
│   │   │   └── workspace/   # Workspace components
│   │   ├── contexts/        # React contexts
│   │   ├── hooks/           # Custom React hooks
│   │   ├── lib/             # Utilities and helpers
│   │   ├── services/        # API integration layer
│   │   └── types/           # TypeScript type definitions
│   └── package.json         # Frontend dependencies
└── README.md                # This file
```

## 🏗️ Architecture Overview

### Backend Architecture

The backend follows a **Clean Domain-Driven Design** pattern with clear separation of concerns:

1. **API Layer** (`api/routes/`)
   - RESTful endpoints with FastAPI
   - Request validation with Pydantic
   - Authentication via dependency injection

2. **Domain Layer** (`models/domain/`)
   - Business logic and rules
   - Operation classes for each entity
   - Domain-specific validations

3. **Data Layer** (`models/database/`)
   - SQLModel ORM models
   - Multi-schema architecture (public, vault)
   - Relationship definitions

4. **Service Layer** (`services/`)
   - Workflow orchestration
   - External API integrations
   - Background task processing

### Frontend Architecture

The frontend uses **Next.js App Router** with a component-based architecture:

1. **App Router Structure**
   - File-based routing with layouts
   - Server and client components
   - Protected route handling

2. **State Management**
   - Context API for feature-specific state
   - Zustand for global application state
   - Optimistic updates for better UX

3. **API Integration**
   - Centralized API client with auth
   - Request/response caching
   - Automatic retry with backoff

4. **Component Design**
   - Compound components pattern
   - Radix UI for accessibility
   - Tailwind CSS for styling

## 🔐 Security

- **Authentication**: JWT-based with Supabase Auth
- **Authorization**: Role-based access control (RBAC)
- **Database**: Row-level security with PostgreSQL
- **API Security**: CORS, rate limiting, input validation
- **Environment**: Secure credential management

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL (via Supabase)
- Supabase account and project

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Configure your environment variables
alembic upgrade head  # Run database migrations
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
cp .env.local.example .env.local  # Configure your environment variables
npm run dev
```

### Environment Variables

#### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@host:port/database
SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-key
OPENAI_API_KEY=your-openai-key
PERPLEXITY_API_KEY=your-perplexity-key
JWT_SECRET_KEY=your-jwt-secret
```

#### Frontend (.env.local)
```env
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📊 Database Schema

The application uses a multi-schema PostgreSQL database:

### Public Schema
- User management and authentication
- Enterprise/organization data
- Research searches and messages
- Shared enumerations

### Vault Schema
- Virtual paralegal configurations
- Abilities and behaviors
- Long-term memory storage
- User-specific data

### Key Relationships
- User ↔ Enterprise (many-to-one)
- User ↔ VirtualParalegal (one-to-many)
- VirtualParalegal ↔ Abilities (many-to-many)
- Search ↔ SearchMessage (one-to-many)

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
pytest --cov=.  # With coverage
```

### Frontend Tests
```bash
cd frontend
npm run test
npm run test:coverage
```

## 🚢 Deployment

### Backend Deployment (AWS EB)
```bash
cd backend
eb init -p python-3.11 legalvault-backend
eb create legalvault-backend-env
eb deploy
```

### Frontend Deployment (Vercel)
```bash
cd frontend
vercel
```

## 📝 API Documentation

When running locally, API documentation is available at:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is proprietary software. All rights reserved.

## 👥 Team

- **Development**: Crimson Sun Team
- **Product**: LegalVault Product Team
- **Design**: LegalVault Design Team

## 📞 Support

For support, email support@legalvault.ai or visit our [documentation](https://docs.legalvault.ai).

---

**Note**: This is a beta version. Features marked as "Coming Soon" are under active development and will be released in upcoming versions.
# Architecture Overview – LegalVault Beta

## 📌 Overview  
LegalVault is designed to serve as an **intelligent legal workstation**—an “AI Bloomberg Terminal for Lawyers.” In LegalVault Beta, each user is paired with their own AI-powered **Virtual Paralegal (VP)**, which acts as an intelligent assistant, capable of contextual support across legal tasks and workflows.

---

## 🧠 Virtual Paralegal Architecture

Each Virtual Paralegal (VP) has:
- A name, profile picture, email address, and WhatsApp/phone number.
- Defined **Abilities**, **Behaviours**, **Long-Term Memory**, and **Short-Term Memory**.

### Abilities
Abilities represent the **functional capabilities** of each VP. Examples:
- Summarizing emails.
- Extracting tasks and populating to-do lists.

Abilities are structured as a **tech tree**, similar to strategy games—indicating current and future capabilities. Each `SpecificAbility` is a class/model with:
- Sub-functions (e.g., `GET_TASK`, `READ_EMAIL`).
- A coded `AbilityOperator` that interprets user input using LLMs and executes the appropriate workflow.

### Behaviours
Behaviours control *how* abilities are executed. Some are hardcoded; others are user-customizable.
Examples include:
- Formal vs informal communication tone.
- Preferred summary style (bullet points vs long-form).

### Long-Term Memory
A structured multi-class architecture including:
1. **Self-Identity**: Traits, capabilities, specializations, working preferences.
2. **Global/System Knowledge**: Organization-wide awareness, domain knowledge.
3. **Educational/Training Memory**: Legal handbooks, best practices.
4. **Conversational History**: Relationship context and communication patterns.
5. **Task History**: Past actions, workflows, and performance insights.
6. **Project-Specific Memory**: Client/project-specific data and documents.

### Short-Term Memory
Handled via **Redis** for maintaining contextual awareness across conversations and threads—e.g., current actions, recent messages.

---

## 🗂 Core Application Modules

### 1. Workspace
The main interface for Projects and Client profiles. Projects are a composite of various data classes:
- `Notebook`: Notes from user or VP  
- `Reminders`, `Tasks`: To-do management  
- `Clients` & `Contacts`: Core relational entities  

### 2. Library
A searchable knowledge repository comprising synchronized and user-generated knowledge content across the system.

### 3. Research
A lightweight legal research assistant (powered by Perplexity’s Sonar API), designed to replace traditional Google searches for legal professionals. Features include:
- Querying legal precedents, case law, market intel
- Condensing & sharing results
- Bookmarking and integrating research into Projects

---

## 🏗 Multi-Tenant Database Structure

### A. `vault.*` Schema (System-Wide)
Contains platform-level tables such as:
- `Enterprises`, `Users`, `VirtualParalegals`
- `Abilities`, `Behaviours`
- Integration configs and system metadata

### B. `public.*` Schema (Blueprints)
Holds reusable templates for key entity classes:
- `ClientBlueprint`, `ContactBlueprint`, `ProjectBlueprint`
- Inherit from abstract base classes (e.g., `ClientBase`)
- Used for testing and visual reference

### C. `enterprise_<slug>.*` Schemas (Per Enterprise)
Each enterprise has its own schema for data isolation. Concrete implementations of Blueprint classes:
- `Clients`, `Projects`, `Contacts`, `Tasks`, `Notebooks`, `Reminders`

This ensures **data segregation** across tenants while maintaining **structural consistency**.

---

## 🧱 Backend Class & Code Architecture

Follows **domain-driven design** principles, structured into logical layers:

| Layer | Purpose | Example Entities |
|-------|--------|------------------|
| `models/database` | SQLAlchemy table definitions | `Project`, `Client`, `ProjectClient` |
| `models/domain` | Business logic representation | `VirtualParalegal` |
| `models/domain/operations` | Complex queries and rules | `TaskOperations` |
| `models/schemas` | Pydantic validation models | `ProjectSchema`, `ClientSchema` |
| `models/enums` | Enum definitions | `TaskStatus`, `RoleType` |
| `models/dtos` | Middleware between domain/API | `TaskDTO`, `ProjectDTO` |

### Services:
- `services/executor`: AI-powered feature workflows (e.g., `TaskManagementExecutor`)
- `services/initializer`: Set up initial configs (e.g., `AbilityInitializer`)
- `services/workflow`: Multi-step orchestration (e.g., `EmailWorkflow`)
- `scripts/initializer`: Data seeding/setup

### API Routes:
- FastAPI endpoints located in `api/routes`

#### Example Entity Needs:
| Entity Type | Required Layers |
|-------------|------------------|
| `ProjectClient` (simple) | DB, Schema, Operations, Routes |
| `Client`, `Project` (basic) | All above + Domain |
| `VirtualParalegal`, `Ability` (complex/AI) | All layers |
| `TaskManagement` (system feature) | Most layers, minimal scripts |

---

## 🔗 Frontend–Backend Integration

- **Frontend** (Next.js):
  - React Components trigger API calls (e.g., `ResearchPage`)
  - Custom Hooks manage local state (e.g., `useResearch`)
  - API services handle HTTP requests (`research-api.ts`)

- **Backend** (FastAPI):
  - Routes (e.g., `GET /api/research/sessions`) handle requests
  - Pydantic schemas for validation
  - Business logic in Domain Operations
  - Data persisted via SQLAlchemy in Supabase

This architecture ensures **modular**, **scalable**, and **maintainable** development.

---

## ⚙ Tech Stack Summary

### Frontend
- **Framework**: Next.js (React)
- **Language**: TypeScript
- **UI Components**: Tremor UI
- **Styling**: Tailwind CSS
- **State/Data Management**: Supabase client

### Backend
- **Framework**: FastAPI
- **AI Services**: LangChain, HuggingFace
- **Workflow Management**: Custom Executors/Workflows

### Data Layer
- **Database**: Supabase (PostgreSQL)
- **Auth**: Supabase Auth
- **Vector DB (future)**: Pinecone
- **Memory Stores**: Redis (STM), MongoDB (conversation history)

### Infrastructure
- **Backend Hosting**: Fly.io → AWS EB (planned)
- **Frontend Hosting**: Vercel
- **AI Orchestration**: LangChain, LlamaIndex

### Development Tools
- Type Safety: TypeScript, Pydantic
- DB Management: Alembic Migrations
- Logging, error handling, caching utilities

---
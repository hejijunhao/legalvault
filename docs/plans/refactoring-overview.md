# LegalVault Refactoring Proposals

## Overview

This document summarizes opportunities to simplify the LegalVault codebase without losing functionality. The goal is to reduce complexity, eliminate duplication, and make the code more maintainable.

**Current State:**
- Backend: ~26,870 lines across 330 Python files
- Frontend: ~15,000 lines across 150+ TypeScript files
- Estimated boilerplate: 60-65%

**Target State:**
- Backend: ~9,200 lines (66% reduction)
- Frontend: ~10,000 lines (33% reduction)
- Value-add code: 70%+

## Priority Matrix

| Priority | Area | Effort | Impact | Files Affected |
|----------|------|--------|--------|----------------|
| **P0** | Security: Next.js upgrade | Done | Critical | 1 |
| **P1** | Backend: Permission consolidation | Low | High | 16 → 1 |
| **P1** | Frontend: Delete empty hooks | Low | Medium | 5 |
| **P2** | Backend: Generic executor base | Medium | High | 10+ executors |
| **P2** | Frontend: Animation presets | Low | Medium | 40 components |
| **P3** | Backend: Collapse model layers | High | Very High | 150+ files |
| **P3** | Frontend: Auth consolidation | Medium | High | 3 → 1 |
| **P4** | Backend: Workflow layer review | High | Medium | 50 files |
| **P4** | Frontend: Split ResearchContext | Medium | Medium | 1 → 3 |

## Quick Wins (Week 1)

### Backend Quick Wins

1. **Consolidate permission/operation enums** (saves ~700 lines)
   - Replace 16 `operations_*.py` files with single `models/permissions.py`
   - See: [Backend Refactoring - Section 2.1](./refactoring-backend.md#21-consolidated-permission-system)

2. **Remove unused DTO files** (saves ~100 lines)
   - DTOs only used for research module, inconsistently
   - Either extend to all modules or remove entirely

3. **Delete empty domain models** (saves ~200 lines)
   - Several domain models are empty stubs (e.g., `UserManager`)

### Frontend Quick Wins

1. **Delete empty hook files** (5 files)
   - `use-paralegal-profile.ts`, `use-paralegal-abilities.ts`, etc.
   - Currently contain 1 line each

2. **Create animation presets** (saves ~80 lines across 40 components)
   - Extract repeated Framer Motion configs to `lib/animations.ts`

3. **Standardize API error handling** (saves ~60 lines)
   - Replace 3 different error handlers with one `ApiError` class

## Document Index

| Document | Contents |
|----------|----------|
| [refactoring-backend.md](./refactoring-backend.md) | Detailed backend analysis and proposals |
| [refactoring-frontend.md](./refactoring-frontend.md) | Detailed frontend analysis and proposals |

## Implementation Phases

### Phase 1: Foundation (Weeks 1-2)
- All quick wins from above
- Create base abstractions (generic executor, API client)
- Add comprehensive tests for refactored code

### Phase 2: Model Consolidation (Weeks 3-4)
- Merge database + domain models where business logic is minimal
- Consolidate auth implementations (frontend)
- Create unified type definitions

### Phase 3: Service Layer (Weeks 5-6)
- Evaluate workflow layer necessity
- Implement generic CRUD patterns
- Split ResearchContext (frontend)

### Phase 4: Polish (Week 7)
- Update documentation
- Remove deprecated code paths
- Performance testing

## Guiding Principles

1. **Single Source of Truth** - Each concept defined once
2. **Eliminate Translation Layers** - Reduce model conversions
3. **Favor Composition** - Generic base classes with thin subclasses
4. **Test First** - Write tests before refactoring
5. **Incremental** - Small, verifiable changes

## Risk Mitigation

- Feature branches for each phase
- Comprehensive test coverage before changes
- Run existing tests after each change
- Review sessions for major refactors

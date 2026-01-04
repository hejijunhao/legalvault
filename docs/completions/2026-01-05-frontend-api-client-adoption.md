# Frontend API Client Adoption - P2 Completion

**Date:** 2026-01-05
**Status:** Completed
**Priority:** P2

## Summary

Updated the research API service layer to use the centralized `apiClient` from `@/lib/api-client.ts` instead of duplicated fetch utilities. This eliminates code duplication and provides consistent error handling across all API calls.

## Before

**Duplicated patterns across API files:**

```typescript
// Old pattern (repeated in every function)
const headers = await getAuthHeader();
const response = await withRetry(() => fetchWithSelfSignedCert(url, {
  method: 'POST',
  headers,
  body: JSON.stringify(data)
}));
if (!response.ok) return handleApiError(response);
const result = await response.json();
```

**Files with duplicated logic:**
- `research-api-core.ts` - 241 lines of utility functions
- `research-api-sessions.ts` - 227 lines with verbose fetch patterns
- `research-api-messages.ts` - 161 lines with verbose fetch patterns

## After

**Clean pattern using apiClient:**

```typescript
// New pattern (single line)
const data = await apiClient.post<ResearchSession>('/api/research/searches', {
  query,
  search_params: searchParams
});
```

**Updated files:**
- `research-api-sessions.ts` - 153 lines (33% reduction)
- `research-api-messages.ts` - 121 lines (25% reduction)
- `research-api-core.ts` - 178 lines (deprecated, kept for backwards compatibility)

## Changes Made

### Files Modified (4)

| File | Before | After | Change |
|------|--------|-------|--------|
| `research-api-sessions.ts` | 227 lines | 153 lines | -33% |
| `research-api-messages.ts` | 161 lines | 121 lines | -25% |
| `research-api-core.ts` | 241 lines | 178 lines | -26% (deprecated) |
| `research-api-types.ts` | 34 lines | 29 lines | Re-export ApiError |
| `research-api.ts` | 69 lines | 98 lines | Added proper types |

### Key Improvements

1. **Removed duplicated fetch logic** - All API calls now use `apiClient.get()`, `apiClient.post()`, `apiClient.patch()`, `apiClient.delete()`

2. **Removed duplicated auth handling** - `apiClient` handles authentication automatically via Supabase session

3. **Removed duplicated retry logic** - `apiClient` has built-in exponential backoff retry

4. **Removed duplicated error handling** - `apiClient` throws `ApiError` with proper status codes

5. **Deprecated legacy utilities** - Old functions marked with `@deprecated` for backwards compatibility

## API Comparison

| Function | Old Implementation | New Implementation |
|----------|-------------------|-------------------|
| `fetchSessions()` | 22 lines | 14 lines |
| `fetchSession()` | 17 lines | 10 lines |
| `createNewSession()` | 23 lines | 12 lines |
| `sendSessionMessage()` | 25 lines | 12 lines |
| `updateSessionMetadata()` | 19 lines | 12 lines |
| `deleteSession()` | 15 lines | 7 lines |

## Usage

```typescript
// Before
import { getAuthHeader, fetchWithSelfSignedCert, withRetry, handleApiError } from './research-api-core';

const headers = await getAuthHeader();
const response = await withRetry(() =>
  fetchWithSelfSignedCert('/api/research/searches', { headers })
);
if (!response.ok) return handleApiError(response);
const data = await response.json();

// After
import { apiClient } from '@/lib/api-client';

const data = await apiClient.get<SearchListResponse>('/api/research/searches', {
  limit: 10,
  offset: 0
});
```

## Backwards Compatibility

- Legacy functions in `research-api-core.ts` are preserved but marked `@deprecated`
- `ApiError` is re-exported from central location for existing imports
- All public API function signatures remain unchanged

## Verification

```bash
npx tsc --noEmit  # TypeScript compilation passes
```

## Impact

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Total lines (API files) | 629 | 481 | -24% |
| Duplicated fetch patterns | 12 | 0 | -100% |
| Error handling locations | 12 | 1 | -92% |

## Migration Notes

- Existing code importing from `research-api` continues to work
- New code should use `apiClient` from `@/lib/api-client` directly for non-research APIs
- Legacy core utilities can be removed in a future cleanup when all services are migrated

## Next Steps

1. **Migrate other services** (user-api, paralegal-api) to use `apiClient`
2. **Remove deprecated functions** after migration is complete
3. **Add unit tests** for apiClient error handling

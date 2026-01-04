# Frontend Refactoring Proposals

## Executive Summary

The frontend is well-structured with good separation of concerns, but has consolidation opportunities across components, state management, and API integration.

**Key Findings:**
- 3 separate auth implementations (Context, Manager, Service)
- ResearchContext is a 523-line mega-context managing too much state
- 40 components duplicate Framer Motion animation configs
- Empty hook files and duplicated block components
- Types duplicated between context and services

**Estimated Reduction:** 400-500 lines without losing functionality

---

## 1. Component Consolidation

### 1.1 Block Components Duplication

**Current State:**
```
components/library/blocks/
├── librarian-block.tsx (267 lines)
├── highlights-block.tsx (149 lines)
└── collapsible-block.tsx (148 lines)

Total: 564 lines
```

All follow the same pattern:
```typescript
const [isExpanded, setIsExpanded] = useState(false)
<Card onClick={() => setIsExpanded(!isExpanded)}>
  <motion.div>...</motion.div>
</Card>
```

**Proposal: Generic ExpandableBlock**

```typescript
// components/library/blocks/expandable-block.tsx
import { useState, ReactNode } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Card } from '@/components/ui/card'
import { ChevronDown, ChevronUp } from 'lucide-react'

interface ExpandableBlockProps {
  title: string
  subtitle?: string
  icon?: ReactNode
  badge?: string | number
  children: ReactNode
  expandedContent?: ReactNode
  defaultExpanded?: boolean
  onViewAll?: () => void
  variant?: 'default' | 'compact' | 'featured'
}

export function ExpandableBlock({
  title,
  subtitle,
  icon,
  badge,
  children,
  expandedContent,
  defaultExpanded = false,
  onViewAll,
  variant = 'default',
}: ExpandableBlockProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded)

  return (
    <Card
      className={cn(
        "cursor-pointer transition-shadow hover:shadow-md",
        variant === 'featured' && "border-primary",
        variant === 'compact' && "p-3"
      )}
      onClick={() => setIsExpanded(!isExpanded)}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4">
        <div className="flex items-center gap-3">
          {icon}
          <div>
            <h3 className="font-medium">{title}</h3>
            {subtitle && <p className="text-sm text-muted-foreground">{subtitle}</p>}
          </div>
        </div>
        <div className="flex items-center gap-2">
          {badge && (
            <span className="px-2 py-1 text-xs bg-muted rounded-full">{badge}</span>
          )}
          {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </div>
      </div>

      {/* Always visible content */}
      <div className="px-4 pb-4">{children}</div>

      {/* Expandable content */}
      <AnimatePresence>
        {isExpanded && expandedContent && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4 border-t pt-4">{expandedContent}</div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* View All button */}
      {onViewAll && (
        <button
          onClick={(e) => {
            e.stopPropagation()
            onViewAll()
          }}
          className="w-full p-2 text-sm text-primary hover:bg-muted transition-colors"
        >
          View All
        </button>
      )}
    </Card>
  )
}
```

**Usage:**
```typescript
// Replace librarian-block.tsx
<ExpandableBlock
  title="Librarian"
  subtitle="Your document assistant"
  icon={<BookOpen className="h-5 w-5" />}
  badge={unreadCount}
  variant="featured"
  onViewAll={() => router.push('/library/librarian')}
>
  <LibrarianPreview items={recentItems.slice(0, 3)} />
</ExpandableBlock>
```

**Reduction:** 564 lines → ~200 lines (65% reduction)

---

### 1.2 Animation Presets

**Current State:** 40 components with inline Framer Motion configs

```typescript
// Repeated across 40+ files
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.5 }}
>
```

**Proposal: Centralized Animation Library**

```typescript
// lib/animations.ts
import { Variants } from 'framer-motion'

// Motion presets (for spread syntax)
export const motion = {
  fadeIn: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
    transition: { duration: 0.2 },
  },
  fadeInUp: {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: 20 },
    transition: { duration: 0.3 },
  },
  fadeInDown: {
    initial: { opacity: 0, y: -20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 },
    transition: { duration: 0.3 },
  },
  slideInRight: {
    initial: { opacity: 0, x: 20 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: 20 },
    transition: { duration: 0.3 },
  },
  slideInLeft: {
    initial: { opacity: 0, x: -20 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -20 },
    transition: { duration: 0.3 },
  },
  scaleIn: {
    initial: { opacity: 0, scale: 0.95 },
    animate: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 0.95 },
    transition: { duration: 0.2 },
  },
  expand: {
    initial: { height: 0, opacity: 0 },
    animate: { height: 'auto', opacity: 1 },
    exit: { height: 0, opacity: 0 },
    transition: { duration: 0.2 },
  },
} as const

// Variants for complex animations
export const listVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
    },
  },
}

export const listItemVariants: Variants = {
  hidden: { opacity: 0, y: 10 },
  visible: { opacity: 1, y: 0 },
}

// Stagger delays
export const stagger = {
  fast: 0.05,
  normal: 0.1,
  slow: 0.15,
}
```

**Usage:**
```typescript
import { motion as motionPresets } from '@/lib/animations'

// Before
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.5 }}
>

// After
<motion.div {...motionPresets.fadeInUp}>
```

**Reduction:** ~80 lines across 40 components

---

### 1.3 Tab Components

**Current State:** Custom tab logic in research-tabs.tsx (129 lines) and project-tabs.tsx (112 lines)

**Proposal:** Use Radix Tabs directly with styling wrapper

```typescript
// components/ui/styled-tabs.tsx
import * as TabsPrimitive from '@radix-ui/react-tabs'
import { cn } from '@/lib/utils'

export const Tabs = TabsPrimitive.Root

export const TabsList = React.forwardRef<
  React.ElementRef<typeof TabsPrimitive.List>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitive.List> & {
    variant?: 'default' | 'pills' | 'underline'
  }
>(({ className, variant = 'default', ...props }, ref) => (
  <TabsPrimitive.List
    ref={ref}
    className={cn(
      "flex gap-1",
      variant === 'default' && "bg-muted p-1 rounded-lg",
      variant === 'pills' && "gap-2",
      variant === 'underline' && "border-b gap-4",
      className
    )}
    {...props}
  />
))

// ... TabsTrigger, TabsContent with variants
```

**Reduction:** 241 lines → ~100 lines (60% reduction)

---

## 2. State Management Consolidation

### 2.1 Auth Implementation Merge

**Current State:** 3 separate auth implementations

```
contexts/auth/auth-context.tsx (183 lines) - React Context
lib/auth-manager.ts (~80 lines) - Event-based manager
services/user/user-api.ts (partial) - API with auth checks
```

**Proposal: Single Zustand Auth Store**

```typescript
// lib/stores/auth-store.ts
import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import { createClient } from '@/lib/supabase/client'
import type { User, Session } from '@supabase/supabase-js'

interface AuthState {
  user: User | null
  session: Session | null
  isLoading: boolean
  isAuthenticated: boolean

  // Actions
  initialize: () => Promise<void>
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  refreshSession: () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      session: null,
      isLoading: true,
      isAuthenticated: false,

      initialize: async () => {
        const supabase = createClient()
        const { data: { session } } = await supabase.auth.getSession()

        if (session) {
          set({
            user: session.user,
            session,
            isAuthenticated: true,
            isLoading: false,
          })
        } else {
          set({ isLoading: false })
        }

        // Listen for auth changes
        supabase.auth.onAuthStateChange((_event, session) => {
          set({
            user: session?.user ?? null,
            session,
            isAuthenticated: !!session,
          })
        })
      },

      login: async (email, password) => {
        set({ isLoading: true })
        const supabase = createClient()
        const { data, error } = await supabase.auth.signInWithPassword({
          email,
          password,
        })

        if (error) {
          set({ isLoading: false })
          throw error
        }

        set({
          user: data.user,
          session: data.session,
          isAuthenticated: true,
          isLoading: false,
        })
      },

      logout: async () => {
        const supabase = createClient()
        await supabase.auth.signOut()
        set({
          user: null,
          session: null,
          isAuthenticated: false,
        })
      },

      refreshSession: async () => {
        const supabase = createClient()
        const { data: { session } } = await supabase.auth.refreshSession()
        if (session) {
          set({ session, user: session.user })
        }
      },
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        user: state.user,
        session: state.session,
      }),
    }
  )
)

// Hook for easy usage
export function useAuth() {
  const store = useAuthStore()
  return {
    user: store.user,
    isLoading: store.isLoading,
    isAuthenticated: store.isAuthenticated,
    login: store.login,
    logout: store.logout,
  }
}
```

**Migration:**
1. Create auth-store.ts
2. Update ProtectedRoute to use `useAuthStore`
3. Update all components using `useAuth()`
4. Remove auth-context.tsx and auth-manager.ts

**Reduction:** 263 lines → ~120 lines (54% reduction)

---

### 2.2 Split ResearchContext

**Current State:** Single 523-line context managing:
- Session CRUD
- Message polling
- Cache management
- Loading states (6 different ones)
- Error handling

**Proposal: Split into focused stores**

```typescript
// lib/stores/research/sessions-store.ts (~150 lines)
interface SessionsState {
  sessions: ResearchSession[]
  currentSessionId: string | null
  isLoading: boolean

  fetchSessions: () => Promise<void>
  createSession: (query: string) => Promise<string>
  selectSession: (id: string) => void
  deleteSession: (id: string) => Promise<void>
}

// lib/stores/research/messages-store.ts (~120 lines)
interface MessagesState {
  messages: Record<string, Message[]>  // sessionId -> messages
  isSending: boolean
  isPolling: boolean

  fetchMessages: (sessionId: string) => Promise<void>
  sendMessage: (sessionId: string, content: string) => Promise<void>
  startPolling: (sessionId: string) => void
  stopPolling: () => void
}

// lib/stores/research/index.ts - Combined hook
export function useResearch() {
  const sessions = useSessionsStore()
  const messages = useMessagesStore()

  return {
    // Sessions
    sessions: sessions.sessions,
    currentSession: sessions.sessions.find(s => s.id === sessions.currentSessionId),
    createSession: sessions.createSession,
    selectSession: sessions.selectSession,

    // Messages
    messages: messages.messages[sessions.currentSessionId] ?? [],
    sendMessage: (content: string) =>
      messages.sendMessage(sessions.currentSessionId!, content),
    isSending: messages.isSending,
  }
}
```

**Benefits:**
- Smaller, focused state updates
- Better performance (fewer re-renders)
- Easier to test individual stores
- Clearer separation of concerns

**Reduction:** 523 lines → ~350 lines (33% reduction) + better performance

---

## 3. API Layer Consolidation

### 3.1 Centralized API Client

**Current State:** 6 research API files with duplicated utilities

**Proposal: Factory-based API client**

```typescript
// lib/api-client.ts
import { createClient } from '@/lib/supabase/client'

export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'
  body?: unknown
  params?: Record<string, string>
  headers?: Record<string, string>
  retry?: number
  timeout?: number
}

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  private async getAuthHeaders(): Promise<Record<string, string>> {
    const supabase = createClient()
    const { data: { session } } = await supabase.auth.getSession()

    if (!session?.access_token) {
      throw new ApiError(401, 'UNAUTHORIZED', 'No valid session')
    }

    return {
      'Authorization': `Bearer ${session.access_token}`,
      'Content-Type': 'application/json',
    }
  }

  async request<T>(
    endpoint: string,
    options: RequestOptions = {}
  ): Promise<T> {
    const {
      method = 'GET',
      body,
      params,
      headers = {},
      retry = 3,
      timeout = 30000,
    } = options

    const url = new URL(endpoint, this.baseUrl)
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        url.searchParams.set(key, value)
      })
    }

    const authHeaders = await this.getAuthHeaders()

    for (let attempt = 0; attempt < retry; attempt++) {
      try {
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), timeout)

        const response = await fetch(url.toString(), {
          method,
          headers: { ...authHeaders, ...headers },
          body: body ? JSON.stringify(body) : undefined,
          signal: controller.signal,
        })

        clearTimeout(timeoutId)

        if (!response.ok) {
          const error = await response.json().catch(() => ({}))
          throw new ApiError(
            response.status,
            error.code ?? 'API_ERROR',
            error.detail ?? response.statusText
          )
        }

        return await response.json()
      } catch (error) {
        if (attempt === retry - 1) throw error
        await new Promise(r => setTimeout(r, Math.pow(2, attempt) * 1000))
      }
    }

    throw new ApiError(500, 'RETRY_EXHAUSTED', 'Request failed after retries')
  }

  // Convenience methods
  get<T>(endpoint: string, params?: Record<string, string>) {
    return this.request<T>(endpoint, { params })
  }

  post<T>(endpoint: string, body: unknown) {
    return this.request<T>(endpoint, { method: 'POST', body })
  }

  put<T>(endpoint: string, body: unknown) {
    return this.request<T>(endpoint, { method: 'PUT', body })
  }

  delete<T>(endpoint: string) {
    return this.request<T>(endpoint, { method: 'DELETE' })
  }
}

// Singleton instance
let client: ApiClient | null = null

export function getApiClient(): ApiClient {
  if (!client) {
    client = new ApiClient(process.env.NEXT_PUBLIC_API_URL!)
  }
  return client
}
```

**Usage:**
```typescript
// services/research-service.ts
import { getApiClient } from '@/lib/api-client'
import type { ResearchSession, Message } from '@/types/research'

const api = getApiClient()

export const researchService = {
  async getSessions(): Promise<ResearchSession[]> {
    return api.get('/api/research/searches')
  },

  async createSession(query: string): Promise<ResearchSession> {
    return api.post('/api/research/searches', { query })
  },

  async getMessages(sessionId: string): Promise<Message[]> {
    return api.get(`/api/research/searches/${sessionId}/messages`)
  },

  async sendMessage(sessionId: string, content: string): Promise<Message> {
    return api.post(`/api/research/searches/${sessionId}/continue`, {
      follow_up_query: content,
    })
  },
}
```

**Reduction:** Consolidates 6 files (~600 lines) → 2 files (~200 lines)

---

## 4. Type Consolidation

### 4.1 Single Source for Research Types

**Current State:** Types duplicated in context and services

**Proposal: Centralized type definitions**

```typescript
// types/research.ts - SINGLE SOURCE
export enum QueryCategory {
  CLEAR = 'clear',
  UNCLEAR = 'unclear',
  IRRELEVANT = 'irrelevant',
  BORDERLINE = 'borderline',
}

export enum QueryStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export enum QueryType {
  COURT_CASE = 'court_case',
  LEGISLATIVE = 'legislative',
  COMMERCIAL = 'commercial',
  GENERAL = 'general',
}

export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: MessageContent
  sequence: number
  status: QueryStatus
  created_at: string
}

export interface MessageContent {
  text: string
  citations?: Citation[]
  metadata?: Record<string, unknown>
}

export interface Citation {
  text: string
  url: string
}

export interface ResearchSession {
  id: string
  title: string
  query: string
  status: QueryStatus
  category: QueryCategory
  type: QueryType
  messages: Message[]
  created_at: string
  updated_at: string
}

// API request/response types
export interface CreateSessionRequest {
  query: string
  search_params?: Record<string, unknown>
}

export interface SendMessageRequest {
  follow_up_query: string
}
```

**Import everywhere from `@/types/research`**

---

## 5. Cleanup Tasks

### 5.1 Delete Empty Hooks

```
hooks/paralegal/use-paralegal-profile.ts (empty)
hooks/paralegal/use-paralegal-abilities.ts (empty)
hooks/paralegal/use-paralegal-behaviors.ts (empty)
hooks/paralegal/use-paralegal-knowledge.ts (empty)
```

### 5.2 Remove Deprecated Patterns

- Remove `use-supabase-test.ts` (test utility)
- Consolidate paralegal hooks into single `use-paralegal.ts`

### 5.3 Coming Soon Component

Replace multiple "coming soon" placeholders with single reusable component:

```typescript
// components/coming-soon.tsx
interface ComingSoonProps {
  title: string
  description?: string
  features?: string[]
  expectedDate?: string
}

export function ComingSoon({
  title,
  description = "We're working hard to bring you this feature.",
  features,
  expectedDate,
}: ComingSoonProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] p-8 text-center">
      <Construction className="h-16 w-16 text-muted-foreground mb-4" />
      <h2 className="text-2xl font-semibold mb-2">{title}</h2>
      <p className="text-muted-foreground mb-4 max-w-md">{description}</p>

      {features && (
        <ul className="text-left space-y-2 mb-4">
          {features.map((feature) => (
            <li key={feature} className="flex items-center gap-2">
              <Check className="h-4 w-4 text-primary" />
              <span className="text-sm">{feature}</span>
            </li>
          ))}
        </ul>
      )}

      {expectedDate && (
        <p className="text-xs text-muted-foreground">
          Expected: {expectedDate}
        </p>
      )}
    </div>
  )
}
```

---

## 6. Summary

| Area | Current | Proposed | Reduction |
|------|---------|----------|-----------|
| Block components | 564 lines | 200 lines | 65% |
| Auth state | 263 lines | 120 lines | 54% |
| ResearchContext | 523 lines | 350 lines | 33% |
| API layer | 600 lines | 200 lines | 67% |
| Tab components | 241 lines | 100 lines | 59% |
| Animation duplication | 80 lines | 20 lines | 75% |
| Empty hooks | 4 files | 0 files | 100% |
| **Estimated Total** | | | **~500 lines** |

## 7. Migration Order

1. **Week 1: Quick Wins**
   - Delete empty hooks
   - Create animation presets
   - Create ApiError class

2. **Week 2: State Management**
   - Implement auth-store.ts
   - Migrate auth usage
   - Remove old auth files

3. **Week 3: Components**
   - Create ExpandableBlock
   - Migrate block components
   - Create styled-tabs

4. **Week 4: Research Refactor**
   - Split ResearchContext into stores
   - Create unified API client
   - Consolidate types

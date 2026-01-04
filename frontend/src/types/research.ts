// src/types/research.ts
// Consolidated research types - single source of truth

// Enums matching backend
export enum QueryCategory {
  CLEAR = "clear",
  UNCLEAR = "unclear",
  IRRELEVANT = "irrelevant",
  BORDERLINE = "borderline",
}

export enum QueryType {
  COURT_CASE = "court_case",
  LEGISLATIVE = "legislative",
  COMMERCIAL = "commercial",
  GENERAL = "general",
}

export enum QueryStatus {
  PENDING = "pending",
  COMPLETED = "completed",
  FAILED = "failed",
  NEEDS_CLARIFICATION = "needs_clarification",
  IRRELEVANT = "irrelevant_query",
}

// Domain types
export interface Citation {
  text: string
  url: string
  metadata?: Record<string, unknown>
}

export interface MessageContent {
  text: string
  citations?: Citation[]
  thread_id?: string
  token_usage?: number
  metadata?: Record<string, unknown>
}

export interface Message {
  id: string
  role: "user" | "assistant" | "system"
  content: MessageContent
  search_id?: string
  sequence: number
  status?: QueryStatus
  created_at?: string
  updated_at?: string
}

export interface SearchParams {
  temperature?: number
  max_tokens?: number
  top_p?: number
  top_k?: number
  jurisdiction?: string
  type?: QueryType
}

export interface ResearchSession {
  id: string
  title: string
  query: string
  description?: string
  is_featured: boolean
  tags?: string[]
  search_params?: SearchParams
  messages?: Message[]
  created_at: string
  updated_at: string
  status: QueryStatus
  category?: QueryCategory
  query_type?: QueryType
  user_id: string
  enterprise_id?: string
}

// API response types
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  offset: number
  limit: number
}

export type SearchListResponse = PaginatedResponse<ResearchSession>
export type MessageListResponse = PaginatedResponse<Message>

// API request types
export interface CreateSessionRequest {
  query: string
  search_params?: SearchParams
}

export interface SendMessageRequest {
  follow_up_query: string
  thread_id?: string
  previous_messages?: Array<{ role: string; content: string }>
}

export interface UpdateSessionRequest {
  title?: string
  description?: string
  tags?: string[]
  is_featured?: boolean
}

// Cache types
export interface CacheConfig {
  ttl: number
  storageKey: string
  sanitizeBeforeStorage: boolean
  sensitiveFields: string[]
}

export interface CacheEntry<T> {
  data: T
  timestamp: number
  key: string
}

export interface CacheStorage {
  sessions: Record<string, CacheEntry<ResearchSession>>
  sessionLists: Record<string, CacheEntry<SearchListResponse>>
  messages: Record<string, CacheEntry<Message>>
  messageLists: Record<string, CacheEntry<MessageListResponse>>
}

// WebSocket types
export interface WebSocketMessage {
  type: string
  data?: Record<string, unknown>
  message?: string
  search_id?: string
  status?: string
  subscribed_to?: string[]
}

export interface WebSocketConnection {
  disconnect: () => void
  send: (data: Record<string, unknown>) => void
  isConnected: boolean
}

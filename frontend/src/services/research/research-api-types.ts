// src/services/research/research-api-types.ts
// Re-exports from centralized types for backwards compatibility

export {
  QueryCategory,
  QueryStatus,
  QueryType,
  type Citation,
  type Message,
  type MessageContent,
  type SearchParams,
  type ResearchSession,
  type SearchListResponse,
  type MessageListResponse,
  type PaginatedResponse,
  type CacheConfig,
  type CacheEntry,
  type CacheStorage,
  type WebSocketMessage,
  type WebSocketConnection,
  type CreateSessionRequest,
  type SendMessageRequest,
  type UpdateSessionRequest,
} from "@/types/research"

// Legacy ApiError interface - use ApiError from @/lib/api-client instead
export interface ApiError extends Error {
  status?: number
  statusText?: string
  code?: string
  details?: string
  originalError?: Error | unknown
}

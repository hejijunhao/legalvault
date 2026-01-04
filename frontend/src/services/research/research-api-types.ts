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

// ApiError is now exported from @/lib/api-client
// Re-export for backwards compatibility
export { ApiError } from '@/lib/api-client'

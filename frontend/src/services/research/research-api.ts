// src/services/research/research-api.ts
// Main export file for research API

// Re-export types
export * from './research-api-types'

// Re-export ApiError from centralized location
export { ApiError } from '@/lib/api-client'

// Re-export legacy core functionality (deprecated - use @/lib/api-client directly)
export {
  getApiBaseUrl,
  getAuthHeader,
  fetchWithSelfSignedCert,
  withRetry,
  formatApiError,
  handleApiError,
  scheduleCacheClear
} from './research-api-core'

// Re-export session-related functions
export {
  fetchSessions,
  fetchSession,
  createNewSession,
  sendSessionMessage,
  continueSession,
  updateSessionMetadata,
  deleteSession
} from './research-api-sessions'

// Re-export message-related functions
export {
  fetchMessage,
  createMessage,
  fetchMessagesForSearch,
  updateMessage,
  deleteMessage
} from './research-api-messages'

// Export cache interface
import { researchCache } from './research-cache'
import type { ResearchSession, Message, CacheEntry } from './research-api-types'

type SessionListOptions = {
  featuredOnly?: boolean
  status?: string
  limit?: number
  offset?: number
} | null | undefined

type MessageListOptions = {
  limit?: number
  offset?: number
} | null | undefined

export const cache = {
  clear: () => researchCache.clear(),
  invalidateSearch: (searchId: string) => researchCache.invalidateSearch(searchId),
  invalidateMessageList: (searchId: string) => researchCache.invalidateMessageList(searchId),
  getSession: async (sessionId: string) => researchCache.getSession(sessionId),
  getMessage: (messageId: string) => researchCache.getMessage(messageId),
  getSessionList: (options?: SessionListOptions) => researchCache.getSessionList(options),
  getMessageList: async (searchId: string, options?: MessageListOptions) =>
    researchCache.getMessageList(searchId, options),
  setSession: (session: ResearchSession) => researchCache.setSession(session),
  setMessage: (message: Message) => researchCache.setMessage(message),
  clearSessionListCache: () => researchCache.clearSessionListCache(),
  deleteMessage: (messageId: string) => researchCache.deleteMessage(messageId),
  clearMessageCache: () => researchCache.clearMessageCache(),
  refreshCacheIfNeeded: <T>(
    cacheMap: Map<string, CacheEntry<T>>,
    key: string,
    refreshThreshold: number,
    refreshFn: () => Promise<T>
  ) => researchCache.refreshCacheIfNeeded(cacheMap, key, refreshThreshold, refreshFn),
  config: researchCache.config
}

// Import debug utilities
import {
  logCacheState,
  monitorCacheOperations,
  simulateNetworkLatency,
  restoreOriginalFetch
} from './research-api-debug'

// Only expose debug utilities in development
export const debug =
  process.env.NODE_ENV === 'development'
    ? {
        logCacheState,
        monitorCacheOperations,
        simulateNetworkLatency,
        restoreOriginalFetch
      }
    : undefined

// src/services/research/research-api.ts

// Re-export types
export * from './research-api-types';

// Re-export core functionality
export {
  getApiBaseUrl,
  getAuthHeader,
  fetchWithSelfSignedCert,
  withRetry,
  formatApiError,
  handleApiError,
  scheduleCacheClear
} from './research-api-core';

// Re-export session-related functions
export {
  fetchSessions,
  fetchSession,
  createNewSession,
  sendSessionMessage,
  updateSessionMetadata,
  deleteSession
} from './research-api-sessions';

// Re-export message-related functions
export {
  fetchMessage,
  fetchMessagesForSearch,
  updateMessage,
  deleteMessage,
  forwardMessage
} from './research-api-messages';

// Re-export SSE-related functions
export { connectToSSE } from './research-api-sse';

// Re-export WebSocket-related functions (deprecated)
/** @deprecated Use SSE-based connectToSSE instead */
export const connectToMessageUpdates = (...args: any[]) => {
  console.warn('connectToMessageUpdates is deprecated. Please use connectToSSE instead.');
  const { connectToMessageUpdates: wsConnect } = require('./research-api-websocket');
  return wsConnect(...args);
};

/** @deprecated WebSocket functionality is being removed */
export const requestLatestMessages = (...args: any[]) => {
  console.warn('requestLatestMessages is deprecated. Messages are now automatically streamed via SSE.');
  const { requestLatestMessages: wsRequest } = require('./research-api-websocket');
  return wsRequest(...args);
};

/** @deprecated WebSocket functionality is being removed */
export const sendTypingNotification = (...args: any[]) => {
  console.warn('sendTypingNotification is deprecated and will be removed.');
  const { sendTypingNotification: wsNotify } = require('./research-api-websocket');
  return wsNotify(...args);
};

// Export cache interface
import { researchCache } from './research-cache';
export const cache = {
  clear: () => researchCache.clear(),
  invalidateSearch: (searchId: string) => researchCache.invalidateSearch(searchId),
  invalidateMessageList: (searchId: string) => researchCache.invalidateMessageList(searchId),
  getSession: (sessionId: string) => researchCache.getSession(sessionId),
  getMessage: (messageId: string) => researchCache.getMessage(messageId),
  getSessionList: (options?: any) => researchCache.getSessionList(options),
  getMessageList: (searchId: string, options?: any) => researchCache.getMessageList(searchId, options),
  setSession: (session: any) => researchCache.setSession(session),
  setMessage: (message: any) => researchCache.setMessage(message),
  clearSessionListCache: () => researchCache.clearSessionListCache(),
  deleteMessage: (messageId: string) => researchCache.deleteMessage(messageId),
  clearMessageCache: () => researchCache.clearMessageCache(),
  refreshCacheIfNeeded: <T>(cacheMap: Map<string, any>, key: string, refreshThreshold: number, refreshFn: () => Promise<T>) => 
    researchCache.refreshCacheIfNeeded(cacheMap, key, refreshThreshold, refreshFn),
  config: researchCache.config
};

// Import debug utilities
import {
  logCacheState,
  monitorCacheOperations,
  simulateNetworkLatency,
  restoreOriginalFetch
} from './research-api-debug';

// Only expose debug utilities in development
export const debug = process.env.NODE_ENV === 'development' ? {
  logCacheState,
  monitorCacheOperations,
  simulateNetworkLatency,
  restoreOriginalFetch
} : undefined;
// src/services/research/research-api.ts

import { supabase } from '@/lib/supabase'
import { Message, ResearchSession, SearchParams, QueryStatus, QueryCategory, QueryType, Citation } from '@/contexts/research/research-context'

// Cache configuration
interface CacheConfig {
  ttl: number;  // Time to live in milliseconds
  maxSize?: number; // Maximum number of items to store in memory
  persistToStorage?: boolean; // Whether to persist cache to localStorage
}

interface CacheEntry<T> {
  data: T;
  timestamp: number;
  key: string;
}

// Default cache configuration
const DEFAULT_CACHE_CONFIG: CacheConfig = {
  ttl: 5 * 60 * 1000, // 5 minutes default TTL
  maxSize: 100, // Store up to 100 items in memory
  persistToStorage: true // Persist to localStorage by default
};

// In-memory cache for sessions and messages
class ResearchCache {
  private sessionCache: Map<string, CacheEntry<ResearchSession>> = new Map();
  private sessionListCache: Map<string, CacheEntry<SearchListResponse>> = new Map();
  private messageCache: Map<string, CacheEntry<Message>> = new Map();
  private messageListCache: Map<string, CacheEntry<MessageListResponse>> = new Map();
  public config: CacheConfig;
  
  constructor(config: Partial<CacheConfig> = {}) {
    this.config = { ...DEFAULT_CACHE_CONFIG, ...config };
    this.loadFromStorage();
  }
  
  // Session cache methods
  
  /**
   * Store a session in the cache
   * @param session The session to cache
   */
  setSession(session: ResearchSession): void {
    if (!session?.id) return;
    
    const key = session.id;
    const entry: CacheEntry<ResearchSession> = {
      data: session,
      timestamp: Date.now(),
      key
    };
    
    this.sessionCache.set(key, entry);
    this.saveToStorage();
  }
  
  /**
   * Get a session from the cache if it exists and is not expired
   * @param sessionId The ID of the session to retrieve
   * @returns The cached session or undefined if not found or expired
   */
  getSession(sessionId: string): ResearchSession | undefined {
    if (!sessionId) return undefined;
    
    const entry = this.sessionCache.get(sessionId);
    if (!entry) return undefined;
    
    // Check if the entry is expired
    if (Date.now() - entry.timestamp > this.config.ttl) {
      this.sessionCache.delete(sessionId);
      this.saveToStorage();
      return undefined;
    }
    
    return entry.data;
  }
  
  /**
   * Store a list of sessions in the cache
   * @param options The options used to fetch the sessions
   * @param response The session list response to cache
   */
  setSessionList(options: {
    featuredOnly?: boolean;
    status?: QueryStatus;
    limit?: number;
    offset?: number;
  } | undefined, response: SearchListResponse): void {
    const key = this.generateOptionsKey(options);
    const entry: CacheEntry<SearchListResponse> = {
      data: response,
      timestamp: Date.now(),
      key
    };
    
    this.sessionListCache.set(key, entry);
    
    // Also cache individual sessions
    response.items.forEach(session => {
      this.setSession(session);
    });
    
    this.saveToStorage();
  }
  
  /**
   * Get a list of sessions from the cache if it exists and is not expired
   * @param options The options used to fetch the sessions
   * @returns The cached session list or undefined if not found or expired
   */
  getSessionList(options?: {
    featuredOnly?: boolean;
    status?: QueryStatus;
    limit?: number;
    offset?: number;
  }): SearchListResponse | undefined {
    const key = this.generateOptionsKey(options);
    const entry = this.sessionListCache.get(key);
    if (!entry) return undefined;
    
    // Check if the entry is expired
    if (Date.now() - entry.timestamp > this.config.ttl) {
      this.sessionListCache.delete(key);
      this.saveToStorage();
      return undefined;
    }
    
    return entry.data;
  }
  
  // Message cache methods
  
  /**
   * Store a message in the cache
   * @param message The message to cache
   */
  setMessage(message: Message): void {
    if (!message?.id) return;
    
    const key = message.id;
    const entry: CacheEntry<Message> = {
      data: message,
      timestamp: Date.now(),
      key
    };
    
    this.messageCache.set(key, entry);
    this.saveToStorage();
  }
  
  /**
   * Get a message from the cache if it exists and is not expired
   * @param messageId The ID of the message to retrieve
   * @returns The cached message or undefined if not found or expired
   */
  getMessage(messageId: string): Message | undefined {
    if (!messageId) return undefined;
    
    const entry = this.messageCache.get(messageId);
    if (!entry) return undefined;
    
    // Check if the entry is expired
    if (Date.now() - entry.timestamp > this.config.ttl) {
      this.messageCache.delete(messageId);
      this.saveToStorage();
      return undefined;
    }
    
    return entry.data;
  }
  
  /**
   * Store a list of messages in the cache
   * @param searchId The ID of the search the messages belong to
   * @param response The message list response to cache
   * @param options The options used to fetch the messages
   */
  setMessageList(searchId: string, response: MessageListResponse, options?: {
    limit?: number;
    offset?: number;
  }): void {
    const key = this.generateMessageListKey(searchId, options);
    const entry: CacheEntry<MessageListResponse> = {
      data: response,
      timestamp: Date.now(),
      key
    };
    
    this.messageListCache.set(key, entry);
    
    // Also cache individual messages
    response.items.forEach(message => {
      this.setMessage(message);
    });
    
    this.saveToStorage();
  }
  
  /**
   * Get a list of messages from the cache if it exists and is not expired
   * @param searchId The ID of the search the messages belong to
   * @param options The options used to fetch the messages
   * @returns The cached message list or undefined if not found or expired
   */
  getMessageList(searchId: string, options?: {
    limit?: number;
    offset?: number;
  }): MessageListResponse | undefined {
    const key = this.generateMessageListKey(searchId, options);
    const entry = this.messageListCache.get(key);
    if (!entry) return undefined;
    
    // Check if the entry is expired
    if (Date.now() - entry.timestamp > this.config.ttl) {
      this.messageListCache.delete(key);
      this.saveToStorage();
      return undefined;
    }
    
    return entry.data;
  }
  
  /**
   * Invalidate all cache entries related to a specific search
   * @param searchId The ID of the search to invalidate
   */
  invalidateSearch(searchId: string): void {
    if (!searchId) return;
    
    // Remove the session from the cache
    this.sessionCache.delete(searchId);
    
    // Remove any message lists for this search
    for (const [key, entry] of this.messageListCache.entries()) {
      if (key.startsWith(`messages:${searchId}:`)) {
        this.messageListCache.delete(key);
      }
    }
    
    // Remove any session lists (they might contain this session)
    this.clearSessionListCache();
    
    this.saveToStorage();
  }
  
  /**
   * Invalidate message list cache for a specific search
   * @param searchId The ID of the search to invalidate message lists for
   */
  invalidateMessageList(searchId: string): void {
    if (!searchId) return;
    
    // Remove any message lists for this search
    for (const [key, entry] of this.messageListCache.entries()) {
      if (key.startsWith(`messages:${searchId}:`)) {
        this.messageListCache.delete(key);
      }
    }
    
    this.saveToStorage();
  }
  
  /**
   * Clear all cache entries
   */
  clear(): void {
    this.sessionCache.clear();
    this.clearSessionListCache();
    this.clearMessageCache();
    this.messageListCache.clear();
    
    // Clear localStorage
    if (typeof window !== 'undefined' && this.config.persistToStorage) {
      localStorage.removeItem('researchCache');
    }
  }
  
  /**
   * Clear all session list cache entries
   */
  clearSessionListCache(): void {
    this.sessionListCache.clear();
    this.saveToStorage();
  }
  
  /**
   * Delete a message from the cache
   * @param messageId The ID of the message to delete
   */
  deleteMessage(messageId: string): void {
    this.messageCache.delete(messageId);
    this.saveToStorage();
  }

  /**
   * Clear all message cache entries
   */
  clearMessageCache(): void {
    this.messageCache.clear();
    this.saveToStorage();
  }
  
  /**
   * Generate a unique key for session list options
   * @param options The options to generate a key for
   * @returns A string key
   */
  private generateOptionsKey(options?: {
    featuredOnly?: boolean;
    status?: QueryStatus;
    limit?: number;
    offset?: number;
  }): string {
    return `sessions:${JSON.stringify(options || {})}`;
  }
  
  /**
   * Generate a unique key for message list options
   * @param searchId The ID of the search
   * @param options The options to generate a key for
   * @returns A string key
   */
  private generateMessageListKey(searchId: string, options?: {
    limit?: number;
    offset?: number;
  }): string {
    return `messages:${searchId}:${JSON.stringify(options || {})}`;
  }
  
  /**
   * Save the cache to localStorage
   */
  private saveToStorage(): void {
    if (typeof window === 'undefined' || !this.config.persistToStorage) return;
    
    try {
      // Only persist sessions to avoid localStorage size limits
      const sessionsToStore: Record<string, CacheEntry<ResearchSession>> = {};
      this.sessionCache.forEach((entry, key) => {
        sessionsToStore[key] = entry;
      });
      
      localStorage.setItem('researchCache', JSON.stringify({
        sessions: sessionsToStore,
        timestamp: Date.now()
      }));
    } catch (error) {
      console.error('Failed to save research cache to localStorage:', error);
    }
  }
  
  /**
   * Load the cache from localStorage
   */
  private loadFromStorage(): void {
    if (typeof window === 'undefined' || !this.config.persistToStorage) return;
    
    try {
      const storedCache = localStorage.getItem('researchCache');
      if (!storedCache) return;
      
      const parsed = JSON.parse(storedCache);
      if (!parsed || !parsed.sessions || !parsed.timestamp) return;
      
      // Check if the entire cache is expired
      if (Date.now() - parsed.timestamp > this.config.ttl) {
        localStorage.removeItem('researchCache');
        return;
      }
      
      // Load sessions
      Object.entries(parsed.sessions).forEach(([key, entry]: [string, any]) => {
        if (entry && entry.data && entry.timestamp) {
          // Check if the individual entry is expired
          if (Date.now() - entry.timestamp <= this.config.ttl) {
            this.sessionCache.set(key, entry as CacheEntry<ResearchSession>);
          }
        }
      });
    } catch (error) {
      console.error('Failed to load research cache from localStorage:', error);
    }
  }
  
  /**
   * Check if a cache entry is about to expire and refresh it if needed
   * @param key The cache key to check
   * @param refreshThreshold The threshold in milliseconds before expiration to refresh
   * @param refreshFn The function to call to refresh the cache entry
   */
  async refreshCacheIfNeeded<T>(
    cacheMap: Map<string, CacheEntry<T>>,
    key: string,
    refreshThreshold: number,
    refreshFn: () => Promise<T>
  ): Promise<void> {
    const entry = cacheMap.get(key);
    if (!entry) return;
    
    const timeUntilExpiration = this.config.ttl - (Date.now() - entry.timestamp);
    
    // If the entry is about to expire, refresh it
    if (timeUntilExpiration < refreshThreshold) {
      try {
        const freshData = await refreshFn();
        const updatedEntry: CacheEntry<T> = {
          data: freshData,
          timestamp: Date.now(),
          key
        };
        cacheMap.set(key, updatedEntry);
      } catch (error) {
        console.error('Failed to refresh cache entry:', error);
      }
    }
  }
}

// Create a singleton instance of the cache
const researchCache = new ResearchCache();

export interface ApiError {
  status: number
  statusText: string
  message: string
  details?: any
  code?: string
  retryAfter?: number  // For rate limiting errors
}

export async function getAuthHeader() {
  const { data } = await supabase.auth.getSession()
  const token = data.session?.access_token
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
}

interface SearchListResponse {
  items: ResearchSession[]
  total: number
  offset: number
  limit: number
}

/**
 * Utility function to retry API calls with exponential backoff
 * @param fn The async function to retry
 * @param maxRetries Maximum number of retry attempts
 * @param retryDelay Initial delay in milliseconds
 * @param shouldRetry Function to determine if the error is retryable
 * @returns The result of the function call
 */
async function withRetry<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  retryDelay: number = 1000,
  shouldRetry: (error: any) => boolean = (error) => {
    // By default, retry on network errors and 5xx server errors
    if (error instanceof Error && error.message.includes('network')) {
      return true
    }
    if (error && 'status' in error) {
      // Retry on server errors (5xx)
      return error.status >= 500 && error.status < 600
    }
    return false
  }
): Promise<T> {
  let lastError: any
  
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn()
    } catch (error) {
      lastError = error
      
      // Don't retry if we've reached max retries or if the error isn't retryable
      if (attempt >= maxRetries || !shouldRetry(error)) {
        throw error
      }
      
      // If this is a rate limiting error with a retry-after header, use that time
      if (error && typeof error === 'object' && 'retryAfter' in error && typeof error.retryAfter === 'number') {
        // Use type assertion to tell TypeScript that retryAfter is a number
        const typedError = error as { retryAfter: number }
        await new Promise(resolve => setTimeout(resolve, typedError.retryAfter * 1000))
      } else {
        // Otherwise use exponential backoff
        const delay = retryDelay * Math.pow(2, attempt)
        await new Promise(resolve => setTimeout(resolve, delay))
      }
      
      console.log(`Retrying API call (attempt ${attempt + 1}/${maxRetries})...`)
    }
  }
  
  // This should never be reached due to the throw in the loop, but TypeScript needs it
  throw lastError
}

/**
 * Helper function to handle API errors
 * @param response The response object from the API call
 * @returns A formatted ApiError object with user-friendly messages
 */
export async function handleApiError(response: Response): Promise<never> {
  let errorMessage = `HTTP ${response.status}: ${response.statusText}`
  let errorDetails: any = undefined
  
  try {
    // Try to parse error body as JSON
    const errorData = await response.json()
    errorMessage = errorData.detail || errorData.message || errorMessage
    errorDetails = errorData
  } catch (e) {
    // If JSON parsing fails, use status text
    console.error('Failed to parse error response', e)
  }
  
  // Create a base error object
  const apiError: ApiError = {
    status: response.status,
    statusText: response.statusText,
    message: errorMessage,
    details: errorDetails
  }
  
  // Check for Retry-After header (common in rate limiting responses)
  const retryAfter = response.headers.get('Retry-After')
  if (retryAfter) {
    const parsedRetryAfter = parseInt(retryAfter, 10)
    if (!isNaN(parsedRetryAfter)) {
      apiError.retryAfter = parsedRetryAfter
    }
  }
  
  // Format the error with user-friendly messages
  const formattedError = formatApiError(apiError);
  
  throw formattedError
}

/**
 * Formats an API error with user-friendly messages based on error codes
 * This function can be used by both the API service and the context
 * @param error The API error object to format
 * @param defaultMessage Optional default message to use if no specific message is available
 * @returns A formatted ApiError object with user-friendly messages
 */
export function formatApiError(error: ApiError, defaultMessage?: string): ApiError {
  // Create a copy of the error to avoid mutating the original
  const formattedError: ApiError = { ...error };
  
  // If a default message is provided and we don't have a message, use it
  if (defaultMessage && !formattedError.message) {
    formattedError.message = defaultMessage;
  }
  
  // Add specific handling for common error codes
  switch (formattedError.status) {
    case 401:
      formattedError.message = 'Your session has expired. Please log in again.'
      formattedError.code = 'AUTH_REQUIRED'
      break
    case 403:
      formattedError.message = 'You do not have permission to perform this action.'
      formattedError.code = 'PERMISSION_DENIED'
      break
    case 404:
      formattedError.message = 'The requested resource was not found.'
      formattedError.code = 'NOT_FOUND'
      break
    case 409:
      formattedError.message = 'This operation conflicts with the current state.'
      formattedError.code = 'CONFLICT'
      break
    case 429:
      formattedError.message = 'Too many requests. Please try again later.'
      formattedError.code = 'RATE_LIMITED'
      
      // Check for Retry-After header (common in rate limiting responses)
      if (formattedError.retryAfter) {
        formattedError.message = `Rate limit exceeded. Please try again in ${formattedError.retryAfter} seconds.`
      }
      
      // Special handling for Perplexity Sonar API rate limiting
      if (formattedError.details?.error?.includes?.('rate limit') || 
          formattedError.details?.message?.toLowerCase?.().includes('rate limit') ||
          formattedError.details?.detail?.toLowerCase?.().includes('rate limit') ||
          formattedError.details?.message?.toLowerCase?.().includes('perplexity') ||
          formattedError.details?.detail?.toLowerCase?.().includes('perplexity') ||
          formattedError.details?.message?.toLowerCase?.().includes('sonar') ||
          formattedError.details?.detail?.toLowerCase?.().includes('sonar')) {
        formattedError.code = 'PERPLEXITY_RATE_LIMITED'
        formattedError.message = 'Perplexity API rate limit reached. Please try again later.'
      }
      break
    case 500:
    case 502:
    case 503:
    case 504:
      formattedError.message = 'A server error occurred. Please try again later.'
      formattedError.code = 'SERVER_ERROR'
      break
  }
  
  // If we have more specific error details from the API, use those instead
  if (formattedError.details?.detail || formattedError.details?.message) {
    // But keep our specific code if we assigned one
    const code = formattedError.code
    formattedError.message = formattedError.details.detail || formattedError.details.message
    if (code) formattedError.code = code
  }
  
  return formattedError;
}

/**
 * Utility function to clear the cache after a certain time period
 * @param minutes Number of minutes after which to clear the cache
 * @returns A function to cancel the scheduled cache clear
 */
export function scheduleCacheClear(minutes: number = 60): () => void {
  const timeoutId = setTimeout(() => {
    cache.clear();
  }, minutes * 60 * 1000);
  
  // Return a function to cancel the scheduled cache clear
  return () => clearTimeout(timeoutId);
}

/**
 * Fetch a list of research sessions
 * @param options Options for filtering and pagination
 * @returns A list of research sessions
 */
export async function fetchSessions(options?: {
  featuredOnly?: boolean
  status?: QueryStatus
  limit?: number
  offset?: number
}): Promise<SearchListResponse> {
  // Check cache first
  const cachedResponse = researchCache.getSessionList(options);
  if (cachedResponse) {
    return cachedResponse;
  }

  const headers = await getAuthHeader()
  
  // Build query parameters
  const params = new URLSearchParams()
  if (options?.featuredOnly) params.append('featured_only', 'true')
  if (options?.status) params.append('status', options.status)
  if (options?.limit) params.append('limit', options.limit.toString())
  if (options?.offset) params.append('offset', options.offset.toString())
  
  const queryString = params.toString() ? `?${params.toString()}` : ''
  const response = await withRetry(() => fetch(`/api/research/searches${queryString}`, { headers }))
  
  if (!response.ok) return handleApiError(response)
  const data = await response.json()
  
  // Cache the response
  researchCache.setSessionList(options, data);
  
  return data
}

/**
 * Fetch a single research session by ID
 * @param sessionId The ID of the session to fetch
 * @returns The research session
 */
export async function fetchSession(sessionId: string): Promise<ResearchSession> {
  // Check cache first
  const cachedSession = researchCache.getSession(sessionId);
  if (cachedSession) {
    return cachedSession;
  }

  const headers = await getAuthHeader()
  const response = await withRetry(() => fetch(`/api/research/searches/${sessionId}`, { headers }))
  
  if (!response.ok) return handleApiError(response)
  const data = await response.json()
  
  // Cache the response
  researchCache.setSession(data);
  
  return data
}

/**
 * Create a new research session
 * @param query The query to research
 * @param searchParams Optional parameters for the search
 * @returns The newly created research session
 */
export async function createNewSession(query: string, searchParams?: SearchParams): Promise<ResearchSession> {
  const headers = await getAuthHeader()
  const response = await withRetry(() => fetch('/api/research/searches', {
    method: 'POST',
    headers,
    body: JSON.stringify({ 
      query,
      search_params: searchParams || {}
    })
  }))
  
  if (!response.ok) return handleApiError(response)
  const data = await response.json()
  
  // Cache the new session
  researchCache.setSession(data);
  
  // Invalidate session lists as they're now outdated
  researchCache.clearSessionListCache();
  
  return data
}

/**
 * Send a message to a research session
 * @param sessionId The ID of the session to send a message to
 * @param content The content of the message
 * @returns The updated research session
 */
export async function sendSessionMessage(sessionId: string, content: string): Promise<ResearchSession> {
  const headers = await getAuthHeader()
  
  // Use a more aggressive retry strategy for sendSessionMessage due to Perplexity API issues
  const response = await withRetry(
    () => fetch(`/api/research/searches/${sessionId}/continue`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ follow_up_query: content })
    }),
    // More retries for this specific endpoint
    5,
    // Longer initial delay
    2000,
    // Custom retry condition that specifically looks for Perplexity-related errors
    (error) => {
      // Always retry server errors
      if (error && typeof error === 'object' && 'status' in error && 
          (error as { status: number }).status >= 500 && (error as { status: number }).status < 600) {
        return true
      }
      
      // Retry network errors
      if (error instanceof Error && error.message.includes('network')) {
        return true
      }
      
      // Specifically retry Perplexity rate limiting errors
      if (error && typeof error === 'object' && 'code' in error && 
          ((error as { code: string }).code === 'PERPLEXITY_RATE_LIMITED' || (error as { code: string }).code === 'RATE_LIMITED')) {
        return true
      }
      
      return false
    }
  )
  
  if (!response.ok) return handleApiError(response)
  const data = await response.json()
  
  // Cache the updated session
  researchCache.setSession(data);
  
  // Invalidate message lists for this session as they're now outdated
  researchCache.invalidateSearch(sessionId);
  
  return data
}

/**
 * Update the metadata of a research session
 * @param sessionId The ID of the session to update
 * @param updates The updates to apply
 * @returns The updated research session
 */
export async function updateSessionMetadata(sessionId: string, updates: {
  title?: string
  description?: string
  is_featured?: boolean
  tags?: string[]
  category?: QueryCategory
  query_type?: QueryType
  status?: QueryStatus
}): Promise<ResearchSession> {
  const headers = await getAuthHeader()
  const response = await withRetry(() => fetch(`/api/research/searches/${sessionId}`, {
    method: 'PATCH',
    headers,
    body: JSON.stringify(updates)
  }))
  
  if (!response.ok) return handleApiError(response)
  const data = await response.json()
  
  // Cache the updated session
  researchCache.setSession(data);
  
  // Invalidate session lists as they're now outdated
  researchCache.clearSessionListCache();
  
  return data
}

/**
 * Delete a research session
 * @param sessionId The ID of the session to delete
 */
export async function deleteSession(sessionId: string): Promise<void> {
  const headers = await getAuthHeader()
  const response = await withRetry(() => fetch(`/api/research/searches/${sessionId}`, {
    method: 'DELETE',
    headers
  }))
  
  if (!response.ok) return handleApiError(response)
  
  // Invalidate cache for this session
  researchCache.invalidateSearch(sessionId);
  
  // Invalidate session lists as they're now outdated
  researchCache.clearSessionListCache();
}

// Message-specific API functions

export interface MessageListResponse {
  items: Message[]
  total: number
  offset: number
  limit: number
}

/**
 * Fetch a single message by ID
 * @param messageId The ID of the message to fetch
 * @returns The message
 */
export async function fetchMessage(messageId: string): Promise<Message> {
  // Check cache first
  const cachedMessage = researchCache.getMessage(messageId);
  if (cachedMessage) {
    return cachedMessage;
  }

  const headers = await getAuthHeader()
  const response = await withRetry(() => fetch(`/api/research/messages/${messageId}`, { headers }))
  
  if (!response.ok) return handleApiError(response)
  const data = await response.json()
  
  // Cache the response
  researchCache.setMessage(data);
  
  return data
}

/**
 * Fetch messages for a research session
 * @param searchId The ID of the search to fetch messages for
 * @param options Options for pagination
 * @returns A list of messages
 */
export async function fetchMessagesForSearch(
  searchId: string,
  options?: {
    limit?: number
    offset?: number
  }
): Promise<MessageListResponse> {
  // Check cache first
  const cachedMessages = researchCache.getMessageList(searchId, options);
  if (cachedMessages) {
    return cachedMessages;
  }

  const headers = await getAuthHeader()
  
  // Build query parameters
  const params = new URLSearchParams()
  if (options?.limit) params.append('limit', options.limit.toString())
  if (options?.offset) params.append('offset', options.offset.toString())
  
  const queryString = params.toString() ? `?${params.toString()}` : ''
  const response = await withRetry(() => 
    fetch(`/api/research/searches/${searchId}/messages${queryString}`, { headers })
  )
  
  if (!response.ok) return handleApiError(response)
  const data = await response.json()
  
  // Cache the response
  researchCache.setMessageList(searchId, data, options);
  
  return data
}

/**
 * Update a message
 * @param messageId The ID of the message to update
 * @param updates The updates to apply
 * @returns The updated message
 */
export async function updateMessage(
  messageId: string, 
  updates: {
    content?: { text: string, citations?: Citation[] }
    status?: QueryStatus
  }
): Promise<Message> {
  const headers = await getAuthHeader()
  const response = await withRetry(() => fetch(`/api/research/messages/${messageId}`, {
    method: 'PATCH',
    headers,
    body: JSON.stringify(updates)
  }))
  
  if (!response.ok) return handleApiError(response)
  const data = await response.json()
  
  // Cache the updated message
  researchCache.setMessage(data);
  
  // Invalidate session cache as it might contain this message
  if (data.search_id) {
    researchCache.invalidateSearch(data.search_id);
  }
  
  return data
}

/**
 * Delete a message
 * @param messageId The ID of the message to delete
 * @param searchId Optional search ID if known, to avoid extra API call
 */
export async function deleteMessage(messageId: string, searchId?: string): Promise<void> {
  const headers = await getAuthHeader()
  
  // If searchId wasn't provided, try to get it from the message
  if (!searchId) {
    try {
      const message = await fetchMessage(messageId);
      // Try different property names that might contain the search ID
      searchId = (message as any).search_id || (message as any).searchId || (message as any).session_id || (message as any).sessionId;
    } catch (error) {
      console.error('Failed to fetch message before deletion:', error);
    }
  }
  
  const response = await withRetry(() => fetch(`/api/research/messages/${messageId}`, {
    method: 'DELETE',
    headers
  }))
  
  if (!response.ok) return handleApiError(response)
  
  // Remove the message from cache
  researchCache.deleteMessage(messageId);
  
  // Invalidate related caches
  if (searchId) {
    researchCache.invalidateSearch(searchId);
  }
}

/**
 * Forward a message
 * @param messageId The ID of the message to forward
 * @param destination The destination to forward the message to
 * @param destinationType The type of destination (email, user, workspace)
 */
export async function forwardMessage(
  messageId: string,
  destination: string,
  destinationType: 'email' | 'user' | 'workspace'
): Promise<any> {
  const headers = await getAuthHeader()
  const response = await withRetry(() => fetch(`/api/research/messages/${messageId}/forward`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      destination,
      destination_type: destinationType
    })
  }))
  
  if (!response.ok) return handleApiError(response)
  return await response.json()
}

// WebSocket connection for real-time updates

export interface WebSocketMessage {
  type: string;
  data?: any;
  message?: string;
  search_id?: string;
  status?: string;
  subscribed_to?: string[];
}

export interface WebSocketConnection {
  disconnect: () => void;
  send: (data: any) => void;
  isConnected: boolean;
}

/**
 * Establishes a WebSocket connection for real-time message updates
 * @param searchId The ID of the search/conversation to connect to
 * @param onMessage Callback function for handling incoming messages
 * @param onError Callback function for handling errors
 * @param onClose Optional callback function for handling connection close
 * @returns A WebSocketConnection object with methods to interact with the connection
 */
export async function connectToMessageUpdates(
  searchId: string,
  onMessage: (message: WebSocketMessage) => void,
  onError: (error: any) => void,
  onClose?: () => void
): Promise<WebSocketConnection> {
  // Get the auth token
  const headers = await getAuthHeader();
  const token = headers.Authorization.replace('Bearer ', '');
  
  // Create WebSocket connection
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsHost = window.location.host;
  const wsUrl = `${wsProtocol}//${wsHost}/api/research/messages/ws/${searchId}?token=${token}`;
  
  // Reconnection settings
  const maxReconnectAttempts = 5;
  const baseReconnectDelay = 1000; // 1 second
  let reconnectAttempts = 0;
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  let pingInterval: ReturnType<typeof setInterval> | null = null;
  let heartbeatTimeout: ReturnType<typeof setTimeout> | null = null;
  
  console.log(`Connecting to WebSocket at ${wsUrl}`);
  let socket = new WebSocket(wsUrl);
  let isConnected = false;
  let isReconnecting = false;
  let manualDisconnect = false;
  
  // Function to clear all timers
  const clearTimers = () => {
    if (pingInterval) {
      clearInterval(pingInterval);
      pingInterval = null;
    }
    if (heartbeatTimeout) {
      clearTimeout(heartbeatTimeout);
      heartbeatTimeout = null;
    }
    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }
  };
  
  // Function to handle reconnection
  const reconnect = async () => {
    if (manualDisconnect || isReconnecting) return;
    
    isReconnecting = true;
    
    if (reconnectAttempts >= maxReconnectAttempts) {
      console.error(`Failed to reconnect after ${maxReconnectAttempts} attempts`);
      onError(new Error(`Failed to reconnect after ${maxReconnectAttempts} attempts`));
      isReconnecting = false;
      return;
    }
    
    // Clear any existing timers
    clearTimers();
    
    // Calculate delay with exponential backoff
    const delay = baseReconnectDelay * Math.pow(2, reconnectAttempts);
    console.log(`Attempting to reconnect in ${delay}ms (attempt ${reconnectAttempts + 1}/${maxReconnectAttempts})`);
    
    reconnectTimer = setTimeout(async () => {
      reconnectAttempts++;
      
      try {
        // Get a fresh token in case the old one expired
        const freshHeaders = await getAuthHeader();
        const freshToken = freshHeaders.Authorization.replace('Bearer ', '');
        const freshUrl = `${wsProtocol}//${wsHost}/api/research/messages/ws/${searchId}?token=${freshToken}`;
        
        // Create a new socket
        socket = new WebSocket(freshUrl);
        
        // Set up event listeners for the new socket
        setupEventListeners();
      } catch (error) {
        console.error('Error during reconnection:', error);
        isReconnecting = false;
        reconnect(); // Try again
      }
    }, delay);
  };
  
  // Function to set up event listeners
  const setupEventListeners = () => {
    // Connection opened
    socket.addEventListener('open', () => {
      console.log('WebSocket connection established');
      isConnected = true;
      isReconnecting = false;
      reconnectAttempts = 0; // Reset reconnect attempts on successful connection
      
      // Subscribe to all message types
      socket.send(JSON.stringify({
        command: 'subscribe',
        message_types: ['user', 'assistant']
      }));
      
      // Set up ping interval (every 25 seconds)
      pingInterval = setInterval(() => {
        if (socket.readyState === WebSocket.OPEN) {
          socket.send(JSON.stringify({
            command: 'ping',
            timestamp: Date.now()
          }));
        }
      }, 25000);
    });
    
    // Listen for messages
    socket.addEventListener('message', (event) => {
      try {
        const message = JSON.parse(event.data) as WebSocketMessage;
        console.log('Received WebSocket message:', message);
        
        // Handle heartbeat messages
        if (message.type === 'heartbeat' || message.type === 'pong') {
          // Reset heartbeat timeout
          if (heartbeatTimeout) {
            clearTimeout(heartbeatTimeout);
          }
          
          // Set a new timeout - if we don't receive a heartbeat within 70 seconds, reconnect
          heartbeatTimeout = setTimeout(() => {
            console.warn('No heartbeat received, reconnecting...');
            socket.close();
            reconnect();
          }, 70000);
          
          // Don't forward heartbeat messages to the client
          if (message.type === 'heartbeat') {
            return;
          }
        }
        
        onMessage(message);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
        onError(error);
      }
    });
    
    // Listen for errors
    socket.addEventListener('error', (event) => {
      console.error('WebSocket error:', event);
      onError(event);
    });
    
    // Listen for connection close
    socket.addEventListener('close', (event) => {
      console.log(`WebSocket connection closed: ${event.code} ${event.reason}`);
      isConnected = false;
      
      // Clear intervals
      clearTimers();
      
      if (onClose) onClose();
      
      // Attempt to reconnect unless manually disconnected
      if (!manualDisconnect) {
        reconnect();
      }
    });
  };
  
  // Set up initial event listeners
  setupEventListeners();
  
  // Return connection interface
  return {
    disconnect: () => {
      manualDisconnect = true;
      clearTimers();
      
      if (socket.readyState === WebSocket.OPEN) {
        socket.close();
      }
    },
    send: (data: any) => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify(data));
      } else if (!manualDisconnect) {
        console.warn('Cannot send message: WebSocket is not open, queuing reconnect');
        reconnect();
      } else {
        console.warn('Cannot send message: WebSocket was manually disconnected');
      }
    },
    get isConnected() {
      return isConnected;
    }
  };
}

/**
 * Helper function to request latest messages via WebSocket
 * @param connection The WebSocketConnection to use
 * @param limit Maximum number of messages to retrieve
 * @param offset Pagination offset
 */
export function requestLatestMessages(connection: WebSocketConnection, limit: number = 10, offset: number = 0): void {
  if (!connection.isConnected) {
    console.warn('Cannot request messages: WebSocket is not connected');
    return;
  }
  
  connection.send({
    command: 'get_latest',
    limit,
    offset
  });
}

/**
 * Helper function to notify the server that the user is typing
 * @param connection The WebSocketConnection to use
 */
export function sendTypingNotification(connection: WebSocketConnection): void {
  if (!connection.isConnected) return;
  
  connection.send({
    command: 'typing'
  });
}

// Export cache functions for direct use
export const cache = {
  clear: () => researchCache.clear(),
  invalidateSearch: (searchId: string) => researchCache.invalidateSearch(searchId),
  invalidateMessageList: (searchId: string) => researchCache.invalidateMessageList(searchId),
  getSession: (sessionId: string) => researchCache.getSession(sessionId),
  getMessage: (messageId: string) => researchCache.getMessage(messageId),
  getSessionList: (options?: any) => researchCache.getSessionList(options),
  getMessageList: (searchId: string, options?: any) => researchCache.getMessageList(searchId, options),
  setSession: (session: ResearchSession) => researchCache.setSession(session),
  setMessage: (message: Message) => researchCache.setMessage(message),
  clearSessionListCache: () => researchCache.clearSessionListCache(),
  deleteMessage: (messageId: string) => researchCache.deleteMessage(messageId),
  clearMessageCache: () => researchCache.clearMessageCache(),
  refreshCacheIfNeeded: <T>(cacheMap: Map<string, CacheEntry<T>>, key: string, refreshThreshold: number, refreshFn: () => Promise<T>) => 
    researchCache.refreshCacheIfNeeded(cacheMap, key, refreshThreshold, refreshFn),
  config: researchCache.config
}
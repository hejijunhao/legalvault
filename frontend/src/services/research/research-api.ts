// src/services/research/research-api.ts

import { supabase } from '@/lib/supabase'
import { Message, ResearchSession, SearchParams, QueryStatus, QueryCategory, QueryType, Citation } from '@/contexts/research/research-context'
import authManager from '@/lib/auth-manager'

// Define sensitive fields that should not be stored in localStorage
type SensitiveField = 'access_token' | 'refresh_token' | 'token' | 'password' | 'secret';

// Cache configuration
interface CacheConfig {
  ttl: number;  // Time to live in milliseconds
  maxSize?: number; // Maximum number of items to store in memory
  persistToStorage?: boolean; // Whether to persist cache to localStorage
  security?: CacheSecurityConfig; // Security configuration
}

// Configuration for cache security
interface CacheSecurityConfig {
  sanitizeForStorage: boolean; // Whether to sanitize data before storing in localStorage
  sensitiveFields: SensitiveField[]; // Fields to remove or encrypt
  encryptSensitiveData: boolean; // Whether to encrypt sensitive data instead of removing it
}

interface CacheEntry<T> {
  data: T;
  timestamp: number;
  key: string;
}

// Default security configuration
const DEFAULT_SECURITY_CONFIG: CacheSecurityConfig = {
  sanitizeForStorage: true,
  sensitiveFields: ['access_token', 'refresh_token', 'token', 'password', 'secret'],
  encryptSensitiveData: false // Default to removing rather than encrypting
};

// Default cache configuration
const DEFAULT_CACHE_CONFIG: CacheConfig = {
  ttl: 5 * 60 * 1000, // 5 minutes default TTL
  maxSize: 100, // Store up to 100 items in memory
  persistToStorage: true, // Persist to localStorage by default
  security: DEFAULT_SECURITY_CONFIG
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
   * @param response The session list response to cache
   * @param options The options used to fetch the sessions
   */
  setSessionList(response: SearchListResponse, options?: {
    featuredOnly?: boolean;
    status?: QueryStatus;
    limit?: number;
    offset?: number;
  } | null): void {
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
  } | null): SearchListResponse | undefined {
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
  } | null): void {
    if (!searchId) return;
    
    const key = this.generateMessageOptionsKey(searchId, options);
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
  } | null): MessageListResponse | undefined {
    if (!searchId) return undefined;
    
    const key = this.generateMessageOptionsKey(searchId, options);
    const entry = this.messageListCache.get(key);
    if (!entry) return undefined;
    
    // Check if the entry is expired
    if (Date.now() - entry.timestamp > this.config.ttl) {
      this.messageListCache.delete(key);
      return undefined;
    }
    
    return entry.data;
  }
  
  /**
   * Delete a session from the cache
   * @param sessionId The ID of the session to delete
   */
  deleteSession(sessionId: string): void {
    if (!sessionId) return;
    
    this.sessionCache.delete(sessionId);
    this.saveToStorage();
  }
  
  /**
   * Delete a message from the cache
   * @param messageId The ID of the message to delete
   */
  deleteMessage(messageId: string): void {
    if (!messageId) return;
    
    this.messageCache.delete(messageId);
  }
  
  /**
   * Invalidate all caches related to a search
   * @param searchId The ID of the search to invalidate
   */
  invalidateSearch(searchId: string): void {
    if (!searchId) return;
    
    // Delete the search from the session cache
    this.sessionCache.delete(searchId);
    
    // Delete all message lists for this search
    const messageListKeys = Array.from(this.messageListCache.keys())
      .filter(key => key.startsWith(`search:${searchId}:`));
    
    messageListKeys.forEach(key => {
      this.messageListCache.delete(key);
    });
    
    this.saveToStorage();
  }
  
  /**
   * Invalidate the message list cache for a search
   * @param searchId The ID of the search to invalidate
   */
  invalidateMessageList(searchId: string): void {
    if (!searchId) return;
    
    // Delete all message lists for this search
    const messageListKeys = Array.from(this.messageListCache.keys())
      .filter(key => key.startsWith(`search:${searchId}:`));
    
    messageListKeys.forEach(key => {
      this.messageListCache.delete(key);
    });
  }
  
  /**
   * Clear the entire cache
   */
  clear(): void {
    this.sessionCache.clear();
    this.sessionListCache.clear();
    this.messageCache.clear();
    this.messageListCache.clear();
    
    // Clear localStorage
    if (typeof localStorage !== 'undefined') {
      localStorage.removeItem('research_session_cache');
      localStorage.removeItem('research_session_list_cache');
    }
  }
  
  /**
   * Clear the session list cache
   */
  clearSessionListCache(): void {
    this.sessionListCache.clear();
    
    // Update localStorage
    if (typeof localStorage !== 'undefined' && this.config.persistToStorage) {
      localStorage.removeItem('research_session_list_cache');
    }
  }
  
  /**
   * Clear the message cache
   */
  clearMessageCache(): void {
    this.messageCache.clear();
    this.messageListCache.clear();
  }
  
  /**
   * Generate a key for caching session lists based on options
   * @param options The options used to fetch the sessions
   * @returns A string key
   */
  generateOptionsKey(options?: {
    featuredOnly?: boolean;
    status?: QueryStatus;
    limit?: number;
    offset?: number;
  } | null): string {
    if (!options) return 'all';
    
    return `featured:${options.featuredOnly || false}:status:${options.status || 'all'}:limit:${options.limit || 10}:offset:${options.offset || 0}`;
  }
  
  /**
   * Generate a key for caching message lists based on search ID and options
   * @param searchId The ID of the search
   * @param options The options used to fetch the messages
   * @returns A string key
   */
  private generateMessageOptionsKey(searchId: string, options?: {
    limit?: number;
    offset?: number;
  } | null): string {
    if (!options) return `search:${searchId}:all`;
    
    return `search:${searchId}:limit:${options.limit || 10}:offset:${options.offset || 0}`;
  }
  
  /**
   * Sanitize data before storing in localStorage
   * Removes or encrypts sensitive fields
   * @param data The data to sanitize
   * @returns Sanitized data
   */
  private sanitizeData<T>(data: T): T {
    if (!this.config.security?.sanitizeForStorage) {
      return data;
    }
    
    if (!data || typeof data !== 'object') {
      return data;
    }
    
    // Create a deep copy to avoid modifying the original
    const sanitized = JSON.parse(JSON.stringify(data));
    
    // Get the list of sensitive fields
    const sensitiveFields = this.config.security.sensitiveFields || DEFAULT_SECURITY_CONFIG.sensitiveFields;
    
    // Function to recursively sanitize objects
    const sanitizeObject = (obj: any) => {
      if (!obj || typeof obj !== 'object') return;
      
      // Process each property
      Object.keys(obj).forEach(key => {
        // Check if this is a sensitive field
        if (sensitiveFields.includes(key as SensitiveField)) {
          if (this.config.security?.encryptSensitiveData) {
            // Implement encryption here if needed
            // For now, just mark as encrypted
            obj[key] = '[ENCRYPTED]';
          } else {
            // Remove sensitive data
            delete obj[key];
          }
        } else if (typeof obj[key] === 'object' && obj[key] !== null) {
          // Recursively sanitize nested objects
          sanitizeObject(obj[key]);
        }
      });
    };
    
    sanitizeObject(sanitized);
    return sanitized;
  }
  
  /**
   * Save cache to localStorage
   */
  private saveToStorage(): void {
    if (!this.config.persistToStorage || typeof localStorage === 'undefined') return;
    
    try {
      // Only save sessions to localStorage, not messages (to reduce size)
      const sessionEntries = Array.from(this.sessionCache.entries());
      const sessionListEntries = Array.from(this.sessionListCache.entries());
      
      // Sanitize data before storing
      const sanitizedSessions = sessionEntries.map(([key, entry]) => {
        return [key, { ...entry, data: this.sanitizeData(entry.data) }];
      });
      
      const sanitizedSessionLists = sessionListEntries.map(([key, entry]) => {
        return [key, { ...entry, data: this.sanitizeData(entry.data) }];
      });
      
      localStorage.setItem('research_session_cache', JSON.stringify(sanitizedSessions));
      localStorage.setItem('research_session_list_cache', JSON.stringify(sanitizedSessionLists));
    } catch (error) {
      console.error('Error saving cache to localStorage:', error);
    }
  }
  
  /**
   * Load cache from localStorage
   */
  private loadFromStorage(): void {
    if (!this.config.persistToStorage || typeof localStorage === 'undefined') return;
    
    try {
      const sessionCacheJson = localStorage.getItem('research_session_cache');
      const sessionListCacheJson = localStorage.getItem('research_session_list_cache');
      
      if (sessionCacheJson) {
        const sessionEntries = JSON.parse(sessionCacheJson);
        sessionEntries.forEach(([key, entry]: [string, CacheEntry<ResearchSession>]) => {
          this.sessionCache.set(key, entry);
        });
      }
      
      if (sessionListCacheJson) {
        const sessionListEntries = JSON.parse(sessionListCacheJson);
        sessionListEntries.forEach(([key, entry]: [string, CacheEntry<SearchListResponse>]) => {
          this.sessionListCache.set(key, entry);
        });
      }
    } catch (error) {
      console.error('Error loading cache from localStorage:', error);
      // If there's an error loading from localStorage, clear it to prevent future errors
      localStorage.removeItem('research_session_cache');
      localStorage.removeItem('research_session_list_cache');
    }
  }
  
  /**
   * Proactively refresh a cache entry if it's close to expiring
   * @param cacheMap The cache map to check
   * @param key The key of the entry to check
   * @param refreshThreshold The threshold in milliseconds before expiry to refresh
   * @param refreshFn Function to call to refresh the data
   */
  async refreshCacheIfNeeded<T>(
    cacheMap: Map<string, CacheEntry<T>>,
    key: string,
    refreshThreshold: number,
    refreshFn: () => Promise<T>
  ): Promise<void> {
    const entry = cacheMap.get(key);
    if (!entry) return;
    
    const timeUntilExpiration = (entry.timestamp + this.config.ttl) - Date.now();
    
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

export async function getAuthHeader(): Promise<Record<string, string>> {
  // Create base headers that will be returned regardless of auth status
  const headers: Record<string, string> = {
    'Content-Type': 'application/json'
  };
  
  // Guard clause for non-browser environments
  if (typeof window === 'undefined') {
    console.warn('getAuthHeader: Not in browser environment');
    return headers;
  }
  
  try {
    // Use the auth manager to get the access token directly
    console.log('getAuthHeader: Attempting to get access token');
    const accessToken = await authManager.getAccessToken();
    
    // Log token status (but not the actual token for security)
    console.log('getAuthHeader: Access token obtained:', accessToken ? 'Yes' : 'No');
    
    // Only add Authorization if we have a token
    if (accessToken) {
      headers['Authorization'] = `Bearer ${accessToken}`;
    } else {
      console.warn('getAuthHeader: Proceeding with request without Authorization header');
    }
    
    return headers;
  } catch (error) {
    console.error('getAuthHeader: Error getting access token:', error);
    
    // Return headers without Authorization as a fallback
    return headers;
  }
}

interface SearchListResponse {
  items: ResearchSession[]
  total: number
  offset: number
  limit: number
}

/**
 * Custom fetch function that handles self-signed certificates in development
 * @param url URL to fetch
 * @param options Fetch options
 * @returns Response from fetch
 */
async function fetchWithSelfSignedCert(url: string, options?: RequestInit): Promise<Response> {
  // In development, we've set NODE_TLS_REJECT_UNAUTHORIZED=0 in package.json
  // This should allow self-signed certificates, but we need to handle any remaining issues
  
  // Add timeout to fetch requests
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
  
  try {
    const fetchOptions = {
      ...options,
      signal: controller.signal,
    };
    
    // For absolute URLs, use them directly
    // For relative URLs, use the base URL from the environment or default to localhost
    let fetchUrl: string;
    try {
      fetchUrl = url.startsWith('http') 
        ? url 
        : `${process.env.NEXT_PUBLIC_API_URL || 'https://localhost:8000'}${url.startsWith('/') ? url : `/${url}`}`;
    } catch (urlError) {
      console.error('Error constructing URL:', urlError);
      fetchUrl = url; // Fallback to original URL
    }
    
    console.log(`Fetching: ${fetchUrl}`);
    
    // Check if fetch is available
    if (typeof fetch !== 'function') {
      throw new Error('Fetch API is not available in this environment');
    }
    
    const response = await fetch(fetchUrl, fetchOptions);
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    
    // Log detailed error information
    console.error('Fetch error details:', {
      url,
      error: error instanceof Error ? error.message : String(error),
      code: (error as any)?.code,
      type: error instanceof Error ? error.constructor.name : typeof error,
      stack: error instanceof Error ? error.stack : undefined
    });
    
    // Handle specific error types
    if (error instanceof Error) {
      // Handle abort error (timeout)
      if (error.name === 'AbortError') {
        throw new Error(`Request timeout after 30 seconds: ${url}`);
      }
      
      // Handle certificate errors
      if (error.message.includes('certificate') || 
          error.message.includes('SSL') || 
          error.message.includes('UNABLE_TO_VERIFY_LEAF_SIGNATURE') || 
          (error as any).code === 'UNABLE_TO_VERIFY_LEAF_SIGNATURE' ||
          (error as any).code === 'ECONNRESET') {
        
        console.warn('Certificate or connection error detected. Make sure the backend is running with SSL enabled.');
        console.warn('Backend should be started with: uvicorn main:app --reload --ssl-keyfile localhost+2-key.pem --ssl-certfile localhost+2.pem');
        
        // If we're in development, provide a more helpful error
        if (process.env.NODE_ENV === 'development') {
          throw new Error(
            `SSL Certificate or Connection Error: ${error.message}. ` +
            `Make sure the backend is running with SSL enabled and that the certificates are trusted. ` +
            `Check that NODE_TLS_REJECT_UNAUTHORIZED=0 is set in your environment.`
          );
        }
      }
      
      // Handle network errors
      if (error.message.includes('network') || 
          error.message.includes('fetch') ||
          error.message.includes('Failed to fetch') ||
          (error as any).code === 'ENOTFOUND' ||
          (error as any).code === 'ECONNREFUSED') {
        throw new Error(
          `Network Error: Could not connect to the server at ${url}. ` +
          `Make sure the backend server is running and accessible.`
        );
      }
    }
    
    // Rethrow the original error
    throw error;
  }
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
    if (!error) return false;
    
    // Don't retry on authentication errors (401)
    if (error && typeof error === 'object' && 'status' in error && error.status === 401) {
      console.log('Not retrying due to authentication error (401)');
      return false;
    }
    
    // Don't retry on redirect loops
    if (error && typeof error === 'object' && 'status' in error && error.status === 307) {
      console.log('Not retrying due to redirect (307)');
      return false;
    }
    
    if (error instanceof Error && (
      error.message.includes('network') ||
      error.message.includes('connection') ||
      error.message.includes('timeout') ||
      error.message.includes('abort')
    )) {
      return true
    }
    
    if (error && typeof error === 'object' && 'status' in error) {
      // Retry on server errors (5xx)
      return error.status >= 500 && error.status < 600
    }
    
    return false
  }
): Promise<T> {
  let lastError: any
  
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      // Wrap the function call in a try-catch to handle any synchronous errors
      const result = await fn()
      return result
    } catch (error) {
      console.log(`API call failed (attempt ${attempt + 1}/${maxRetries + 1}):`, error)
      lastError = error
      
      // Don't retry if we've reached max retries or if the error isn't retryable
      if (attempt >= maxRetries || !shouldRetry(error)) {
        console.log(`Not retrying: ${attempt >= maxRetries ? 'max retries reached' : 'error not retryable'}`)
        throw error
      }
      
      // If this is a rate limiting error with a retry-after header, use that time
      if (error && typeof error === 'object' && 'retryAfter' in error && typeof error.retryAfter === 'number') {
        // Use type assertion to tell TypeScript that retryAfter is a number
        const typedError = error as { retryAfter: number }
        const retryAfterMs = typedError.retryAfter * 1000
        console.log(`Rate limited. Retrying after ${retryAfterMs}ms...`)
        await new Promise(resolve => setTimeout(resolve, retryAfterMs))
      } else {
        // Otherwise use exponential backoff
        const delay = retryDelay * Math.pow(2, attempt)
        console.log(`Retrying API call after ${delay}ms (attempt ${attempt + 1}/${maxRetries})...`)
        await new Promise(resolve => setTimeout(resolve, delay))
      }
    }
  }
  
  // This should never be reached due to the throw in the loop, but TypeScript needs it
  console.error('Exhausted all retry attempts')
  throw lastError || new Error('Failed after multiple retry attempts')
}

/**
 * Helper function to handle API errors
 * @param response The response object from the API call
 * @returns A formatted ApiError object with user-friendly messages
 */
export async function handleApiError(response: Response): Promise<never> {
  // Guard against undefined or null response
  if (!response) {
    const error = new Error('No response received from server');
    (error as any).status = 0;
    (error as any).statusText = 'No Response';
    throw formatApiError(error, 'Server communication error');
  }
  
  // Special handling for authentication errors to prevent infinite loops
  if (response.status === 401) {
    const authError: ApiError = {
      status: 401,
      statusText: 'Unauthorized',
      message: 'Your session has expired. Please log in again.',
      details: { message: 'Authentication required' },
      code: 'AUTH_REQUIRED'
    };
    throw authError;
  }
  
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
export function formatApiError(error: ApiError | any, defaultMessage?: string): ApiError {
  // Handle case where error is undefined or null
  if (!error) {
    return {
      message: defaultMessage || 'An unknown error occurred',
      details: { message: 'No error details available' },
      status: 0,
      statusText: 'Unknown',
      code: 'UNKNOWN_ERROR'
    };
  }
  
  // Handle case where error is a string
  if (typeof error === 'string') {
    return {
      message: error,
      details: { message: error },
      status: 0,
      statusText: 'Unknown',
      code: 'STRING_ERROR'
    };
  }
  
  // Handle case where error is a plain Error object
  if (error instanceof Error && !('status' in error)) {
    return {
      message: error.message || defaultMessage || 'An error occurred',
      details: { message: error.message, stack: error.stack },
      status: 0,
      statusText: 'Error',
      code: 'JS_ERROR'
    };
  }
  
  // Create a copy of the error to avoid mutating the original
  const formattedError: ApiError = { ...error };
  
  // If a default message is provided and we don't have a message, use it
  if (defaultMessage && !formattedError.message) {
    formattedError.message = defaultMessage;
  }
  
  // Ensure we have a status code, defaulting to 0 if not present
  formattedError.status = formattedError.status || 0;
  
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
  append?: boolean
  skipAuthCheck?: boolean
} | null | undefined): Promise<SearchListResponse> {
  console.log('fetchSessions called with options:', options);
  
  // Prepare query parameters
  const params = new URLSearchParams();
  
  if (options?.featuredOnly) {
    params.append('featured', 'true');
  }
  
  if (options?.status) {
    params.append('status', options.status);
  }
  
  if (options?.limit) {
    params.append('limit', options.limit.toString());
  }
  
  if (options?.offset) {
    params.append('offset', options.offset.toString());
  }
  
  // Check cache first
  const cacheKey = researchCache.generateOptionsKey(options);
  const cachedData = researchCache.getSessionList(options);
  
  if (cachedData) {
    console.log('Using cached session list data');
    return cachedData;
  }
  
  // Get auth header for request
  console.log('Getting auth header for fetchSessions');
  const headers = await getAuthHeader();
  console.log('Headers being sent:', headers);
  
  // If no auth token and not explicitly skipping auth check, return empty results
  if (!headers.Authorization && !options?.skipAuthCheck) {
    console.log('No authorization token available, returning empty results');
    return {
      items: [],
      total: 0,
      offset: options?.offset || 0,
      limit: options?.limit || 10
    };
  }
  
  // Build query string
  const queryString = params.toString() ? `?${params.toString()}` : '';
  // Ensure URL has a trailing slash
  const baseUrl = '/api/research/searches/';
  const url = `${baseUrl}${queryString}`;
  console.log(`Making API request to: ${url} (baseUrl: ${baseUrl}, queryString: ${queryString})`);
  
  // Use a lower retry count for authentication-related requests to prevent excessive retries
  const response = await withRetry(
    () => fetchWithSelfSignedCert(url, { headers }),
    1,  // Only retry once for this endpoint
    1000,
    (error) => {
      // Don't retry on authentication errors (401)
      if (error && typeof error === 'object' && 'status' in error && error.status === 401) {
        console.log('Not retrying due to authentication error (401)');
        return false;
      }
      
      // Don't retry on redirect loops
      if (error && typeof error === 'object' && 'status' in error && error.status === 307) {
        console.log('Not retrying due to redirect (307)');
        return false;
      }
      
      // Only retry on server errors (5xx)
      return error && typeof error === 'object' && 'status' in error && 
             error.status >= 500 && error.status < 600;
    }
  );
  console.log(`API response status: ${response.status} ${response.statusText}`);
  
  // Handle 401 Unauthorized errors specifically
  if (response.status === 401) {
    console.error('Authentication error (401 Unauthorized)');
    
    // Try to refresh the token
    try {
      console.log('Attempting to refresh the token after 401 error');
      const { data, error } = await supabase.auth.refreshSession();
      if (error) {
        console.error('Failed to refresh token:', error);
      } else if (data.session) {
        console.log('Token refreshed successfully, user should retry the operation');
      }
    } catch (refreshError) {
      console.error('Error refreshing token:', refreshError);
    }
    
    const emptyResponse: SearchListResponse = {
      items: [],
      total: 0,
      offset: options?.offset || 0,
      limit: options?.limit || 10
    };
    return emptyResponse;
  }
  
  if (!response.ok) {
    console.error('Error response from API:', response.status, response.statusText);
    return handleApiError(response)
  }
  
  // Parse the response with error handling
  let data: any;
  try {
    data = await response.json()
    console.log('Successfully parsed API response:', {
      itemsCount: data?.items?.length || 0,
      total: data?.total,
      hasItems: Array.isArray(data?.items)
    });
  } catch (parseError) {
    console.error('Error parsing JSON response:', parseError)
    throw new Error(`Failed to parse server response: ${parseError instanceof Error ? parseError.message : String(parseError)}`)
  }
  
  // Validate the response structure
  if (!data || typeof data !== 'object') {
    console.error('Invalid response format:', data)
    throw new Error('Server returned an invalid response format')
  }
  
  if (!Array.isArray(data.items)) {
    console.error('Response missing items array:', data)
    // Try to recover by creating a default structure
    data = {
      items: [],
      total: 0,
      offset: options?.offset || 0,
      limit: options?.limit || 10,
      ...data // Keep any other fields that might be present
    }
  }
  
  // Cache the response
  researchCache.setSessionList(data, options);
  
  return data
}

/**
 * Fetch a single research session by ID
 * @param sessionId The ID of the session to fetch
 * @returns The research session
 */
export async function fetchSession(sessionId: string): Promise<ResearchSession> {
  try {
    // Check cache first
    const cachedSession = researchCache.getSession(sessionId);
    if (cachedSession) {
      return cachedSession;
    }

    const headers = await getAuthHeader()
    const response = await withRetry(() => fetchWithSelfSignedCert(`/api/research/searches/${sessionId}/`, { headers }))
    
    if (!response.ok) return handleApiError(response)
    
    // Parse the response with error handling
    let data: any;
    try {
      data = await response.json()
    } catch (parseError) {
      console.error(`Error parsing JSON response for session ${sessionId}:`, parseError)
      throw new Error(`Failed to parse server response: ${parseError instanceof Error ? parseError.message : String(parseError)}`)
    }
    
    // Validate the response structure
    if (!data || typeof data !== 'object') {
      console.error('Invalid response format:', data)
      throw new Error('Server returned an invalid response format')
    }
    
    if (!data.id) {
      console.error('Response missing session ID:', data)
      throw new Error('Server returned an invalid session format')
    }
    
    // Cache the response
    researchCache.setSession(data);
    
    return data
  } catch (error) {
    console.error(`Error in fetchSession for session ${sessionId}:`, error);
    
    // If the error is already an ApiError, rethrow it
    if (error && (error as any).code) {
      throw error;
    }
    
    // Otherwise, format it and throw
    throw formatApiError(error, `Failed to fetch research session ${sessionId}`);
  }
}

/**
 * Create a new research session
 * @param query The query to research
 * @param searchParams Optional parameters for the search
 * @returns The newly created research session
 */
export async function createNewSession(query: string, searchParams?: SearchParams): Promise<ResearchSession> {
  const headers = await getAuthHeader()
  const response = await withRetry(() => fetchWithSelfSignedCert('/api/research/searches/', {
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
    () => fetchWithSelfSignedCert(`/api/research/searches/${sessionId}/continue/`, {
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
  const response = await withRetry(() => fetchWithSelfSignedCert(`/api/research/searches/${sessionId}/`, {
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
  const response = await withRetry(() => fetchWithSelfSignedCert(`/api/research/searches/${sessionId}/`, {
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
  const response = await withRetry(() => fetchWithSelfSignedCert(`/api/research/messages/${messageId}`, { headers }))
  
  if (!response.ok) return handleApiError(response)
  const data = await response.json()
  
  // Cache the response
  researchCache.setMessage(data);
  
  return data
}

/**
 * Fetch messages for a search
 * @param searchId The ID of the search to fetch messages for
 * @param options Options for filtering and pagination
 * @returns A list of messages
 */
export async function fetchMessagesForSearch(
  searchId: string,
  options?: {
    limit?: number
    offset?: number;
  } | null
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
    fetchWithSelfSignedCert(`/api/research/searches/${searchId}/messages/${queryString}`, { headers })
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
  const response = await withRetry(() => fetchWithSelfSignedCert(`/api/research/messages/${messageId}`, {
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
  
  const response = await withRetry(() => fetchWithSelfSignedCert(`/api/research/messages/${messageId}`, {
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
  const response = await withRetry(() => fetchWithSelfSignedCert(`/api/research/messages/${messageId}/forward`, {
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
 * @param searchId The ID of the search to connect to
 * @param onMessage Callback function for handling incoming messages
 * @param onError Callback function for handling errors
 * @param onConnectionChange Callback function for handling connection state changes
 * @returns A WebSocketConnection object with methods to interact with the connection
 */
export async function connectToMessageUpdates(
  searchId: string,
  onMessage: (message: WebSocketMessage) => void,
  onError: (error: any) => void,
  onConnectionChange: (connected: boolean) => void
): Promise<WebSocketConnection> {
  // Get the auth token with retry logic
  let token: string | null = null;
  let tokenRetryCount = 0;
  const maxTokenRetries = 3;
  
  while (!token && tokenRetryCount < maxTokenRetries) {
    try {
      console.log(`Attempting to get auth token (attempt ${tokenRetryCount + 1}/${maxTokenRetries})`);
      const { data, error } = await supabase.auth.getSession();
      
      if (error) {
        console.error('Error getting auth session:', error);
        throw error;
      }
      
      token = data?.session?.access_token || null;
      
      if (!token) {
        // If token is still null after getSession, try refreshing the session
        console.log('No token found, attempting to refresh session...');
        const { data: refreshData, error: refreshError } = await supabase.auth.refreshSession();
        
        if (refreshError) {
          console.error('Error refreshing session:', refreshError);
          throw refreshError;
        }
        
        token = refreshData?.session?.access_token || null;
      }
      
      if (!token) {
        console.warn('Failed to get token, will retry...');
        tokenRetryCount++;
        // Wait before retrying with exponential backoff
        await new Promise(resolve => setTimeout(resolve, 1000 * Math.pow(2, tokenRetryCount)));
      }
    } catch (error) {
      console.error('Error retrieving auth token:', error);
      tokenRetryCount++;
      // Wait before retrying
      await new Promise(resolve => setTimeout(resolve, 1000 * Math.pow(2, tokenRetryCount)));
    }
  }
  
  if (!token) {
    const error = new Error('Failed to retrieve authentication token after multiple attempts');
    console.error(error);
    onError(error);
    onConnectionChange(false); 
    throw error;
  }
  
  console.log('Successfully retrieved auth token');
  
  // Create WebSocket connection
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  let wsHost: string;
  
  try {
    wsHost = process.env.NEXT_PUBLIC_API_URL ? 
      new URL(process.env.NEXT_PUBLIC_API_URL).host : 
      window.location.host;
  } catch (error) {
    console.error('Error parsing API URL:', error);
    wsHost = window.location.host; // Fallback to current host
  }
  
  const wsUrl = `${wsProtocol}//${wsHost}/api/research/messages/ws/${searchId}?token=${encodeURIComponent(token)}`;
  
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
      
      // Notify about connection state change
      onConnectionChange(true);
      
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
      
      onConnectionChange(false);
      
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
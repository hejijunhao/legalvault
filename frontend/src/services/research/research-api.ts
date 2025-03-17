// src/services/research/research-api.ts

import { supabase } from '@/lib/supabase'
import { Message, ResearchSession, SearchParams, QueryStatus, QueryCategory, QueryType, Citation } from '@/contexts/research/research-context'

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

// Helper function to handle API errors
async function handleApiError(response: Response): Promise<never> {
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
  
  // Add specific handling for common error codes
  switch (response.status) {
    case 401:
      apiError.message = 'Your session has expired. Please log in again.'
      apiError.code = 'AUTH_REQUIRED'
      break
    case 403:
      apiError.message = 'You do not have permission to perform this action.'
      apiError.code = 'PERMISSION_DENIED'
      break
    case 404:
      apiError.message = 'The requested resource was not found.'
      apiError.code = 'NOT_FOUND'
      break
    case 409:
      apiError.message = 'This operation conflicts with the current state.'
      apiError.code = 'CONFLICT'
      break
    case 429:
      apiError.message = 'Too many requests. Please try again later.'
      apiError.code = 'RATE_LIMITED'
      
      // Check for Retry-After header (common in rate limiting responses)
      const retryAfter = response.headers.get('Retry-After')
      if (retryAfter) {
        apiError.retryAfter = parseInt(retryAfter, 10)
        if (!isNaN(apiError.retryAfter)) {
          apiError.message = `Rate limit exceeded. Please try again in ${apiError.retryAfter} seconds.`
        }
      }
      
      // Special handling for Perplexity Sonar API rate limiting
      if (errorDetails?.error?.includes?.('rate limit') || 
          errorDetails?.message?.toLowerCase?.().includes('rate limit') ||
          errorDetails?.detail?.toLowerCase?.().includes('rate limit') ||
          errorDetails?.message?.toLowerCase?.().includes('perplexity') ||
          errorDetails?.detail?.toLowerCase?.().includes('perplexity') ||
          errorDetails?.message?.toLowerCase?.().includes('sonar') ||
          errorDetails?.detail?.toLowerCase?.().includes('sonar')) {
        apiError.code = 'PERPLEXITY_RATE_LIMITED'
        apiError.message = 'Perplexity API rate limit reached. Please try again later.'
      }
      break
    case 500:
    case 502:
    case 503:
    case 504:
      apiError.message = 'A server error occurred. Please try again later.'
      apiError.code = 'SERVER_ERROR'
      break
  }
  
  // If we have more specific error details from the API, use those instead
  if (errorDetails?.detail || errorDetails?.message) {
    // But keep our specific code if we assigned one
    const code = apiError.code
    apiError.message = errorDetails.detail || errorDetails.message
    if (code) apiError.code = code
  }
  
  throw apiError
}

export async function fetchSessions(options?: {
  featuredOnly?: boolean
  status?: QueryStatus
  limit?: number
  offset?: number
}): Promise<SearchListResponse> {
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
  return await response.json()
}

export async function fetchSession(sessionId: string): Promise<ResearchSession> {
  const headers = await getAuthHeader()
  const response = await withRetry(() => fetch(`/api/research/searches/${sessionId}`, { headers }))
  
  if (!response.ok) return handleApiError(response)
  return await response.json()
}

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
  return await response.json()
}

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
  return await response.json()
}

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
  return await response.json()
}

export async function deleteSession(sessionId: string): Promise<void> {
  const headers = await getAuthHeader()
  const response = await withRetry(() => fetch(`/api/research/searches/${sessionId}`, {
    method: 'DELETE',
    headers
  }))
  
  if (!response.ok) return handleApiError(response)
}

// Message-specific API functions

export interface MessageListResponse {
  items: Message[]
  total: number
  offset: number
  limit: number
}

export async function fetchMessage(messageId: string): Promise<Message> {
  const headers = await getAuthHeader()
  const response = await withRetry(() => fetch(`/api/research/messages/${messageId}`, { headers }))
  
  if (!response.ok) return handleApiError(response)
  return await response.json()
}

export async function fetchMessagesForSearch(
  searchId: string,
  options?: {
    limit?: number
    offset?: number
  }
): Promise<MessageListResponse> {
  const headers = await getAuthHeader()
  
  // Build query parameters
  const params = new URLSearchParams()
  if (options?.limit) params.append('limit', options.limit.toString())
  if (options?.offset) params.append('offset', options.offset.toString())
  
  const queryString = params.toString() ? `?${params.toString()}` : ''
  const response = await withRetry(() => 
    fetch(`/api/research/messages/search/${searchId}${queryString}`, { headers })
  )
  
  if (!response.ok) return handleApiError(response)
  return await response.json()
}

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
  return await response.json()
}

export async function deleteMessage(messageId: string): Promise<void> {
  const headers = await getAuthHeader()
  const response = await withRetry(() => fetch(`/api/research/messages/${messageId}`, {
    method: 'DELETE',
    headers
  }))
  
  if (!response.ok) return handleApiError(response)
}

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
  
  console.log(`Connecting to WebSocket at ${wsUrl}`);
  const socket = new WebSocket(wsUrl);
  let isConnected = false;
  
  // Connection opened
  socket.addEventListener('open', () => {
    console.log('WebSocket connection established');
    isConnected = true;
    
    // Subscribe to all message types
    socket.send(JSON.stringify({
      command: 'subscribe',
      message_types: ['user', 'assistant']
    }));
  });
  
  // Listen for messages
  socket.addEventListener('message', (event) => {
    try {
      const message = JSON.parse(event.data) as WebSocketMessage;
      console.log('Received WebSocket message:', message);
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
    if (onClose) onClose();
  });
  
  // Return connection interface
  return {
    disconnect: () => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.close();
      }
    },
    send: (data: any) => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify(data));
      } else {
        console.warn('Cannot send message: WebSocket is not open');
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
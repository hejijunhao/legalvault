// src/services/research/research-api.ts

import { supabase } from '@/lib/supabase'
import { Message, ResearchSession, SearchParams, QueryStatus, QueryCategory, QueryType } from '@/contexts/research/research-context'

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
  const response = await fetch(`/api/research/searches${queryString}`, { headers })
  
  if (!response.ok) return handleApiError(response)
  return await response.json()
}

export async function fetchSession(sessionId: string): Promise<ResearchSession> {
  const headers = await getAuthHeader()
  const response = await fetch(`/api/research/searches/${sessionId}`, { headers })
  
  if (!response.ok) return handleApiError(response)
  return await response.json()
}

export async function createNewSession(query: string, searchParams?: SearchParams): Promise<ResearchSession> {
  const headers = await getAuthHeader()
  const response = await fetch('/api/research/searches', {
    method: 'POST',
    headers,
    body: JSON.stringify({ 
      query,
      search_params: searchParams || {}
    })
  })
  
  if (!response.ok) return handleApiError(response)
  return await response.json()
}

export async function sendSessionMessage(sessionId: string, content: string): Promise<ResearchSession> {
  const headers = await getAuthHeader()
  const response = await fetch(`/api/research/searches/${sessionId}/continue`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ follow_up_query: content })
  })
  
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
  const response = await fetch(`/api/research/searches/${sessionId}`, {
    method: 'PATCH',
    headers,
    body: JSON.stringify(updates)
  })
  
  if (!response.ok) return handleApiError(response)
  return await response.json()
}

export async function deleteSession(sessionId: string): Promise<void> {
  const headers = await getAuthHeader()
  const response = await fetch(`/api/research/searches/${sessionId}`, {
    method: 'DELETE',
    headers
  })
  
  if (!response.ok) return handleApiError(response)
}
// src/lib/api-client.ts
// Centralized API client with auth, retry, and error handling

import { supabase } from './supabase'

// API Error class with structured error info
export class ApiError extends Error {
  status?: number
  statusText?: string
  code?: string
  details?: string

  constructor(message: string, options?: {
    status?: number
    statusText?: string
    code?: string
    details?: string
  }) {
    super(message)
    this.name = 'ApiError'
    if (options) {
      this.status = options.status
      this.statusText = options.statusText
      this.code = options.code
      this.details = options.details
    }
  }

  static fromResponse(status: number, body?: any): ApiError {
    let message = 'An unexpected error occurred'
    let code: string | undefined

    // Map status codes to user-friendly messages
    switch (status) {
      case 400:
        message = body?.detail || 'Invalid request'
        break
      case 401:
        message = 'Your session has expired. Please log in again.'
        code = 'AUTH_EXPIRED'
        break
      case 403:
        message = 'You do not have permission to perform this action.'
        code = 'FORBIDDEN'
        break
      case 404:
        message = 'The requested resource was not found.'
        code = 'NOT_FOUND'
        break
      case 429:
        message = 'Rate limit exceeded. Please try again later.'
        code = 'RATE_LIMITED'
        break
      default:
        if (status >= 500) {
          message = 'A server error occurred. Please try again later.'
          code = 'SERVER_ERROR'
        }
    }

    // Handle Perplexity API specific errors
    if (body?.message?.includes('Perplexity') || body?.detail?.includes('Perplexity')) {
      if (body.message?.includes('rate limit') || body.detail?.includes('rate limit')) {
        message = 'Research API rate limit exceeded. Please try again later.'
        code = 'PERPLEXITY_RATE_LIMITED'
      } else {
        message = 'Research API error. Please try again.'
        code = 'PERPLEXITY_ERROR'
      }
    }

    return new ApiError(message, {
      status,
      code,
      details: body?.detail,
    })
  }
}

interface RequestOptions extends Omit<RequestInit, 'body'> {
  body?: unknown
  params?: Record<string, string | number | boolean | undefined>
  retry?: number
  timeout?: number
}

// Get base URL
function getBaseUrl(): string {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL

  if (!apiUrl) {
    if (process.env.NODE_ENV === 'development') {
      return 'http://localhost:8000'
    }
    throw new Error('NEXT_PUBLIC_API_URL must be set')
  }

  // Normalize URL
  let url = apiUrl.endsWith('/') ? apiUrl.slice(0, -1) : apiUrl

  // Force HTTPS in production
  if (process.env.NODE_ENV !== 'development' && url.startsWith('http://')) {
    url = url.replace('http://', 'https://')
  }

  return url
}

// Get auth headers from Supabase session
async function getAuthHeaders(): Promise<Record<string, string>> {
  try {
    const { data: { session }, error } = await supabase.auth.getSession()

    if (error || !session) {
      // Try to refresh session
      const { data: refreshData } = await supabase.auth.refreshSession()
      if (refreshData.session) {
        return {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${refreshData.session.access_token}`,
        }
      }
      throw new ApiError('Authentication required', { status: 401, code: 'AUTH_REQUIRED' })
    }

    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${session.access_token}`,
    }
  } catch (error) {
    if (error instanceof ApiError) throw error
    throw new ApiError('Authentication failed', { status: 401, code: 'AUTH_FAILED' })
  }
}

// Sleep for retry backoff
function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms))
}

// Main request function
async function request<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const {
    method = 'GET',
    body,
    params,
    headers: customHeaders = {},
    retry = 3,
    timeout = 30000,
    ...fetchOptions
  } = options

  // Build URL with params
  const baseUrl = getBaseUrl()
  const url = new URL(endpoint.startsWith('/') ? endpoint : `/${endpoint}`, baseUrl)

  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        url.searchParams.set(key, String(value))
      }
    })
  }

  // Get auth headers
  const authHeaders = await getAuthHeaders()
  const headers = {
    ...authHeaders,
    ...(customHeaders as Record<string, string>),
  }

  // Prepare request options
  const requestInit: RequestInit = {
    method,
    headers,
    ...fetchOptions,
  }

  if (body && method !== 'GET') {
    requestInit.body = JSON.stringify(body)
  }

  // Retry loop
  for (let attempt = 0; attempt < retry; attempt++) {
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), timeout)

      const response = await fetch(url.toString(), {
        ...requestInit,
        signal: controller.signal,
      })

      clearTimeout(timeoutId)

      // Handle redirects
      if (response.status === 307 || response.status === 308) {
        const redirectUrl = response.headers.get('Location')
        if (redirectUrl) {
          return request<T>(redirectUrl, options)
        }
      }

      // Handle errors
      if (!response.ok) {
        let errorBody: any
        try {
          const contentType = response.headers.get('content-type')
          if (contentType?.includes('application/json')) {
            errorBody = await response.json()
          } else {
            errorBody = { detail: await response.text() }
          }
        } catch {
          errorBody = {}
        }

        throw ApiError.fromResponse(response.status, errorBody)
      }

      // Parse response
      const contentType = response.headers.get('content-type')
      if (contentType?.includes('application/json')) {
        return await response.json()
      }

      return await response.text() as unknown as T
    } catch (error) {
      // Don't retry on auth errors or client errors
      if (error instanceof ApiError) {
        if (error.status && error.status < 500 && error.status !== 429) {
          throw error
        }
      }

      // Last attempt - throw the error
      if (attempt === retry - 1) {
        if (error instanceof ApiError) throw error
        throw new ApiError(
          error instanceof Error ? error.message : 'Request failed',
          { code: 'REQUEST_FAILED' }
        )
      }

      // Wait before retry with exponential backoff
      await sleep(Math.pow(2, attempt) * 1000)
    }
  }

  throw new ApiError('Request failed after retries', { code: 'RETRY_EXHAUSTED' })
}

// API client with convenience methods
export const apiClient = {
  get<T>(endpoint: string, params?: Record<string, string | number | boolean | undefined>) {
    return request<T>(endpoint, { method: 'GET', params })
  },

  post<T>(endpoint: string, body?: unknown) {
    return request<T>(endpoint, { method: 'POST', body })
  },

  put<T>(endpoint: string, body?: unknown) {
    return request<T>(endpoint, { method: 'PUT', body })
  },

  patch<T>(endpoint: string, body?: unknown) {
    return request<T>(endpoint, { method: 'PATCH', body })
  },

  delete<T>(endpoint: string) {
    return request<T>(endpoint, { method: 'DELETE' })
  },

  // Raw request for custom options
  request,
}

export default apiClient

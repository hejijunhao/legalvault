// src/services/research/research-api-core.ts
// Legacy utilities - prefer using @/lib/api-client directly
//
// These functions are kept for backwards compatibility.
// New code should import from @/lib/api-client instead.

import { supabase } from '@/lib/supabase'
import { ApiError } from '@/lib/api-client'

// Re-export ApiError from centralized location
export { ApiError } from '@/lib/api-client'

/**
 * @deprecated Use apiClient from @/lib/api-client instead
 * Get the base URL for API requests
 */
export function getApiBaseUrl(): string {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL

  if (!apiUrl) {
    if (process.env.NODE_ENV === 'development') {
      return 'http://localhost:8000'
    }
    throw new Error('NEXT_PUBLIC_API_URL must be set in production')
  }

  let url = apiUrl.endsWith('/') ? apiUrl.slice(0, -1) : apiUrl

  if (process.env.NODE_ENV !== 'development' && url.startsWith('http://')) {
    url = url.replace('http://', 'https://')
  }

  return url
}

/**
 * @deprecated Use apiClient from @/lib/api-client instead - handles auth automatically
 * Get authentication headers for API requests
 */
export async function getAuthHeader(): Promise<Record<string, string>> {
  const { data: { session }, error } = await supabase.auth.getSession()

  if (error || !session) {
    const { data: refreshData } = await supabase.auth.refreshSession()
    if (refreshData.session) {
      return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${refreshData.session.access_token}`,
      }
    }
    throw new Error('Authentication required')
  }

  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${session.access_token}`,
  }
}

/**
 * @deprecated Use apiClient from @/lib/api-client instead - handles fetch automatically
 */
export async function fetchWithSelfSignedCert(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  let fullUrl = url

  if (!url.startsWith('http')) {
    const baseUrl = getApiBaseUrl()
    const separator = baseUrl.endsWith('/') || url.startsWith('/') ? '' : '/'
    fullUrl = `${baseUrl}${separator}${url}`
  }

  if (process.env.NODE_ENV !== 'development' && fullUrl.startsWith('http://')) {
    fullUrl = fullUrl.replace('http://', 'https://')
  }

  const headers = new Headers(options.headers || {})
  if (!headers.has('Accept')) headers.set('Accept', 'application/json')

  return fetch(fullUrl, { ...options, headers })
}

/**
 * @deprecated Use apiClient from @/lib/api-client instead - has built-in retry
 */
export async function withRetry<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  shouldRetry: (error: unknown, retryCount: number) => boolean = () => true
): Promise<T> {
  let retryCount = 0

  while (true) {
    try {
      return await fn()
    } catch (error) {
      retryCount++
      if (retryCount >= maxRetries || !shouldRetry(error, retryCount)) {
        throw error
      }
      const delay = Math.pow(2, retryCount) * 1000
      await new Promise(resolve => setTimeout(resolve, delay))
    }
  }
}

/**
 * @deprecated Use ApiError from @/lib/api-client instead
 */
export function formatApiError(error: unknown, defaultMessage?: string): Error {
  if (error instanceof ApiError) return error
  if (error instanceof Error) {
    return new ApiError(error.message || defaultMessage || 'An unexpected error occurred')
  }
  return new ApiError(defaultMessage || 'An unexpected error occurred')
}

/**
 * @deprecated Use apiClient from @/lib/api-client instead - handles errors automatically
 */
export async function handleApiError(response: Response): Promise<never> {
  let message = 'An unexpected error occurred'
  let details: string | undefined

  try {
    const contentType = response.headers.get('content-type')
    if (contentType?.includes('application/json')) {
      const json = await response.json()
      details = json.detail
    } else {
      details = await response.text()
    }
  } catch {
    // Ignore parse errors
  }

  switch (response.status) {
    case 400:
      message = details || 'Invalid request'
      break
    case 401:
      message = 'Your session has expired. Please log in again.'
      break
    case 403:
      message = 'You do not have permission to perform this action.'
      break
    case 404:
      message = 'The requested resource was not found.'
      break
    case 429:
      message = 'Rate limit exceeded. Please try again later.'
      break
    default:
      if (response.status >= 500) {
        message = 'A server error occurred. Please try again later.'
      }
  }

  throw new ApiError(message, {
    status: response.status,
    statusText: response.statusText,
    details,
  })
}

/**
 * Schedule a cache clear after a specified time
 */
export function scheduleCacheClear(
  clearFn: () => void,
  delay: number = 5 * 60 * 1000
): () => void {
  const timeoutId = setTimeout(clearFn, delay)
  return () => clearTimeout(timeoutId)
}

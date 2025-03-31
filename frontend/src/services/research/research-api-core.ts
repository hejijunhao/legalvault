// src/services/research/research-api-core.ts


import { supabase } from "@/lib/supabase";
import { ApiError } from "./research-api-types";

/**
 * Get the base URL for API requests with better environment handling
 */
export function getApiBaseUrl(): string {
  // In development, default to localhost:8000 if no API URL is provided
  if (process.env.NODE_ENV === 'development') {
    return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  }
  
  // In production, use the provided API URL or current origin
  const apiUrl = process.env.NEXT_PUBLIC_API_URL;
  if (apiUrl) {
    // Ensure the URL doesn't have a trailing slash
    return apiUrl.endsWith('/') ? apiUrl.slice(0, -1) : apiUrl;
  }
  
  // Fallback to current origin (should only happen in production)
  const origin = window.location.origin;
  console.warn(`No NEXT_PUBLIC_API_URL provided, falling back to current origin: ${origin}`);
  return origin;
}

/**
 * Get authentication headers for API requests
 */
export async function getAuthHeader(): Promise<Record<string, string>> {
  try {
    // First try to get the current session
    const { data: { session }, error: sessionError } = await supabase.auth.getSession();
    
    if (sessionError) {
      console.error('Error getting auth session:', sessionError);
      throw new Error('Authentication failed');
    }
    
    if (!session) {
      // If no session, try to get the token from localStorage as fallback
      const token = localStorage.getItem('auth_token');
      if (!token) {
        throw new Error('Authentication required');
      }
      
      // Try to refresh the session using the token
      const { data: { session: refreshedSession }, error: refreshError } = 
        await supabase.auth.refreshSession();
        
      if (refreshError || !refreshedSession) {
        console.error('Failed to refresh session:', refreshError);
        throw new Error('Authentication required');
      }
      
      return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${refreshedSession.access_token}`
      };
    }
    
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${session.access_token}`
    };
  } catch (error) {
    console.error('Authentication error:', error);
    throw new Error('Authentication required');
  }
}

/**
 * Fetch with support for self-signed certificates
 * @param url The URL to fetch
 * @param options Fetch options
 * @returns A fetch response
 */
export async function fetchWithSelfSignedCert(
  url: string, 
  options: RequestInit = {}
): Promise<Response> {
  // Normalize URL to prevent trailing slash issues
  const normalizedUrl = url.endsWith('/') && !url.endsWith('//') ? url.slice(0, -1) : url;
  
  // Ensure URL is absolute
  let fullUrl = normalizedUrl;
  if (!normalizedUrl.startsWith('http')) {
    const baseUrl = getApiBaseUrl();
    // Ensure we don't have double slashes when joining paths
    const separator = baseUrl.endsWith('/') && normalizedUrl.startsWith('/') ? '' : 
                     (!baseUrl.endsWith('/') && !normalizedUrl.startsWith('/')) ? '/' : '';
    fullUrl = `${baseUrl}${separator}${normalizedUrl}`;
  }
  
  // Ensure headers are properly initialized
  const headers = new Headers(options.headers || {});
  
  // Set default headers if not already present
  if (!headers.has('Accept')) {
    headers.set('Accept', 'application/json');
  }
  
  if (!headers.has('Content-Type') && options.method !== 'GET' && options.body) {
    headers.set('Content-Type', 'application/json');
  }
  
  // Log request (without sensitive data)
  console.log(`API Request: ${options.method || 'GET'} ${fullUrl.replace(/token=([^&]+)/, 'token=***')}`);
  
  try {
    const response = await fetch(fullUrl, {
      ...options,
      headers
    });
    
    // Log response status
    console.log(`API Response: ${response.status} ${response.statusText} for ${options.method || 'GET'} ${fullUrl.replace(/token=([^&]+)/, 'token=***')}`);
    
    // Handle redirects that might be caused by trailing slash issues
    if (response.status === 307 || response.status === 308) {
      console.warn(`Received redirect (${response.status}) for URL: ${fullUrl}`);
      const redirectUrl = response.headers.get('Location');
      if (redirectUrl) {
        console.log(`Following redirect to: ${redirectUrl.replace(/token=([^&]+)/, 'token=***')}`);
        return fetchWithSelfSignedCert(redirectUrl, options);
      }
    }
    
    return response;
  } catch (error) {
    console.error(`API Request failed for ${options.method || 'GET'} ${fullUrl.replace(/token=([^&]+)/, 'token=***')}:`, error);
    throw error;
  }
}

/**
 * Retry a function with exponential backoff
 * @param fn The function to retry
 * @param maxRetries Maximum number of retries
 * @param shouldRetry Function to determine if a retry should be attempted
 * @returns The result of the function
 */
export async function withRetry<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  shouldRetry: (error: any, retryCount: number) => boolean = () => true
): Promise<T> {
  let retryCount = 0;
  
  while (true) {
    try {
      return await fn();
    } catch (error) {
      retryCount++;
      
      if (retryCount >= maxRetries || !shouldRetry(error, retryCount)) {
        throw error;
      }
      
      // Exponential backoff
      const delay = Math.pow(2, retryCount) * 1000;
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
}

/**
 * Format an API error
 * @param error The error to format
 * @param defaultMessage Optional default message to use if no specific message is available
 * @returns A formatted API error
 */
export function formatApiError(error: any, defaultMessage?: string): ApiError {
  const formattedError: ApiError = new Error(
    error.message || defaultMessage || 'An unexpected error occurred'
  ) as ApiError;
  
  // Copy properties from the original error
  if (error.status) formattedError.status = error.status;
  if (error.statusText) formattedError.statusText = error.statusText;
  if (error.code) formattedError.code = error.code;
  if (error.details) formattedError.details = error.details;
  
  formattedError.originalError = error;
  
  // Format based on status code
  if (formattedError.status !== undefined) {
    if (formattedError.status === 401) {
      formattedError.message = 'Your session has expired. Please log in again.';
    } else if (formattedError.status === 403) {
      formattedError.message = 'You do not have permission to perform this action.';
    } else if (formattedError.status === 404) {
      formattedError.message = 'The requested resource was not found.';
    } else if (formattedError.status === 429) {
      formattedError.message = 'Rate limit exceeded. Please try again later.';
      formattedError.code = 'RATE_LIMITED';
    } else if (formattedError.status >= 500) {
      formattedError.message = 'A server error occurred. Please try again later.';
    }
  }
  
  // Special handling for Perplexity API errors
  if (error.message?.includes('Perplexity API') || error.details?.includes('Perplexity API')) {
    if (error.message?.includes('rate limit') || error.details?.includes('rate limit')) {
      formattedError.message = 'Perplexity API rate limit exceeded. Please try again later.';
      formattedError.code = 'PERPLEXITY_RATE_LIMITED';
    } else {
      formattedError.message = 'An error occurred with the Perplexity API. Please try again later.';
      formattedError.code = 'PERPLEXITY_ERROR';
    }
  }
  
  return formattedError;
}

/**
 * Handle an API error response
 * @param response The response to handle
 * @returns Never returns, always throws an error
 */
export async function handleApiError(response: Response): Promise<never> {
  let errorData: any = {
    status: response.status,
    statusText: response.statusText
  };
  
  try {
    // Try to parse error details from response
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      const json = await response.json();
      errorData = { ...errorData, ...json };
    } else {
      errorData.details = await response.text();
    }
  } catch (e) {
    console.error('Error parsing error response:', e);
  }
  
  throw formatApiError(errorData);
}

/**
 * Schedule a cache clear after a specified time
 * @param clearFn The function to clear the cache
 * @param delay The delay in milliseconds
 * @returns A function to cancel the scheduled clear
 */
export function scheduleCacheClear(
  clearFn: () => void, 
  delay: number = 5 * 60 * 1000
): () => void {
  const timeoutId = setTimeout(clearFn, delay);
  return () => clearTimeout(timeoutId);
}
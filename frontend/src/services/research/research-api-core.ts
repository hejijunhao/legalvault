// src/services/research/research-api-core.ts

import { supabase } from "@/lib/supabase";
import { ApiError } from "./research-api-types";

/**
 * Get the base URL for API requests with better environment handling
 */
export function getApiBaseUrl(): string {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL;
  
  if (!apiUrl) {
    console.error('NEXT_PUBLIC_API_URL is not set.');
    if (process.env.NODE_ENV === 'development') {
      console.warn('Falling back to http://localhost:8000 for development');
      return 'http://localhost:8000';
    }
    throw new Error('NEXT_PUBLIC_API_URL must be set in production');
  }
  
  const normalizedUrl = apiUrl.endsWith('/') ? apiUrl.slice(0, -1) : apiUrl;
  if (process.env.NODE_ENV !== 'development' && !normalizedUrl.startsWith('https://')) {
    console.warn(`Forcing HTTPS for API URL: ${normalizedUrl}`);
    return `https://${normalizedUrl.replace(/^http:\/\//, '')}`;
  }
  
  console.log('API Base URL:', normalizedUrl);
  return normalizedUrl;
}

/**
 * Get authentication headers for API requests
 */
export async function getAuthHeader(): Promise<Record<string, string>> {
  try {
    const { data: { session }, error: sessionError } = await supabase.auth.getSession();
    
    if (sessionError) {
      console.error('Error getting auth session:', sessionError);
      throw new Error('Authentication failed');
    }
    
    if (!session) {
      const token = localStorage.getItem('auth_token');
      if (!token) {
        throw new Error('Authentication required');
      }
      
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
 */
export async function fetchWithSelfSignedCert(
  url: string, 
  options: RequestInit = {}
): Promise<Response> {
  const normalizedUrl = url.endsWith('/') && !url.endsWith('//') ? url.slice(0, -1) : url;
  let fullUrl = normalizedUrl;
  
  if (!normalizedUrl.startsWith('http')) {
    const baseUrl = getApiBaseUrl();
    const separator = baseUrl.endsWith('/') && normalizedUrl.startsWith('/') ? '' : 
                     (!baseUrl.endsWith('/') && !normalizedUrl.startsWith('/')) ? '/' : '';
    fullUrl = `${baseUrl}${separator}${normalizedUrl}`;
  }
  
  // Force HTTPS in production
  if (process.env.NODE_ENV !== 'development' && fullUrl.startsWith('http://')) {
    console.warn(`Converting HTTP to HTTPS for URL: ${fullUrl}`);
    fullUrl = `https://${fullUrl.replace(/^http:\/\//, '')}`;
  }
  
  console.log(`Final Fetch URL: ${fullUrl}`);
  
  const headers = new Headers(options.headers || {});
  if (!headers.has('Accept')) headers.set('Accept', 'application/json');
  if (!headers.has('Content-Type') && options.method !== 'GET' && options.body) {
    headers.set('Content-Type', 'application/json');
  }
  
  try {
    const response = await fetch(fullUrl, {
      ...options,
      headers
    });
    
    console.log(`Response: ${response.status} ${response.statusText} for ${options.method || 'GET'} ${fullUrl}`);
    
    if (response.status === 307 || response.status === 308) {
      console.warn(`Redirect (${response.status}) for URL: ${fullUrl}`);
      const redirectUrl = response.headers.get('Location');
      if (redirectUrl) {
        console.log(`Following redirect to: ${redirectUrl}`);
        return fetchWithSelfSignedCert(redirectUrl, options);
      }
    }
    
    return response;
  } catch (error) {
    console.error(`Fetch failed for ${options.method || 'GET'} ${fullUrl}:`, error);
    throw error;
  }
}

/**
 * Retry a function with exponential backoff
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
      
      const delay = Math.pow(2, retryCount) * 1000;
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
}

/**
 * Format an API error
 */
export function formatApiError(error: any, defaultMessage?: string): ApiError {
  const formattedError: ApiError = new Error(
    error.message || defaultMessage || 'An unexpected error occurred'
  ) as ApiError;
  
  if (error.status) formattedError.status = error.status;
  if (error.statusText) formattedError.statusText = error.statusText;
  if (error.code) formattedError.code = error.code;
  if (error.details) formattedError.details = error.details;
  
  formattedError.originalError = error;
  
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
 */
export async function handleApiError(response: Response): Promise<never> {
  let errorData: any = {
    status: response.status,
    statusText: response.statusText
  };
  
  try {
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
  
  let message = 'An unexpected error occurred';
  if (errorData.status === 400) {
    message = `Validation error: ${errorData.detail || 'Invalid request'}`;
  } else if (errorData.status === 404) {
    message = 'Resource not found';
  } else if (errorData.status === 500) {
    message = 'A server error occurred. Please try again later.';
  } else if (errorData.status === 503) {
    message = 'Service unavailable. Please try again later.';
  }
  
  throw new Error(message);
}

/**
 * Schedule a cache clear after a specified time
 */
export function scheduleCacheClear(
  clearFn: () => void, 
  delay: number = 5 * 60 * 1000
): () => void {
  const timeoutId = setTimeout(clearFn, delay);
  return () => clearTimeout(timeoutId);
}
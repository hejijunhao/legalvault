// src/services/research/research-api-core.ts

import { supabase } from "@/lib/supabase";
import { ApiError } from "./research-api-types";

/**
 * Get the base URL for API requests
 */
export function getApiBaseUrl(): string {
  // Use environment variable if available, otherwise use current origin
  return process.env.NEXT_PUBLIC_API_URL || window.location.origin;
}

/**
 * Get authentication headers for API requests
 */
export async function getAuthHeader(): Promise<Record<string, string>> {
  const { data, error } = await supabase.auth.getSession();
  
  if (error || !data.session) {
    console.error('Error getting auth session:', error);
    throw new Error('Authentication required');
  }
  
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${data.session.access_token}`
  };
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
  // Ensure URL is absolute
  if (!url.startsWith('http')) {
    url = `${getApiBaseUrl()}${url}`;
  }
  
  return fetch(url, {
    ...options,
    // Add any special handling for self-signed certs if needed
  });
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
 * @returns A formatted API error
 */
export function formatApiError(error: any): ApiError {
  const formattedError: ApiError = new Error(
    error.message || 'An unexpected error occurred'
  ) as ApiError;
  
  // Copy properties from the original error
  if (error.status) formattedError.status = error.status;
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
// src/services/research/research-api-sessions.ts

import { 
  ResearchSession, 
  SearchListResponse, 
  SearchParams, 
  QueryCategory, 
  QueryStatus, 
  QueryType 
} from './research-api-types';
import { 
  getApiBaseUrl, 
  getAuthHeader, 
  fetchWithSelfSignedCert, 
  withRetry, 
  handleApiError,
  handleEncryptedFields 
} from './research-api-core';
import { researchCache } from './research-cache';

/**
 * Fetch a list of research sessions
 * @param options Options for filtering and pagination
 * @returns A list of research sessions
 */
export async function fetchSessions(
  options?: {
    featuredOnly?: boolean;
    status?: QueryStatus;
    limit?: number;
    offset?: number;
  } | null
): Promise<SearchListResponse> {
  // Check cache first
  const cachedData = researchCache.getSessionList(options);
  if (cachedData) {
    return cachedData;
  }
  
  const headers = await getAuthHeader();
  
  // Build query parameters
  const params = new URLSearchParams();
  if (options?.featuredOnly) params.append('featured', 'true');
  if (options?.status) params.append('status', options.status);
  if (options?.limit) params.append('limit', options.limit.toString());
  if (options?.offset) params.append('offset', options.offset.toString());
  
  const queryString = params.toString() ? `?${params.toString()}` : '';
  const url = `${getApiBaseUrl()}/research/searches${queryString}`;
  
  const response = await withRetry(() => fetchWithSelfSignedCert(url, { headers }));
  
  if (!response.ok) return handleApiError(response);
  const data = await response.json();
  
  // Cache the response
  researchCache.setSessionList(data, options);
  
  return data;
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
    return handleEncryptedFields(cachedSession);
  }
  
  const headers = await getAuthHeader();
  const response = await withRetry(() => 
    fetchWithSelfSignedCert(`${getApiBaseUrl()}/research/searches/${sessionId}/`, { headers })
  );
  
  if (!response.ok) return handleApiError(response);
  const data = await response.json();
  const processedData = handleEncryptedFields(data);
  researchCache.setSession(processedData);
  return processedData;
}

/**
 * Create a new research session
 * @param query The query to create a session for
 * @param searchParams Additional search parameters
 * @returns The created research session
 */
export async function createNewSession(
  query: string,
  searchParams?: SearchParams
): Promise<ResearchSession> {
  const headers = await getAuthHeader();
  const response = await withRetry(() => fetchWithSelfSignedCert(`${getApiBaseUrl()}/research/searches/`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      query,
      search_params: searchParams
    })
  }));
  
  if (!response.ok) return handleApiError(response);
  const data = await response.json();
  
  // Cache the new session
  researchCache.setSession(data);
  
  // Invalidate session lists as they're now outdated
  researchCache.clearSessionListCache();
  
  return data;
}

/**
 * Send a message to a research session
 * @param sessionId The ID of the session to send a message to
 * @param content The content of the message
 * @returns The updated research session
 */
export async function sendSessionMessage(
  sessionId: string,
  content: string
): Promise<ResearchSession> {
  const headers = await getAuthHeader();
  const response = await withRetry(
    () => fetchWithSelfSignedCert(`${getApiBaseUrl()}/research/searches/${sessionId}/messages/`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ content: { text: content } })
    }),
    3,
    (error, retryCount) => {
      // Retry on rate limit errors
      if (error && 
          ((error as { status: number }).status === 429 || 
           (error as { code: string }).code === 'PERPLEXITY_RATE_LIMITED' || 
           (error as { code: string }).code === 'RATE_LIMITED')) {
        return true;
      }
      
      return false;
    }
  );
  
  if (!response.ok) return handleApiError(response);
  const data = await response.json();
  
  // Cache the updated session
  researchCache.setSession(data);
  
  // Invalidate message lists for this session as they're now outdated
  researchCache.invalidateSearch(sessionId);
  
  return data;
}

/**
 * Continue a research session with a follow-up query
 * @param sessionId The ID of the session to continue
 * @param followUpQuery The follow-up query
 * @param options Additional options for the continuation
 * @returns The updated research session
 */
export async function continueSession(
  sessionId: string,
  followUpQuery: string,
  options?: {
    threadId?: string;
    previousMessages?: Array<{ role: string; content: any }>;
    searchParams?: SearchParams;
  }
): Promise<ResearchSession> {
  const headers = await getAuthHeader();
  const response = await withRetry(
    () => fetchWithSelfSignedCert(`${getApiBaseUrl()}/research/searches/${sessionId}/continue`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        follow_up_query: followUpQuery,
        thread_id: options?.threadId,
        previous_messages: options?.previousMessages,
        search_params: options?.searchParams
      })
    }),
    3,
    (error, retryCount) => {
      // Retry on rate limit errors
      if (error && 
          ((error as { status: number }).status === 429 || 
           (error as { code: string }).code === 'PERPLEXITY_RATE_LIMITED' || 
           (error as { code: string }).code === 'RATE_LIMITED')) {
        return true;
      }
      return false;
    }
  );

  if (!response.ok) return handleApiError(response);
  const data = await response.json();

  // Cache the updated session
  researchCache.setSession(data);

  // Invalidate message lists for this session as they're now outdated
  researchCache.invalidateSearch(sessionId);

  return data;
}

/**
 * Update the metadata of a research session
 * @param sessionId The ID of the session to update
 * @param updates The updates to apply
 * @returns The updated research session
 */
export async function updateSessionMetadata(
  sessionId: string, 
  updates: {
    title?: string;
    description?: string;
    is_featured?: boolean;
    tags?: string[];
    category?: QueryCategory;
    query_type?: QueryType;
    status?: QueryStatus;
  }
): Promise<ResearchSession> {
  const headers = await getAuthHeader();
  const response = await withRetry(() => fetchWithSelfSignedCert(`${getApiBaseUrl()}/research/searches/${sessionId}/`, {
    method: 'PATCH',
    headers,
    body: JSON.stringify(updates)
  }));
  
  if (!response.ok) return handleApiError(response);
  const data = await response.json();
  
  // Cache the updated session
  researchCache.setSession(data);
  
  // Invalidate session lists as they're now outdated
  researchCache.clearSessionListCache();
  
  return data;
}

/**
 * Delete a research session
 * @param sessionId The ID of the session to delete
 */
export async function deleteSession(sessionId: string): Promise<void> {
  const headers = await getAuthHeader();
  const response = await withRetry(() => fetchWithSelfSignedCert(`${getApiBaseUrl()}/research/searches/${sessionId}/`, {
    method: 'DELETE',
    headers
  }));
  
  if (!response.ok) return handleApiError(response);
  
  // Invalidate cache for this session
  researchCache.invalidateSearch(sessionId);
  
  // Invalidate session lists as they're now outdated
  researchCache.clearSessionListCache();
}
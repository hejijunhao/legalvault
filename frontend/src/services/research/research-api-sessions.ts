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
  getAuthHeader, 
  fetchWithSelfSignedCert, 
  withRetry, 
  handleApiError 
} from './research-api-core';
import { researchCache } from './research-cache';

/**
 * Fetch a list of research sessions
 */
export async function fetchSessions(
  options?: {
    featuredOnly?: boolean;
    status?: QueryStatus;
    limit?: number;
    offset?: number;
  } | null
): Promise<SearchListResponse> {
  const cachedData = researchCache.getSessionList(options);
  if (cachedData) {
    return cachedData;
  }
  
  const headers = await getAuthHeader();
  const params = new URLSearchParams();
  if (options?.featuredOnly) params.append('featured', 'true');
  if (options?.status) params.append('status', options.status);
  if (options?.limit) params.append('limit', options.limit.toString());
  if (options?.offset) params.append('offset', options.offset.toString());
  
  const queryString = params.toString() ? `?${params.toString()}` : '';
  const url = `/api/research/searches${queryString}`;
  console.log('fetchSessions URL:', url);
  
  const response = await withRetry(() => fetchWithSelfSignedCert(url, { headers }));
  
  if (!response.ok) return handleApiError(response);
  const data = await response.json();
  
  researchCache.setSessionList(data, options);
  return data;
}

/**
 * Fetch a single research session by ID
 */
export async function fetchSession(sessionId: string): Promise<ResearchSession> {
  const cachedSession = researchCache.checkSessionCache(sessionId);
  if (cachedSession) {
    return cachedSession;
  }
  
  const headers = await getAuthHeader();
  const url = `/api/research/searches/${sessionId}`;
  console.log('fetchSession URL:', url);
  
  const response = await withRetry(() => fetchWithSelfSignedCert(url, { headers }));
  
  if (!response.ok) return handleApiError(response);
  const data = await response.json();
  
  researchCache.setSession(data);
  return data;
}

/**
 * Create a new research session
 */
export async function createNewSession(
  query: string,
  searchParams?: SearchParams
): Promise<ResearchSession> {
  const headers = await getAuthHeader();
  const url = '/api/research/searches';
  console.log('createNewSession URL:', url);
  
  const response = await withRetry(() => fetchWithSelfSignedCert(url, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      query,
      search_params: searchParams
    })
  }));
  
  if (!response.ok) return handleApiError(response);
  const data = await response.json();
  
  researchCache.setSession(data);
  researchCache.clearSessionListCache();
  return data;
}

/**
 * Send a message to a research session
 */
export async function sendSessionMessage(
  sessionId: string,
  content: string
): Promise<ResearchSession> {
  const headers = await getAuthHeader();
  const url = `/api/research/searches/${sessionId}/continue`;
  console.log('sendSessionMessage URL:', url);
  
  const response = await withRetry(
    () => fetchWithSelfSignedCert(url, {
      method: 'POST',
      headers,
      body: JSON.stringify({ follow_up_query: content })
    }),
    3,
    (error) => error?.status === 429 || 
               error?.code === 'PERPLEXITY_RATE_LIMITED' || 
               error?.code === 'RATE_LIMITED'
  );
  
  if (!response.ok) return handleApiError(response);
  const data = await response.json();
  
  researchCache.setSession(data);
  researchCache.invalidateSearch(sessionId);
  return data;
}

/**
 * Continue a research session with a follow-up query
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
  const url = `/api/research/searches/${sessionId}/continue`;
  console.log('continueSession URL:', url);
  
  const response = await withRetry(
    () => fetchWithSelfSignedCert(url, {
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
    (error) => error?.status === 429 || 
               error?.code === 'PERPLEXITY_RATE_LIMITED' || 
               error?.code === 'RATE_LIMITED'
  );
  
  if (!response.ok) return handleApiError(response);
  const data = await response.json();
  
  researchCache.setSession(data);
  researchCache.invalidateSearch(sessionId);
  return data;
}

/**
 * Update the metadata of a research session
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
  const url = `/api/research/searches/${sessionId}`;
  console.log('updateSessionMetadata URL:', url);
  
  const response = await withRetry(() => fetchWithSelfSignedCert(url, {
    method: 'PATCH',
    headers,
    body: JSON.stringify(updates)
  }));
  
  if (!response.ok) return handleApiError(response);
  const data = await response.json();
  
  researchCache.setSession(data);
  researchCache.clearSessionListCache();
  return data;
}

/**
 * Delete a research session
 */
export async function deleteSession(sessionId: string): Promise<void> {
  const headers = await getAuthHeader();
  const url = `/api/research/searches/${sessionId}`;
  console.log('deleteSession URL:', url);
  
  const response = await withRetry(() => fetchWithSelfSignedCert(url, {
    method: 'DELETE',
    headers
  }));
  
  if (!response.ok) return handleApiError(response);
  
  researchCache.invalidateSearch(sessionId);
  researchCache.clearSessionListCache();
}
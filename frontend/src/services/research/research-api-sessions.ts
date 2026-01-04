// src/services/research/research-api-sessions.ts
// Research session API functions using centralized apiClient

import { apiClient } from '@/lib/api-client'
import {
  ResearchSession,
  SearchListResponse,
  SearchParams,
  QueryCategory,
  QueryStatus,
  QueryType
} from './research-api-types'
import { researchCache } from './research-cache'

/**
 * Fetch a list of research sessions
 */
export async function fetchSessions(
  options?: {
    featuredOnly?: boolean
    status?: QueryStatus
    limit?: number
    offset?: number
  } | null
): Promise<SearchListResponse> {
  const cachedData = researchCache.getSessionList(options)
  if (cachedData) {
    return cachedData
  }

  const params: Record<string, string | number | boolean | undefined> = {}
  if (options?.featuredOnly) params.featured = true
  if (options?.status) params.status = options.status
  if (options?.limit) params.limit = options.limit
  if (options?.offset) params.offset = options.offset

  const data = await apiClient.get<SearchListResponse>('/api/research/searches', params)

  researchCache.setSessionList(data, options)
  return data
}

/**
 * Fetch a single research session by ID
 */
export async function fetchSession(sessionId: string): Promise<ResearchSession> {
  const cachedSession = researchCache.checkSessionCache(sessionId)
  if (cachedSession) {
    return cachedSession
  }

  const data = await apiClient.get<ResearchSession>(`/api/research/searches/${sessionId}`)

  researchCache.setSession(data)
  return data
}

/**
 * Create a new research session
 */
export async function createNewSession(
  query: string,
  searchParams?: SearchParams
): Promise<ResearchSession> {
  const data = await apiClient.post<ResearchSession>('/api/research/searches', {
    query,
    search_params: searchParams
  })

  researchCache.setSession(data)
  researchCache.clearSessionListCache()
  return data
}

/**
 * Send a message to a research session (follow-up query)
 */
export async function sendSessionMessage(
  sessionId: string,
  content: string
): Promise<ResearchSession> {
  const data = await apiClient.post<ResearchSession>(
    `/api/research/searches/${sessionId}/continue`,
    { follow_up_query: content }
  )

  researchCache.setSession(data)
  researchCache.invalidateSearch(sessionId)
  return data
}

/**
 * Continue a research session with a follow-up query (extended options)
 */
export async function continueSession(
  sessionId: string,
  followUpQuery: string,
  options?: {
    threadId?: string
    previousMessages?: Array<{ role: string; content: unknown }>
    searchParams?: SearchParams
  }
): Promise<ResearchSession> {
  const data = await apiClient.post<ResearchSession>(
    `/api/research/searches/${sessionId}/continue`,
    {
      follow_up_query: followUpQuery,
      thread_id: options?.threadId,
      previous_messages: options?.previousMessages,
      search_params: options?.searchParams
    }
  )

  researchCache.setSession(data)
  researchCache.invalidateSearch(sessionId)
  return data
}

/**
 * Update the metadata of a research session
 */
export async function updateSessionMetadata(
  sessionId: string,
  updates: {
    title?: string
    description?: string
    is_featured?: boolean
    tags?: string[]
    category?: QueryCategory
    query_type?: QueryType
    status?: QueryStatus
  }
): Promise<ResearchSession> {
  const data = await apiClient.patch<ResearchSession>(
    `/api/research/searches/${sessionId}`,
    updates
  )

  researchCache.setSession(data)
  researchCache.clearSessionListCache()
  return data
}

/**
 * Delete a research session
 */
export async function deleteSession(sessionId: string): Promise<void> {
  await apiClient.delete(`/api/research/searches/${sessionId}`)

  researchCache.invalidateSearch(sessionId)
  researchCache.clearSessionListCache()
}

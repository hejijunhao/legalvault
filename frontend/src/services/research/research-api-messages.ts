// src/services/research/research-api-messages.ts
// Research message API functions using centralized apiClient

import { apiClient } from '@/lib/api-client'
import {
  Message,
  MessageListResponse,
  Citation,
  QueryStatus
} from './research-api-types'
import { researchCache } from './research-cache'

/**
 * Fetch a single message by ID
 */
export async function fetchMessage(messageId: string): Promise<Message> {
  const cachedMessage = researchCache.getMessage(messageId)
  if (cachedMessage) {
    return cachedMessage
  }

  const data = await apiClient.get<Message>(`/api/research/messages/${messageId}`)

  researchCache.setMessage(data)
  return data
}

/**
 * Create a new message in a search
 */
export async function createMessage(
  searchId: string,
  message: {
    role: string
    content: { text: string; citations?: Citation[] }
    sequence?: number
    status?: QueryStatus
  }
): Promise<Message> {
  const data = await apiClient.post<Message>(
    `/api/research/messages/search/${searchId}`,
    message
  )

  researchCache.setMessage(data)
  researchCache.invalidateMessageList(searchId)
  return data
}

/**
 * Fetch messages for a search
 */
export async function fetchMessagesForSearch(
  searchId: string,
  options?: {
    limit?: number
    offset?: number
  } | null
): Promise<MessageListResponse> {
  const cachedMessages = researchCache.checkMessageListCache(searchId, options)
  if (cachedMessages) {
    return cachedMessages
  }

  const params: Record<string, string | number | boolean | undefined> = {}
  if (options?.limit) params.limit = options.limit
  if (options?.offset) params.offset = options.offset

  const data = await apiClient.get<MessageListResponse>(
    `/api/research/messages/search/${searchId}`,
    params
  )

  researchCache.setMessageList(searchId, data, options)
  return data
}

/**
 * Update a message
 */
export async function updateMessage(
  messageId: string,
  updates: {
    content?: { text: string; citations?: Citation[] }
    status?: QueryStatus
  }
): Promise<Message> {
  const data = await apiClient.patch<Message>(
    `/api/research/messages/${messageId}`,
    updates
  )

  researchCache.setMessage(data)
  if (data.search_id) {
    researchCache.invalidateMessageList(data.search_id)
  }
  return data
}

/**
 * Delete a message
 */
export async function deleteMessage(messageId: string, searchId?: string): Promise<void> {
  // If searchId not provided, try to get it from cached message
  if (!searchId) {
    try {
      const message = await fetchMessage(messageId)
      searchId = message.search_id
    } catch {
      // Continue without searchId - cache invalidation will be skipped
    }
  }

  await apiClient.delete(`/api/research/messages/${messageId}`)

  researchCache.deleteMessage(messageId)
  if (searchId) {
    researchCache.invalidateMessageList(searchId)
  }
}

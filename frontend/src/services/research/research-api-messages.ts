// src/services/research/research-api-messages.ts

import { 
  Message, 
  MessageListResponse, 
  Citation, 
  QueryStatus 
} from './research-api-types';
import { 
  getAuthHeader, 
  fetchWithSelfSignedCert, 
  withRetry, 
  handleApiError 
} from './research-api-core';
import { researchCache } from './research-cache';

/**
 * Fetch a single message by ID
 */
export async function fetchMessage(messageId: string): Promise<Message> {
  const cachedMessage = researchCache.getMessage(messageId);
  if (cachedMessage) {
    return cachedMessage;
  }

  const headers = await getAuthHeader();
  const url = `/api/research/messages/${messageId}`;
  console.log('fetchMessage URL:', url);
  
  const response = await withRetry(() => fetchWithSelfSignedCert(url, { headers }));
  
  if (!response.ok) return handleApiError(response);
  const data = await response.json();
  
  researchCache.setMessage(data);
  return data;
}

/**
 * Create a new message in a search
 */
export async function createMessage(
  searchId: string,
  message: {
    role: string;
    content: { text: string; citations?: Citation[] };
    sequence?: number;
    status?: QueryStatus;
  }
): Promise<Message> {
  const headers = await getAuthHeader();
  const url = `/api/research/messages/search/${searchId}`;
  console.log('createMessage URL:', url);
  
  const response = await withRetry(() => fetchWithSelfSignedCert(url, {
    method: 'POST',
    headers,
    body: JSON.stringify(message)
  }));
  
  if (!response.ok) return handleApiError(response);
  const data = await response.json();
  
  researchCache.setMessage(data);
  researchCache.invalidateMessageList(searchId);
  return data;
}

/**
 * Fetch messages for a search
 */
export async function fetchMessagesForSearch(
  searchId: string,
  options?: {
    limit?: number;
    offset?: number;
  } | null
): Promise<MessageListResponse> {
  const cachedMessages = researchCache.getMessageList(searchId, options);
  if (cachedMessages) {
    return cachedMessages;
  }

  const headers = await getAuthHeader();
  const params = new URLSearchParams();
  if (options?.limit) params.append('limit', options.limit.toString());
  if (options?.offset) params.append('offset', options.offset.toString());
  
  const queryString = params.toString() ? `?${params.toString()}` : '';
  const url = `/api/research/messages/search/${searchId}${queryString}`;
  console.log('fetchMessagesForSearch URL:', url);
  
  const response = await withRetry(() => fetchWithSelfSignedCert(url, { headers }));
  
  if (!response.ok) return handleApiError(response);
  const data = await response.json();
  
  researchCache.setMessageList(searchId, data, options);
  return data;
}

/**
 * Update a message
 */
export async function updateMessage(
  messageId: string, 
  updates: {
    content?: { text: string, citations?: Citation[] };
    status?: QueryStatus;
  }
): Promise<Message> {
  const headers = await getAuthHeader();
  const url = `/api/research/messages/${messageId}`;
  console.log('updateMessage URL:', url);
  
  const response = await withRetry(() => fetchWithSelfSignedCert(url, {
    method: 'PATCH',
    headers,
    body: JSON.stringify(updates)
  }));
  
  if (!response.ok) return handleApiError(response);
  const data = await response.json();
  
  researchCache.setMessage(data);
  if (data.search_id) {
    researchCache.invalidateMessageList(data.search_id);
  }
  return data;
}

/**
 * Delete a message
 */
export async function deleteMessage(messageId: string, searchId?: string): Promise<void> {
  const headers = await getAuthHeader();
  
  if (!searchId) {
    try {
      const message = await fetchMessage(messageId);
      searchId = message.search_id;
    } catch (error) {
      console.error('Failed to fetch message before deletion:', error);
    }
  }
  
  const url = `/api/research/messages/${messageId}`;
  console.log('deleteMessage URL:', url);
  
  const response = await withRetry(() => fetchWithSelfSignedCert(url, {
    method: 'DELETE',
    headers
  }));
  
  if (!response.ok) return handleApiError(response);
  
  researchCache.deleteMessage(messageId);
  if (searchId) {
    researchCache.invalidateMessageList(searchId);
  }
}

// TODO: Implement backend endpoint POST /research/messages/{message_id}/forward
// export async function forwardMessage(...) { ... }
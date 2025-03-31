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
  handleApiError,
  handleEncryptedFields 
} from './research-api-core';
import { researchCache } from './research-cache';

/**
 * Fetch a single message by ID
 * @param messageId The ID of the message to fetch
 * @returns The message
 */
export async function fetchMessage(messageId: string): Promise<Message> {
  // Check cache first
  const cachedMessage = researchCache.getMessage(messageId);
  if (cachedMessage) {
    return handleEncryptedFields(cachedMessage);
  }

  const headers = await getAuthHeader();
  const response = await withRetry(() => 
    fetchWithSelfSignedCert(`/api/research/messages/${messageId}`, { headers })
  );
  
  if (!response.ok) return handleApiError(response);
  const data = await response.json();
  const processedData = handleEncryptedFields(data);
  // Cache the response
  researchCache.setMessage(processedData);
  
  return processedData;
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
  const response = await withRetry(() => 
    fetchWithSelfSignedCert(`/api/research/messages/search/${searchId}`, {
      method: 'POST',
      headers,
      body: JSON.stringify(message)
    })
  );
  
  if (!response.ok) return handleApiError(response);
  const data = await response.json();
  const processedData = handleEncryptedFields(data);
  // Cache the new message
  researchCache.setMessage(processedData);
  
  // Invalidate message list cache for this search
  researchCache.invalidateMessageList(searchId);
  
  return processedData;
}

/**
 * Fetch messages for a search
 * @param searchId The ID of the search to fetch messages for
 * @param options Options for filtering and pagination
 * @returns A list of messages
 */
export async function fetchMessagesForSearch(
  searchId: string,
  options?: {
    limit?: number;
    offset?: number;
  } | null
): Promise<MessageListResponse> {
  // Check cache first
  const cachedMessages = researchCache.getMessageList(searchId, options);
  if (cachedMessages) {
    return handleEncryptedFields(cachedMessages);
  }

  const headers = await getAuthHeader();
  
  // Build query parameters
  const params = new URLSearchParams();
  if (options?.limit) params.append('limit', options.limit.toString());
  if (options?.offset) params.append('offset', options.offset.toString());
  
  const queryString = params.toString() ? `?${params.toString()}` : '';
  const response = await withRetry(() => 
    fetchWithSelfSignedCert(`/api/research/messages/search/${searchId}${queryString}`, { headers })
  );
  
  if (!response.ok) return handleApiError(response);
  const data = await response.json();
  const processedData = handleEncryptedFields(data);
  // Cache the response
  researchCache.setMessageList(searchId, processedData, options);
  
  return processedData;
}

/**
 * Update a message
 * @param messageId The ID of the message to update
 * @param data The updates to apply
 * @returns The updated message
 */
export async function updateMessage(
  messageId: string,
  data: Partial<Message>
): Promise<Message> {
  const headers = await getAuthHeader();
  const response = await withRetry(() =>
    fetchWithSelfSignedCert(`/api/research/messages/${messageId}/`, {
      method: 'PATCH',
      headers,
      body: JSON.stringify(data)
    })
  );
  
  if (!response.ok) return handleApiError(response);
  const responseData = await response.json();
  const processedData = handleEncryptedFields(responseData);
  
  // Cache the updated message
  researchCache.setMessage(processedData);
  
  // Invalidate message list cache if we have the search_id
  const searchId = (processedData as Message).search_id;
  if (searchId) {
    researchCache.invalidateMessageList(searchId);
  }
  
  return processedData;
}

/**
 * Delete a message
 * @param messageId The ID of the message to delete
 * @param searchId Optional search ID if known, to avoid extra API call
 */
export async function deleteMessage(messageId: string, searchId?: string): Promise<void> {
  const headers = await getAuthHeader();
  
  // If searchId wasn't provided, try to get it from the message
  if (!searchId) {
    try {
      const message = await fetchMessage(messageId);
      searchId = message.search_id;
    } catch (error) {
      console.error('Failed to fetch message before deletion:', error);
    }
  }
  
  const response = await withRetry(() => 
    fetchWithSelfSignedCert(`/api/research/messages/${messageId}`, {
      method: 'DELETE',
      headers
    })
  );
  
  if (!response.ok) return handleApiError(response);
  
  // Remove from cache
  researchCache.deleteMessage(messageId);
  
  // Invalidate message list cache if we have the search_id
  if (searchId) {
    researchCache.invalidateMessageList(searchId);
  }
}

/**
 * Forward a message
     * @param messageId The ID of the message to forward
     * @param destination The destination to forward the message to
     * @param destinationType The type of destination (email, user, workspace)
 */
export async function forwardMessage(
  messageId: string,
  destination: string,
  destinationType: 'email' | 'user' | 'workspace'
): Promise<any> {
  const headers = await getAuthHeader();
  const response = await withRetry(() => 
    fetchWithSelfSignedCert(`/api/research/messages/${messageId}/forward`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        destination,
        destination_type: destinationType
      })
    })
  );
  
  if (!response.ok) return handleApiError(response);
  return await response.json();
}
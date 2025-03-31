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
  handleEncryptedFields,
  getApiBaseUrl
} from './research-api-core';
import { researchCache } from './research-cache';

/**
 * Fetch a single message by ID
 * @param searchId The ID of the search to fetch messages for
 * @param messageId The ID of the message to fetch
 * @returns The message
 */
export async function fetchMessage(searchId: string, messageId: string): Promise<Message> {
  // Check cache first
  const cachedMessage = researchCache.getMessage(messageId);
  if (cachedMessage) {
    return handleEncryptedFields(cachedMessage);
  }

  const headers = await getAuthHeader();
  const response = await withRetry(() => 
    fetchWithSelfSignedCert(`${getApiBaseUrl()}/research/searches/${searchId}/messages/${messageId}`, { headers })
  );
  
  if (!response.ok) return handleApiError(response);
  const data = await response.json();
  const processedData = handleEncryptedFields(data);
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
    status?: QueryStatus;
    metadata?: Record<string, any>;
  }
): Promise<Message> {
  const headers = await getAuthHeader();
  const response = await withRetry(() =>
    fetchWithSelfSignedCert(
      `${getApiBaseUrl()}/research/searches/${searchId}/messages`,
      {
        method: 'POST',
        headers: { ...headers, 'Content-Type': 'application/json' },
        body: JSON.stringify(message)
      }
    )
  );

  if (!response.ok) return handleApiError(response);
  const data = await response.json();
  const processedData = handleEncryptedFields(data);
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
  const cachedMessages = researchCache.getMessageList(searchId);
  if (cachedMessages) {
    return handleEncryptedFields(cachedMessages);
  }

  const headers = await getAuthHeader();
  const queryParams = new URLSearchParams();
  if (options?.limit) queryParams.append('limit', options.limit.toString());
  if (options?.offset) queryParams.append('offset', options.offset.toString());

  const response = await withRetry(() =>
    fetchWithSelfSignedCert(
      `${getApiBaseUrl()}/research/searches/${searchId}/messages?${queryParams}`,
      { headers }
    )
  );

  if (!response.ok) return handleApiError(response);
  const data = await response.json();
  const processedData = handleEncryptedFields(data);
  researchCache.setMessageList(searchId, processedData);
  
  return processedData;
}

/**
 * Update a message
 * @param searchId The ID of the search to update messages for
 * @param messageId The ID of the message to update
 * @param data The updates to apply
 * @returns The updated message
 */
export async function updateMessage(
  searchId: string,
  messageId: string,
  data: Partial<Message>
): Promise<Message> {
  const headers = await getAuthHeader();
  const response = await withRetry(() =>
    fetchWithSelfSignedCert(
      `${getApiBaseUrl()}/research/searches/${searchId}/messages/${messageId}`,
      {
        method: 'PATCH',
        headers: { ...headers, 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      }
    )
  );

  if (!response.ok) return handleApiError(response);
  const responseData = await response.json();
  const processedData = handleEncryptedFields(responseData);
  researchCache.setMessage(processedData);
  
  // Invalidate message list cache if we have the search_id
  researchCache.invalidateMessageList(searchId);
  
  return processedData;
}

/**
 * Delete a message
 * @param searchId The ID of the search to delete messages for
 * @param messageId The ID of the message to delete
 */
export async function deleteMessage(searchId: string, messageId: string): Promise<void> {
  const headers = await getAuthHeader();
  const response = await withRetry(() =>
    fetchWithSelfSignedCert(
      `${getApiBaseUrl()}/research/searches/${searchId}/messages/${messageId}`,
      {
        method: 'DELETE',
        headers
      }
    )
  );

  if (!response.ok) return handleApiError(response);
  researchCache.deleteMessage(messageId);
  researchCache.invalidateMessageList(searchId);
}

/**
 * Forward a message
 * @param searchId The ID of the search to forward messages for
 * @param messageId The ID of the message to forward
 * @param destination The destination to forward the message to
 * @param destinationType The type of destination (email, user, workspace)
 */
export async function forwardMessage(
  searchId: string,
  messageId: string,
  destination: string,
  destinationType: 'email' | 'user' | 'workspace'
): Promise<any> {
  const headers = await getAuthHeader();
  const response = await withRetry(() => 
    fetchWithSelfSignedCert(
      `${getApiBaseUrl()}/research/searches/${searchId}/messages/${messageId}/forward`,
      {
        method: 'POST',
        headers,
        body: JSON.stringify({
          destination,
          destination_type: destinationType
        })
      }
    )
  );
  
  if (!response.ok) return handleApiError(response);
  return await response.json();
}
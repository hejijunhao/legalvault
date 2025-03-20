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
 * @param messageId The ID of the message to fetch
 * @returns The message
 */
export async function fetchMessage(messageId: string): Promise<Message> {
  // Check cache first
  const cachedMessage = researchCache.getMessage(messageId);
  if (cachedMessage) {
    return cachedMessage;
  }

  const headers = await getAuthHeader();
  const response = await withRetry(() => 
    fetchWithSelfSignedCert(`/api/research/messages/${messageId}`, { headers })
  );
  
  if (!response.ok) return handleApiError(response);
  const data = await response.json();
  
  // Cache the response
  researchCache.setMessage(data);
  
  return data;
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
    return cachedMessages;
  }

  const headers = await getAuthHeader();
  
  // Build query parameters
  const params = new URLSearchParams();
  if (options?.limit) params.append('limit', options.limit.toString());
  if (options?.offset) params.append('offset', options.offset.toString());
  
  const queryString = params.toString() ? `?${params.toString()}` : '';
  const response = await withRetry(() => 
    fetchWithSelfSignedCert(`/api/research/searches/${searchId}/messages/${queryString}`, { headers })
  );
  
  if (!response.ok) return handleApiError(response);
  const data = await response.json();
  
  // Cache the response
  researchCache.setMessageList(searchId, data, options);
  
  return data;
}

/**
 * Update a message
 * @param messageId The ID of the message to update
 * @param updates The updates to apply
 * @returns The updated message
 */
export async function updateMessage(
  messageId: string, 
  updates: {
    content?: { text: string, citations?: Citation[] };
    status?: QueryStatus;
  }
): Promise<Message> {
  const headers = await getAuthHeader();
  const response = await withRetry(() => fetchWithSelfSignedCert(`/api/research/messages/${messageId}`, {
    method: 'PATCH',
    headers,
    body: JSON.stringify(updates)
  }));
  
  if (!response.ok) return handleApiError(response);
  const data = await response.json();
  
  // Cache the updated message
  researchCache.setMessage(data);
  
  // Invalidate session cache as it might contain this message
  if (data.search_id) {
    researchCache.invalidateSearch(data.search_id);
  }
  
  return data;
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
          // Try different property names that might contain the search ID
          searchId = (message as any).search_id || (message as any).searchId || (message as any).session_id || (message as any).sessionId;
        } catch (error) {
          console.error('Failed to fetch message before deletion:', error);
        }
      }
      
      const response = await withRetry(() => fetchWithSelfSignedCert(`/api/research/messages/${messageId}`, {
        method: 'DELETE',
        headers
      }));
      
      if (!response.ok) return handleApiError(response);
      
      // Remove the message from cache
      researchCache.deleteMessage(messageId);
      
      // Invalidate related caches
      if (searchId) {
        researchCache.invalidateSearch(searchId);
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
      const response = await withRetry(() => fetchWithSelfSignedCert(`/api/research/messages/${messageId}/forward`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          destination,
          destination_type: destinationType
        })
      }));
      
      if (!response.ok) return handleApiError(response);
      return await response.json();
    }
    
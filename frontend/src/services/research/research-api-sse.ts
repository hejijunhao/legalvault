// src/services/research/research-api-sse.ts

import { getApiBaseUrl, getAuthHeader } from "./research-api-core";
import { SSEConnection, SSEOptions, ConnectionStatus, SSEEventType } from "./research-api-types";

/**
 * Establishes an SSE connection for real-time message updates
 * @param searchId The ID of the search to connect to
 * @param options Configuration options for the SSE connection
 * @returns An SSEConnection object with methods to interact with the connection
 */
export async function connectToSSE(
  searchId: string,
  options: SSEOptions
): Promise<SSEConnection> {
  const { onMessage, onError = console.error, onConnectionChange = () => {} } = options;

  // Get auth header
  const headers = await getAuthHeader();
  const token = headers.Authorization?.replace('Bearer ', '');
  if (!token) {
    throw new Error('No authentication token found');
  }

  // Create EventSource with auth token in URL
  const baseUrl = `${getApiBaseUrl()}/research/searches/${searchId}/stream?token=${token}`;
  console.log('Connecting to SSE URL:', baseUrl);
  const eventSource = new EventSource(baseUrl);

  let connected = false;

  eventSource.onopen = () => {
    connected = true;
    onConnectionChange(ConnectionStatus.CONNECTED);
  };

  // Handle specific event types
  eventSource.addEventListener('connected', () => {
    connected = true;
    onConnectionChange(ConnectionStatus.CONNECTED);
  });

  eventSource.addEventListener('messages', (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage({
        type: SSEEventType.MESSAGES,
        data
      });
    } catch (error) {
      onError(error as Error);
    }
  });

  eventSource.addEventListener('heartbeat', () => {
    onMessage({
      type: SSEEventType.HEARTBEAT,
      data: {}
    });
  });

  eventSource.addEventListener('error', (event) => {
    connected = false;
    onConnectionChange(ConnectionStatus.ERROR);
    onError(new Error('SSE connection error'));
  });

  return {
    disconnect: () => {
      eventSource.close();
      connected = false;
      onConnectionChange(ConnectionStatus.DISCONNECTED);
    },
    isConnected: () => connected
  };
}
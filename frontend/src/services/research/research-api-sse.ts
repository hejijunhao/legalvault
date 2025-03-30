// src/services/research/research-api-sse.ts

import { getApiBaseUrl, getAuthHeader } from "./research-api-core";
import { SSEConnection, SSEOptions, SSEMessage, SSEEventType, ApiError } from "./research-api-types";

const DEFAULT_RETRY_ATTEMPTS = 3;
const DEFAULT_RETRY_DELAY = 1000; // 1 second
const HEARTBEAT_TIMEOUT = 90000; // 90 seconds

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
  const {
    onMessage,
    onError,
    onConnectionChange,
    retryAttempts = DEFAULT_RETRY_ATTEMPTS,
    retryDelay = DEFAULT_RETRY_DELAY
  } = options;

  // Get the auth token with retry logic
  let token: string | null = null;
  let tokenRetryCount = 0;

  while (!token && tokenRetryCount < retryAttempts) {
    try {
      console.debug(`Attempting to get auth token (attempt ${tokenRetryCount + 1}/${retryAttempts})`);
      const headers = await getAuthHeader();
      token = headers.Authorization?.replace('Bearer ', '') || null;

      if (!token) {
        tokenRetryCount++;
        await new Promise(resolve => setTimeout(resolve, retryDelay * Math.pow(2, tokenRetryCount)));
      }
    } catch (error) {
      console.error('Error retrieving auth token:', error);
      tokenRetryCount++;
      await new Promise(resolve => setTimeout(resolve, retryDelay * Math.pow(2, tokenRetryCount)));
    }
  }

  if (!token) {
    const error = new Error('Failed to retrieve authentication token') as ApiError;
    error.code = 'AUTH_TOKEN_FAILED';
    console.error(error);
    onError(error);
    onConnectionChange(false);
    throw error;
  }

  // Create SSE connection URL
  const baseUrl = getApiBaseUrl();
  const sseUrl = new URL(`${baseUrl}/api/research/messages/sse/${searchId}`);
  sseUrl.searchParams.append('token', token);

  // Create EventSource with connection state tracking
  let eventSource: EventSource | null = null;
  let isConnected = false;
  let heartbeatTimeout: ReturnType<typeof setTimeout> | null = null;
  let reconnectAttempt = 0;

  function setupEventSource(): void {
    if (eventSource) {
      eventSource.close();
    }

    eventSource = new EventSource(sseUrl.toString());
    console.debug('Creating new SSE connection to:', sseUrl.toString());

    // Set up event listeners
    eventSource.onopen = () => {
      console.debug('SSE connection opened');
      isConnected = true;
      reconnectAttempt = 0;
      onConnectionChange(true);
    };

    eventSource.onerror = (error) => {
      console.error('SSE connection error:', error);
      isConnected = false;
      onConnectionChange(false);

      // Format error for consistent handling
      const apiError = new Error('SSE connection error') as ApiError;
      apiError.code = 'SSE_CONNECTION_ERROR';
      apiError.originalError = error;
      onError(apiError);

      // Attempt reconnection with exponential backoff
      if (reconnectAttempt < retryAttempts) {
        const delay = retryDelay * Math.pow(2, reconnectAttempt);
        console.debug(`Attempting to reconnect in ${delay}ms (attempt ${reconnectAttempt + 1}/${retryAttempts})`);
        setTimeout(setupEventSource, delay);
        reconnectAttempt++;
      }
    };

    // Set up event handlers for different message types
    eventSource.addEventListener(SSEEventType.CONNECTION_ESTABLISHED, (event: MessageEvent) => {
      const data = JSON.parse(event.data);
      onMessage({ type: SSEEventType.CONNECTION_ESTABLISHED, data });
    });

    eventSource.addEventListener(SSEEventType.HEARTBEAT, (event: MessageEvent) => {
      // Reset heartbeat timeout
      if (heartbeatTimeout) {
        clearTimeout(heartbeatTimeout);
      }

      // Set new timeout to detect if heartbeats stop
      heartbeatTimeout = setTimeout(() => {
        const error = new Error('Connection stale: no heartbeat received') as ApiError;
        error.code = 'HEARTBEAT_TIMEOUT';
        onError(error);
      }, HEARTBEAT_TIMEOUT);

      // Process heartbeat
      const data = JSON.parse(event.data);
      onMessage({ type: SSEEventType.HEARTBEAT, data });
    });

    eventSource.addEventListener(SSEEventType.MESSAGES, (event: MessageEvent) => {
      const data = JSON.parse(event.data);
      onMessage({ type: SSEEventType.MESSAGES, data });
    });

    eventSource.addEventListener(SSEEventType.USER_MESSAGE, (event: MessageEvent) => {
      const data = JSON.parse(event.data);
      onMessage({ type: SSEEventType.USER_MESSAGE, data });
    });

    eventSource.addEventListener(SSEEventType.ASSISTANT_CHUNK, (event: MessageEvent) => {
      const data = JSON.parse(event.data);
      onMessage({ type: SSEEventType.ASSISTANT_CHUNK, data });
    });

    eventSource.addEventListener(SSEEventType.ASSISTANT_MESSAGE_COMPLETE, (event: MessageEvent) => {
      const data = JSON.parse(event.data);
      onMessage({ type: SSEEventType.ASSISTANT_MESSAGE_COMPLETE, data });
    });

    eventSource.addEventListener(SSEEventType.ERROR, (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data);
        const error = new Error(data.message || 'Unknown error') as ApiError;
        error.code = 'SSE_SERVER_ERROR';
        error.details = data.details;
        onError(error);
      } catch (e) {
        // If event.data isn't JSON, use the raw error
        const error = new Error('Server error') as ApiError;
        error.code = 'SSE_SERVER_ERROR';
        error.originalError = event;
        onError(error);
      }
    });
  }

  // Initial connection
  setupEventSource();

  // Return connection interface
  return {
    disconnect: () => {
      if (eventSource) {
        console.debug('Closing SSE connection');
        eventSource.close();
        eventSource = null;
      }

      if (heartbeatTimeout) {
        clearTimeout(heartbeatTimeout);
        heartbeatTimeout = null;
      }

      isConnected = false;
      onConnectionChange(false);
    },
    get isConnected() {
      return isConnected;
    }
  };
}
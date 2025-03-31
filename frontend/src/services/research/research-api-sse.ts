// src/services/research/research-api-sse.ts

import { getApiBaseUrl, getAuthHeader } from "./research-api-core";
import { SSEConnection, SSEOptions, ConnectionStatus } from "./research-api-types";

/**
 * Custom EventSource class that supports headers
 */
class HeaderSupportingEventSource extends EventTarget {
  private url: string;
  private headers: Record<string, string>;
  private eventSource: EventSource | null = null;
  private reconnectTimeout: number = 1000;
  private maxReconnectAttempts: number = 5;
  private reconnectAttempts: number = 0;

  constructor(url: string, headers: Record<string, string>) {
    super();
    this.url = this.addAuthHeader(url, headers.Authorization);
    this.headers = headers;
    this.connect();
  }

  private addAuthHeader(url: string, authHeader: string): string {
    const urlObj = new URL(url);
    const token = authHeader.replace('Bearer ', '');
    urlObj.searchParams.append('token', token);
    return urlObj.toString();
  }

  private connect() {
    this.eventSource = new EventSource(this.url);

    this.eventSource.onopen = () => {
      this.reconnectAttempts = 0;
      this.dispatchEvent(new Event('open'));
    };

    this.eventSource.onmessage = (event) => {
      this.dispatchEvent(new MessageEvent('message', { data: event.data }));
    };

    this.eventSource.onerror = (event) => {
      this.dispatchEvent(new Event('error'));
      this.eventSource?.close();
      
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        setTimeout(() => {
          this.reconnectAttempts++;
          this.connect();
        }, this.reconnectTimeout);
      }
    };

    // Forward other events
    ['connected', 'heartbeat'].forEach(eventName => {
      this.eventSource?.addEventListener(eventName, (event: Event) => {
        this.dispatchEvent(new Event(eventName));
      });
    });
  }

  close() {
    this.eventSource?.close();
  }

  addEventListener(type: string, listener: EventListener) {
    super.addEventListener(type, listener);
  }

  removeEventListener(type: string, listener: EventListener) {
    super.removeEventListener(type, listener);
  }
}

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
  const { onMessage, onError, onConnectionChange } = options;

  // Get auth header
  const headers = await getAuthHeader();
  if (!headers.Authorization) {
    throw new Error('No authentication token found');
  }

  // Create EventSource with auth header
  const url = `${getApiBaseUrl()}/research/searches/${searchId}/stream`;
  const eventSource = new HeaderSupportingEventSource(url, headers);

  let connected = false;

  eventSource.addEventListener('open', () => {
    connected = true;
    onConnectionChange(ConnectionStatus.CONNECTED);
  });

  eventSource.addEventListener('message', (event: Event) => {
    try {
      const messages = JSON.parse((event as MessageEvent).data);
      onMessage(messages);
    } catch (error) {
      onError(error as Error);
    }
  });

  eventSource.addEventListener('error', () => {
    connected = false;
    onConnectionChange(ConnectionStatus.ERROR);
    onError(new Error('SSE connection error'));
  });

  eventSource.addEventListener('heartbeat', () => {
    // Connection is alive
  });

  return {
    close: () => {
      eventSource.close();
      connected = false;
      onConnectionChange(ConnectionStatus.DISCONNECTED);
    },
    isConnected: () => connected
  };
}
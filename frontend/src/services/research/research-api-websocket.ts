// src/services/research/research-api-websocket.ts

import { supabase } from "@/lib/supabase";
import { WebSocketConnection, WebSocketMessage } from "./research-api-types";
import { getAuthHeader } from "./research-api-core";

/**
 * Establishes a WebSocket connection for real-time message updates
 * @param searchId The ID of the search to connect to
 * @param onMessage Callback function for handling incoming messages
 * @param onError Callback function for handling errors
 * @param onConnectionChange Callback function for handling connection state changes
 * @returns A WebSocketConnection object with methods to interact with the connection
 */
export async function connectToMessageUpdates(
  searchId: string,
  onMessage: (message: WebSocketMessage) => void,
  onError: (error: any) => void,
  onConnectionChange: (connected: boolean) => void
): Promise<WebSocketConnection> {
  // Get the auth token with retry logic
  let token: string | null = null;
  let tokenRetryCount = 0;
  const maxTokenRetries = 3;
  
  while (!token && tokenRetryCount < maxTokenRetries) {
    try {
      console.log(`Attempting to get auth token (attempt ${tokenRetryCount + 1}/${maxTokenRetries})`);
      const { data, error } = await supabase.auth.getSession();
      
      if (error) {
        console.error('Error getting auth session:', error);
        throw error;
      }
      
      token = data?.session?.access_token || null;
      
      if (!token) {
        // If token is still null after getSession, try refreshing the session
        console.log('No token found, attempting to refresh session...');
        const { data: refreshData, error: refreshError } = await supabase.auth.refreshSession();
        
        if (refreshError) {
          console.error('Error refreshing session:', refreshError);
          throw refreshError;
        }
        
        token = refreshData?.session?.access_token || null;
      }
      
      if (!token) {
        console.warn('Failed to get token, will retry...');
        tokenRetryCount++;
        // Wait before retrying with exponential backoff
        await new Promise(resolve => setTimeout(resolve, 1000 * Math.pow(2, tokenRetryCount)));
      }
    } catch (error) {
      console.error('Error retrieving auth token:', error);
      tokenRetryCount++;
      // Wait before retrying
      await new Promise(resolve => setTimeout(resolve, 1000 * Math.pow(2, tokenRetryCount)));
    }
  }
  
  if (!token) {
    const error = new Error('Failed to retrieve authentication token after multiple attempts');
    console.error(error);
    onError(error);
    onConnectionChange(false); 
    throw error;
  }
  
  console.log('Successfully retrieved auth token');
  
  // Create WebSocket connection
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  let wsHost: string;
  
  try {
    wsHost = process.env.NEXT_PUBLIC_API_URL ? 
      new URL(process.env.NEXT_PUBLIC_API_URL).host : 
      window.location.host;
  } catch (error) {
    console.error('Error parsing API URL:', error);
    wsHost = window.location.host; // Fallback to current host
  }
  
  const wsUrl = `${wsProtocol}//${wsHost}/api/research/messages/ws/${searchId}?token=${encodeURIComponent(token)}`;
  
  // Reconnection settings
  const maxReconnectAttempts = 5;
  const baseReconnectDelay = 1000; // 1 second
  let reconnectAttempts = 0;
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  let pingInterval: ReturnType<typeof setInterval> | null = null;
  let heartbeatTimeout: ReturnType<typeof setTimeout> | null = null;
  
  console.log(`Connecting to WebSocket at ${wsUrl}`);
  let socket = new WebSocket(wsUrl);
  let isConnected = false;
  let isReconnecting = false;
  let manualDisconnect = false;
  
  // Function to clear all timers
  const clearTimers = () => {
    if (pingInterval) {
      clearInterval(pingInterval);
      pingInterval = null;
    }
    if (heartbeatTimeout) {
      clearTimeout(heartbeatTimeout);
      heartbeatTimeout = null;
    }
    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }
  };
  
  // Function to handle reconnection
  const reconnect = async () => {
    if (manualDisconnect || isReconnecting) return;
    
    isReconnecting = true;
    
    if (reconnectAttempts >= maxReconnectAttempts) {
      console.error(`Failed to reconnect after ${maxReconnectAttempts} attempts`);
      onError(new Error(`Failed to reconnect after ${maxReconnectAttempts} attempts`));
      isReconnecting = false;
      return;
    }
    
    // Clear any existing timers
    clearTimers();
    
    // Calculate delay with exponential backoff
    const delay = baseReconnectDelay * Math.pow(2, reconnectAttempts);
    console.log(`Attempting to reconnect in ${delay}ms (attempt ${reconnectAttempts + 1}/${maxReconnectAttempts})`);
    
    reconnectTimer = setTimeout(async () => {
      reconnectAttempts++;
      
      try {
        // Get a fresh token in case the old one expired
        const freshHeaders = await getAuthHeader();
        const freshToken = freshHeaders.Authorization.replace('Bearer ', '');
        const freshUrl = `${wsProtocol}//${wsHost}/api/research/messages/ws/${searchId}?token=${freshToken}`;
        
        // Create a new socket
        socket = new WebSocket(freshUrl);
        
        // Set up event listeners for the new socket
        setupEventListeners();
      } catch (error) {
        console.error('Error during reconnection:', error);
        isReconnecting = false;
        reconnect(); // Try again
      }
    }, delay);
  };
  
  // Function to set up event listeners
  const setupEventListeners = () => {
    // Connection opened
    socket.addEventListener('open', () => {
      console.log('WebSocket connection established');
      isConnected = true;
      isReconnecting = false;
      reconnectAttempts = 0; // Reset reconnect attempts on successful connection
      
      // Notify about connection state change
      onConnectionChange(true);
      
      // Subscribe to all message types
      socket.send(JSON.stringify({
        command: 'subscribe',
        message_types: ['user', 'assistant']
      }));
      
      // Set up ping interval (every 25 seconds)
      pingInterval = setInterval(() => {
        if (socket.readyState === WebSocket.OPEN) {
          socket.send(JSON.stringify({
            command: 'ping',
            timestamp: Date.now()
          }));
        }
      }, 25000);
    });
    
    // Listen for messages
    socket.addEventListener('message', (event) => {
      try {
        const message = JSON.parse(event.data) as WebSocketMessage;
        console.log('Received WebSocket message:', message);
        
        // Handle heartbeat messages
        if (message.type === 'heartbeat' || message.type === 'pong') {
          // Reset heartbeat timeout
          if (heartbeatTimeout) {
            clearTimeout(heartbeatTimeout);
          }
          
          // Set a new timeout - if we don't receive a heartbeat within 70 seconds, reconnect
          heartbeatTimeout = setTimeout(() => {
            console.warn('No heartbeat received, reconnecting...');
            socket.close();
            reconnect();
          }, 70000);
          
          // Don't forward heartbeat messages to the client
          if (message.type === 'heartbeat') {
            return;
          }
        }
        
        onMessage(message);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
        onError(error);
      }
    });
    
    // Listen for errors
    socket.addEventListener('error', (event) => {
      console.error('WebSocket error:', event);
      onError(event);
    });
    
    // Listen for connection close
    socket.addEventListener('close', (event) => {
      console.log(`WebSocket connection closed: ${event.code} ${event.reason}`);
      isConnected = false;
      
      // Clear intervals
      clearTimers();
      
      onConnectionChange(false);
      
      // Attempt to reconnect unless manually disconnected
      if (!manualDisconnect) {
        reconnect();
      }
    });
  };
  
  // Set up initial event listeners
  setupEventListeners();
  
  // Return connection interface
  return {
    disconnect: () => {
      manualDisconnect = true;
      clearTimers();
      
      if (socket.readyState === WebSocket.OPEN) {
        socket.close();
      }
    },
    send: (data: any) => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify(data));
      } else if (!manualDisconnect) {
        console.warn('Cannot send message: WebSocket is not open, queuing reconnect');
        reconnect();
      } else {
        console.warn('Cannot send message: WebSocket was manually disconnected');
      }
    },
    get isConnected() {
      return isConnected;
    }
  };
}

/**
 * Helper function to request latest messages via WebSocket
 * @param connection The WebSocketConnection to use
 * @param limit Maximum number of messages to retrieve
 * @param offset Pagination offset
 */
export function requestLatestMessages(connection: WebSocketConnection, limit: number = 10, offset: number = 0): void {
  if (!connection.isConnected) {
    console.warn('Cannot request messages: WebSocket is not connected');
    return;
  }
  
  connection.send({
    command: 'get_latest',
    limit,
    offset
  });
}

/**
 * Helper function to notify the server that the user is typing
 * @param connection The WebSocketConnection to use
 */
export function sendTypingNotification(connection: WebSocketConnection): void {
  if (!connection.isConnected) return;
  
  connection.send({
    command: 'typing'
  });
}
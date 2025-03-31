// src/hooks/research/use-sse.tsx

"use client"

import { useCallback, useEffect, useRef, useState } from 'react';
import { connectToSSE, SSEConnection, SSEEventType } from '@/services/research/research-api';
import { ResearchSession, ConnectionStatus, ErrorType, Message } from '@/contexts/research/research-context';

interface ValidatedMessageData {
  messages?: Message[];
  text?: string;
  type?: string;
}

export function useSSE(
  sessionId: string,
  setCurrentSession: (session: ResearchSession | null | ((prev: ResearchSession | null) => ResearchSession | null)) => void,
  setError: (error: ErrorType | null) => void
) {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>(ConnectionStatus.DISCONNECTED);
  const [connectionMetrics, setConnectionMetrics] = useState({
    lastHeartbeat: null as number | null,
    reconnectAttempts: 0,
    messageCount: 0,
    lastLatency: 0,
  });

  const sseConnectionRef = useRef<SSEConnection | null>(null);
  const lastHeartbeatRef = useRef<number | null>(null);

  const validateMessageData = (data: any): ValidatedMessageData => {
    if (!data) return {};
    if (Array.isArray(data)) return { messages: data };
    if (typeof data === 'object') {
      return {
        messages: Array.isArray(data.messages) ? data.messages : undefined,
        text: typeof data.text === 'string' ? data.text : undefined,
        type: typeof data.type === 'string' ? data.type : undefined,
      };
    }
    return {};
  };

  const connectToStream = useCallback(async () => {
    if (!sessionId) return;

    const updateConnectionMetrics = (metrics: Partial<typeof connectionMetrics>) => {
      setConnectionMetrics(prev => ({ ...prev, ...metrics }));
    };

    const handleConnectionStateChange = (newStatus: ConnectionStatus) => {
      setConnectionStatus(newStatus);
      setIsConnected(newStatus === ConnectionStatus.CONNECTED);
      if (newStatus === ConnectionStatus.CONNECTED) {
        updateConnectionMetrics({ reconnectAttempts: 0 });
      }
    };

    const attemptConnection = async () => {
      try {
        handleConnectionStateChange(ConnectionStatus.CONNECTING);
        if (sseConnectionRef.current) {
          sseConnectionRef.current.disconnect();
          sseConnectionRef.current = null;
        }

        const startTime = Date.now();
        const connection = await connectToSSE(sessionId, {
          onMessage: (message) => {
            try {
              console.log('Received SSE message:', message);
              const validatedData = validateMessageData(message.data);

              updateConnectionMetrics({
                messageCount: connectionMetrics.messageCount + 1,
                lastLatency: Date.now() - startTime,
              });

              if (message.type === SSEEventType.HEARTBEAT) {
                lastHeartbeatRef.current = Date.now();
                return;
              }

              const messages = validatedData.messages;
              if (message.type === SSEEventType.MESSAGES && Array.isArray(messages) && messages.length > 0) {
                setCurrentSession(prev => {
                  if (!prev || prev.id !== sessionId) return prev;
                  
                  const processedMessages = messages.map(m => ({
                    ...m,
                    id: m.id || `msg-${Date.now()}-${Math.random().toString(36).substring(2, 11)}`,
                  }));
                  
                  const existingMessages = new Map(prev.messages?.map(m => [m.id, m]) ?? []);
                  const newMessages = processedMessages.filter(m => !existingMessages.has(m.id));
                  if (newMessages.length === 0) return prev;
                  
                  const mergedMessages = [...(prev.messages ?? []), ...newMessages]
                    .sort((a, b) => a.sequence - b.sequence);
                  
                  const uniqueMessages = Array.from(
                    new Map(mergedMessages.map(m => [m.id, m])).values()
                  );
                  
                  return {
                    ...prev,
                    messages: uniqueMessages,
                    updated_at: new Date().toISOString()
                  };
                });
              } else if (message.type === SSEEventType.CONNECTION_ESTABLISHED) {
                handleConnectionStateChange(ConnectionStatus.CONNECTED);
              } else if (message.type === SSEEventType.ASSISTANT_CHUNK && typeof validatedData.text === 'string') {
                const chunkText = validatedData.text;
                setCurrentSession(prev => {
                  if (!prev || prev.id !== sessionId) return prev;
                  
                  const messages = prev.messages ?? [];
                  const lastMessage = messages[messages.length - 1];
                  
                  if (lastMessage?.role === 'assistant' && !lastMessage.content.text.endsWith('\n')) {
                    const updatedMessages = [...messages.slice(0, -1), {
                      ...lastMessage,
                      content: {
                        ...lastMessage.content,
                        text: lastMessage.content.text + chunkText
                      },
                      updated_at: new Date().toISOString()
                    }];
                    
                    return {
                      ...prev,
                      messages: updatedMessages,
                      updated_at: new Date().toISOString()
                    };
                  }
                  
                  const newMessage: Message = {
                    id: `chunk-${Date.now()}-${Math.random().toString(36).substring(2, 11)}`,
                    role: 'assistant',
                    content: { text: chunkText },
                    sequence: (lastMessage?.sequence ?? 0) + 1
                  };
                  
                  return {
                    ...prev,
                    messages: [...messages, newMessage],
                    updated_at: new Date().toISOString()
                  };
                });
              }
            } catch (err) {
              console.error('Error processing SSE message:', err);
            }
          },
          onError: async (error) => {
            console.error('SSE error:', error);
            handleConnectionStateChange(ConnectionStatus.ERROR);
            
            const metrics = connectionMetrics.reconnectAttempts;
            if (metrics < 5) {
              handleConnectionStateChange(ConnectionStatus.RECONNECTING);
              const delay = Math.min(1000 * Math.pow(2, metrics), 30000);
              
              console.log(`Attempting reconnection ${metrics + 1}/5 in ${delay}ms`);
              updateConnectionMetrics({ reconnectAttempts: metrics + 1 });
              
              setTimeout(attemptConnection, delay);
            } else {
              setError({
                message: 'Connection lost',
                details: 'Maximum reconnection attempts reached. Please refresh the page.',
                code: 'MAX_RECONNECT_ATTEMPTS'
              });
            }
          },
          onConnectionChange: (connected) => {
            handleConnectionStateChange(connected ? ConnectionStatus.CONNECTED : ConnectionStatus.DISCONNECTED);
            if (!connected) sseConnectionRef.current = null;
          }
        });
        
        sseConnectionRef.current = connection;
        lastHeartbeatRef.current = Date.now();
        setError(null);
        
      } catch (error) {
        console.error('Failed to connect to SSE:', error);
        handleConnectionStateChange(ConnectionStatus.ERROR);
        
        if (connectionMetrics.reconnectAttempts >= 5) {
          setError({
            message: 'Failed to establish real-time connection',
            details: error instanceof Error ? error.message : 'Unknown error',
            code: 'SSE_CONNECTION_ERROR'
          });
        }
        throw error;
      }
    };
    
    await attemptConnection();
  }, [sessionId, setCurrentSession, setError, connectionMetrics.messageCount, connectionMetrics.reconnectAttempts]);

  const disconnectStream = useCallback(() => {
    if (sseConnectionRef.current) {
      sseConnectionRef.current.disconnect();
      sseConnectionRef.current = null;
      setIsConnected(false);
      lastHeartbeatRef.current = null;
    }
  }, []);

  useEffect(() => {
    return () => disconnectStream();
  }, [disconnectStream]);

  useEffect(() => {
    if (!isConnected || !lastHeartbeatRef.current) return;

    const intervalId = setInterval(() => {
      const now = Date.now();
      if (now - lastHeartbeatRef.current! > 30000) {
        console.warn('No heartbeat received for 30 seconds, initiating reconnection');
        setError({
          message: 'Connection stale',
          details: 'No heartbeat received from server. Attempting to reconnect...',
          code: 'STALE_CONNECTION'
        });
        disconnectStream();
        if (sessionId) {
          connectToStream().catch(error => {
            console.error('Failed to reconnect after stale connection:', error);
          });
        }
      }
    }, 5000);

    return () => clearInterval(intervalId);
  }, [isConnected, sessionId, connectToStream, disconnectStream, setError]);

  return {
    isConnected,
    connectionStatus,
    connectionMetrics,
    connectToStream,
    disconnectStream,
  };
}
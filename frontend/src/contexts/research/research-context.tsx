// src/contexts/research/research-context.tsx

"use client"

import React, { createContext, useContext, useState, useEffect, useCallback, useMemo, ReactNode } from 'react'
import { 
  fetchSessions, 
  fetchSession, 
  createNewSession, 
  updateSessionMetadata as updateSessionApi, 
  deleteSession as deleteSessionApi, 
  sendSessionMessage as sendMessageApi, 
  connectToMessageUpdates, 
  WebSocketConnection,
  WebSocketMessage,
  requestLatestMessages,
  sendTypingNotification,
  formatApiError,
  cache,
  ApiError
} from "@/services/research/research-api"
import { supabase } from "@/lib/supabase";
import authManager from '@/lib/auth-manager';

// Define enum types that mirror the backend
export enum QueryCategory {
  CLEAR = "clear",
  UNCLEAR = "unclear",
  IRRELEVANT = "irrelevant",
  BORDERLINE = "borderline"
}

export enum QueryType {
  COURT_CASE = "court_case",
  LEGISLATIVE = "legislative",
  COMMERCIAL = "commercial",
  GENERAL = "general"
}

export enum QueryStatus {
  PENDING = "pending",
  COMPLETED = "completed",
  FAILED = "failed",
  NEEDS_CLARIFICATION = "needs_clarification",
  IRRELEVANT = "irrelevant_query"
}

export interface Citation {
  text: string
  url: string
  metadata?: Record<string, any>
}

export interface Message {
  id: string
  role: "user" | "assistant" | "system"
  content: { text: string, citations?: Citation[] }
  sequence: number
  status?: QueryStatus
}

export interface SearchParams {
  temperature?: number
  max_tokens?: number
  top_p?: number
  top_k?: number
  jurisdiction?: string
  query_type?: QueryType
}

export interface ResearchSession {
  id: string
  title: string
  query: string
  description?: string
  is_featured: boolean
  tags?: string[]
  search_params?: SearchParams
  messages?: Message[]
  created_at: string
  updated_at: string
  status: QueryStatus
  category?: QueryCategory
  query_type?: QueryType
  user_id: string
  enterprise_id?: string
}

export interface SearchListResponse {
  items: ResearchSession[]
  total: number
  offset: number
  limit: number
}

type ErrorType = {
  message: string
  code?: string
  details?: string
}

interface ResearchContextType {
  sessions: ResearchSession[]
  currentSession: ResearchSession | null
  isLoading: boolean
  loadingStates: {
    fetchingSessions: boolean
    fetchingSession: boolean
    creatingSession: boolean
    sendingMessage: boolean
    updatingSession: boolean
    deletingSession: boolean
  }
  error: ErrorType | null
  createSession: (query: string, searchParams?: SearchParams) => Promise<string>
  sendMessage: (sessionId: string, content: string) => Promise<void>
  getSession: (sessionId: string) => Promise<void>
  getSessions: (options?: {
    featuredOnly?: boolean
    status?: QueryStatus
    limit?: number
    offset?: number
    append?: boolean
    skipAuthCheck?: boolean
  }) => Promise<void>
  updateSession: (sessionId: string, updates: {
    title?: string
    description?: string
    is_featured?: boolean
    tags?: string[]
    category?: QueryCategory
    query_type?: QueryType
    status?: QueryStatus
  }) => Promise<void>
  deleteSession: (sessionId: string) => Promise<void>
  clearError: () => void
  totalSessions: number
  isConnected: boolean
  connectToWebSocket: (sessionId: string) => Promise<void>
  disconnectWebSocket: () => void
  clearCache: () => void
}

const ResearchContext = createContext<ResearchContextType | undefined>(undefined)

export function ResearchProvider({ children }: { children: ReactNode }) {
  const [sessions, setSessions] = useState<ResearchSession[]>([])
  const [currentSession, setCurrentSession] = useState<ResearchSession | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [loadingStates, setLoadingStates] = useState({
    fetchingSessions: false,
    fetchingSession: false,
    creatingSession: false,
    sendingMessage: false,
    updatingSession: false,
    deletingSession: false
  })
  const [error, setError] = useState<ErrorType | null>(null)
  const [totalSessions, setTotalSessions] = useState(0)
  const [isConnected, setIsConnected] = useState(false)
  const [wsConnection, setWsConnection] = useState<WebSocketConnection | null>(null)
  const [reconnectionAttempts, setReconnectionAttempts] = useState(0)
  const [lastHeartbeat, setLastHeartbeat] = useState<number | null>(null)

  // Add auth state tracking
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authChecked, setAuthChecked] = useState(false);

  // Use useCallback to memoize the clearError function to prevent infinite loops
  const clearError = useCallback(() => setError(null), [setError])

  const handleApiError = (err: any, defaultMessage: string): ErrorType => {
    // Guard against undefined or null errors
    if (!err) {
      console.error(`API Error: ${defaultMessage}`, 'Error object is undefined or null')
      return {
        message: defaultMessage,
        details: 'An unknown error occurred',
        code: 'UNKNOWN_ERROR'
      }
    }

    console.error(`API Error: ${defaultMessage}`, err)
    
    // Handle connection errors
    if (err instanceof Error && 
        ((err as any).code === 'ECONNRESET' || 
         err.message.includes('socket hang up') ||
         err.message.includes('network') ||
         err.message.includes('connection') ||
         err.message.includes('timeout'))) {
      return {
        message: 'Connection Error',
        details: 'Could not connect to the server. Please check that the backend server is running and try again.',
        code: 'CONNECTION_ERROR'
      }
    }
    
    // Handle authentication errors
    if (err instanceof Error && 
        (err.message.toLowerCase().includes('authentication') || 
         err.message.toLowerCase().includes('auth') || 
         err.message.toLowerCase().includes('token') || 
         err.message.toLowerCase().includes('login') || 
         err.message.toLowerCase().includes('unauthorized') || 
         err.message.toLowerCase().includes('sign in') || 
         (err as any).code === 'UNAUTHORIZED' || 
         (err as any).status === 401)) {
      // Attempt to refresh the session when we detect auth errors
      try {
        // Don't await this - we don't want to block the error handler
        supabase.auth.refreshSession().then(() => {
          console.log('Auth session refreshed after error');
        }).catch(refreshError => {
          console.error('Failed to refresh session:', refreshError);
        });
      } catch (refreshError) {
        console.error('Error attempting to refresh session:', refreshError);
      }
      
      return {
        message: 'Authentication Error',
        details: 'Your session may have expired. Please try refreshing the page or logging in again.',
        code: 'AUTH_ERROR'
      }
    }
    
    // Handle certificate-related errors specifically
    if (err instanceof Error && 
        (err.message.includes('certificate') || 
         err.message.includes('SSL') || 
         err.message.includes('UNABLE_TO_VERIFY_LEAF_SIGNATURE') || 
         (err as any).code === 'UNABLE_TO_VERIFY_LEAF_SIGNATURE')) {
      return {
        message: 'SSL Certificate Error',
        details: 'There was an issue with the SSL certificate. This is likely a development environment issue. Please check your server configuration.',
        code: 'CERTIFICATE_ERROR'
      }
    }
    
    if (err && 'status' in err) {
      // Use the formatApiError function from research-api.ts
      const formattedError = formatApiError(err, defaultMessage)
      
      // Convert details to string if needed
      let detailsStr = formattedError.statusText || ''
      if (formattedError.details) {
        try {
          // If it's already a string, use it directly
          if (typeof formattedError.details === 'string') {
            detailsStr = formattedError.details
          } else {
            // Otherwise stringify it
            detailsStr = JSON.stringify(formattedError.details)
          }
        } catch (e) {
          console.error('Error stringifying details:', e)
          detailsStr = 'Error details could not be displayed'
        }
      }
      
      return {
        message: formattedError.message,
        code: formattedError.code,
        details: detailsStr
      }
    }
    
    if (err instanceof Error) {
      return {
        message: defaultMessage,
        details: err.message
      }
    }
    
    return {
      message: defaultMessage,
      details: 'Unknown error occurred'
    }
  }

  const updateSessionInList = (updatedSession: ResearchSession) => {
    setSessions(prevSessions => {
      const index = prevSessions.findIndex(s => s.id === updatedSession.id)
      if (index === -1) {
        // Session doesn't exist in list, add it
        return [...prevSessions, updatedSession]
      } else {
        // Update existing session
        const newSessions = [...prevSessions]
        newSessions[index] = updatedSession
        return newSessions
      }
    })
  }

  // Check authentication status on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession();
        setIsAuthenticated(!!session);
      } catch (error) {
        console.error('Error checking auth status:', error);
        setIsAuthenticated(false);
      } finally {
        setAuthChecked(true);
      }
    };

    checkAuth();

    // Subscribe to auth state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setIsAuthenticated(!!session);
    });

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  const getSessions = useCallback(async (options?: {
    featuredOnly?: boolean
    status?: QueryStatus
    limit?: number
    offset?: number
    append?: boolean
    skipAuthCheck?: boolean
  }) => {
    if (!options?.skipAuthCheck && !isAuthenticated) {
      console.error('Authentication required for getSessions');
      setError({
        message: 'Authentication required',
        details: 'Please log in to view research sessions',
        code: 'AUTH_REQUIRED'
      });
      return;
    }

    setLoadingStates(prev => ({ ...prev, fetchingSessions: true }))
    setIsLoading(true)
    setError(null)
    
    try {
      console.log('getSessions called with options:', options);
      
      // Use the API service to fetch sessions
      const data = await fetchSessions(options)
      
      // Check if we received empty results due to authentication issues
      if (data.items.length === 0 && data.total === 0 && !options?.skipAuthCheck) {
        console.log('Received empty results, checking if this is due to authentication issues');
        // Check if user is logged in
        const { data: sessionData } = await supabase.auth.getSession();
        if (!sessionData.session) {
          console.warn('User is not logged in, setting auth error');
          setError({
            message: "Please log in to view your research sessions",
            details: "Your session may have expired",
            code: "AUTH_REQUIRED"
          });
          setSessions([])
          setTotalSessions(0)
          setLoadingStates(prev => ({ ...prev, fetchingSessions: false }))
          setIsLoading(false)
          return;
        } else {
          // User is logged in but we still got empty results
          // Try refreshing the token
          console.log('User is logged in but received empty results, attempting to refresh token');
          try {
            const { data: refreshData, error: refreshError } = await supabase.auth.refreshSession();
            if (refreshError) {
              console.error('Failed to refresh token:', refreshError);
            } else if (refreshData.session) {
              console.log('Token refreshed successfully, retrying operation');
              // Don't retry here to avoid potential infinite loops
              // Just inform the user to try again
              setError({
                message: "Authentication refreshed",
                details: "Please try again",
                code: "AUTH_REFRESHED"
              });
            }
          } catch (refreshError) {
            console.error('Error refreshing token:', refreshError);
          }
        }
      }
      
      // Validate the response structure and provide fallbacks
      const validatedData = {
        items: Array.isArray(data.items) ? data.items : [],
        total: typeof data.total === 'number' ? data.total : 0,
        offset: typeof data.offset === 'number' ? data.offset : (options?.offset || 0),
        limit: typeof data.limit === 'number' ? data.limit : (options?.limit || 10)
      }
      
      // Either append or replace sessions based on the append flag
      setSessions(prev => options?.append ? [...prev, ...validatedData.items] : validatedData.items)
      setTotalSessions(validatedData.total)
      
      console.log('Successfully loaded sessions:', {
        count: validatedData.items.length,
        total: validatedData.total
      });
    } catch (err) {
      console.error('Error in getSessions:', err)
      
      // Handle the case where err might be undefined or null
      if (!err) {
        setError({
          message: "Failed to fetch research searches",
          details: "An unknown error occurred",
          code: "UNKNOWN_ERROR"
        })
      } else if (err instanceof Error && err.message.includes('307')) {
        setError({
          message: "Temporary Redirect",
          details: "The server is redirecting your request. Please try again later.",
          code: "TEMPORARY_REDIRECT"
        })
      } else {
        setError(handleApiError(err, "Failed to fetch research searches"))
      }
      
      // Only clear sessions if not appending and there was an error
      if (!options?.append) {
        setSessions([])
        setTotalSessions(0)
      }
    } finally {
      setLoadingStates(prev => ({ ...prev, fetchingSessions: false }))
      setIsLoading(false)
    }
  }, [isAuthenticated]);

  // Don't try to fetch sessions until auth state is checked
  useEffect(() => {
    if (authChecked && isAuthenticated) {
      getSessions();
    }
  }, [authChecked, isAuthenticated, getSessions]);

  const getSession = async (sessionId: string) => {
    if (!sessionId) return
    
    // Check if we already have this session in our state
    if (currentSession?.id === sessionId) {
      return
    }
    
    // Check cache before making API call
    const cachedSession = cache.getSession(sessionId);
    if (cachedSession) {
      setCurrentSession(cachedSession);
      return;
    }
    
    setLoadingStates(prev => ({ ...prev, fetchingSession: true }))
    setIsLoading(true)
    setError(null)
    
    try {
      const session = await fetchSession(sessionId)
      setCurrentSession(session)
      updateSessionInList(session)
    } catch (err) {
      setError(handleApiError(err, "Failed to fetch research search"))
    } finally {
      setLoadingStates(prev => ({ ...prev, fetchingSession: false }))
      setIsLoading(false)
    }
  }

  const createSession = async (query: string, searchParams?: SearchParams): Promise<string> => {
    const trimmedQuery = query.trim()
    if (!trimmedQuery) {
      const error = new Error("Query cannot be empty")
      setError(handleApiError(error, "Invalid query"))
      throw error
    }

    // Validate minimum query length
    if (trimmedQuery.length < 3) {
      const error = new Error("Query must be at least 3 characters long")
      setError(handleApiError(error, "Invalid query"))
      throw error
    }

    setLoadingStates(prev => ({ ...prev, creatingSession: true }))
    setIsLoading(true)
    setError(null)
    
    try {
      // Use the API service to create a session
      const newSession = await createNewSession(trimmedQuery, searchParams)
      updateSessionInList(newSession)
      cache.clear()
      return newSession.id
    } catch (err) {
      const errorData = handleApiError(err, "Failed to create research search")
      setError(errorData)
      throw new Error(errorData.message)
    } finally {
      setLoadingStates(prev => ({ ...prev, creatingSession: false }))
      setIsLoading(false)
    }
  }

  const sendMessage = async (sessionId: string, content: string): Promise<void> => {
    const trimmedContent = content.trim()
    if (!sessionId?.trim() || !trimmedContent) {
      setError({
        message: "Invalid request",
        details: !sessionId?.trim() ? "Search ID cannot be empty" : "Message content cannot be empty"
      })
      return
    }

    // Validate minimum content length
    if (trimmedContent.length < 3) {
      setError({
        message: "Invalid request",
        details: "Message content must be at least 3 characters long"
      })
      return
    }

    if (!currentSession) {
      setError({
        message: "No active search",
        details: "Please select a search"
      })
      return
    }

    setLoadingStates(prev => ({ ...prev, sendingMessage: true }))
    setIsLoading(true)
    setError(null)
    
    // Create optimistic update with user message
    const optimisticMessage: Message = {
      id: Math.random().toString(36).substr(2, 9), // Generate a random id for the optimistic update
      role: "user",
      content: { text: trimmedContent },
      sequence: currentSession.messages?.length ?? 0
    }
    
    // Create optimistic session update
    const optimisticSession: ResearchSession = {
      ...currentSession,
      messages: [...(currentSession.messages ?? []), optimisticMessage],
      updated_at: new Date().toISOString()
    }
    
    // Apply optimistic update
    setCurrentSession(optimisticSession)
    updateSessionInList(optimisticSession)
    
    try {
      // Use the API service to send a message
      const updatedSession = await sendMessageApi(sessionId, trimmedContent)
      setCurrentSession(updatedSession)
      updateSessionInList(updatedSession)
      cache.invalidateSearch(sessionId)
    } catch (err) {
      // Revert to previous state on error
      setCurrentSession(currentSession)
      setError(handleApiError(err, "Failed to send message"))
    } finally {
      setLoadingStates(prev => ({ ...prev, sendingMessage: false }))
      setIsLoading(false)
    }
  }

  const updateSession = async (sessionId: string, updates: {
    title?: string
    description?: string
    is_featured?: boolean
    tags?: string[]
    category?: QueryCategory
    query_type?: QueryType
    status?: QueryStatus
  }) => {
    if (!sessionId?.trim()) {
      setError({
        message: "Invalid search ID",
        details: "Search ID cannot be empty"
      })
      return
    }

    // Get current session state
    const sessionToUpdate = currentSession?.id === sessionId 
      ? currentSession 
      : sessions.find(s => s.id === sessionId)
    
    if (!sessionToUpdate) {
      setError({
        message: "Session not found",
        details: "Cannot update a session that doesn't exist"
      })
      return
    }

    // Create optimistic update
    const optimisticSession: ResearchSession = {
      ...sessionToUpdate,
      ...updates,
      updated_at: new Date().toISOString()
    }
    
    // Apply optimistic update
    if (currentSession?.id === sessionId) {
      setCurrentSession(optimisticSession)
    }
    updateSessionInList(optimisticSession)
    
    setLoadingStates(prev => ({ ...prev, updatingSession: true }))
    setIsLoading(true)
    setError(null)
    
    try {
      const updatedSession = await updateSessionApi(sessionId, updates)
      // Update with actual server response
      if (currentSession?.id === updatedSession.id) {
        setCurrentSession(updatedSession)
      }
      updateSessionInList(updatedSession)
      cache.invalidateSearch(sessionId)
    } catch (err) {
      // Revert to previous state on error
      if (currentSession?.id === sessionId) {
        setCurrentSession(sessionToUpdate)
      }
      updateSessionInList(sessionToUpdate)
      setError(handleApiError(err, "Failed to update search"))
    } finally {
      setLoadingStates(prev => ({ ...prev, updatingSession: false }))
      setIsLoading(false)
    }
  }

  const deleteResearchSession = async (sessionId: string) => {
    if (!sessionId?.trim()) {
      setError({
        message: "Invalid search ID",
        details: "Search ID cannot be empty"
      })
      return
    }

    setLoadingStates(prev => ({ ...prev, deletingSession: true }))
    setIsLoading(true)
    setError(null)
    
    // Store current state for potential rollback
    const previousSessions = [...sessions]
    const previousCurrentSession = currentSession
    const previousTotal = totalSessions
    
    // Optimistic update - remove from state immediately
    setSessions(prev => prev.filter(s => s.id !== sessionId))
    if (currentSession?.id === sessionId) {
      setCurrentSession(null)
    }
    setTotalSessions(totalSessions - 1)
    
    try {
      await deleteSessionApi(sessionId)
      // Already updated the UI optimistically, no need to do it again
      cache.invalidateSearch(sessionId)
      cache.clear()
    } catch (err) {
      // Rollback on error
      setSessions(previousSessions)
      setTotalSessions(previousTotal)
      if (currentSession?.id === sessionId) {
        setCurrentSession(previousCurrentSession)
      }
      setError(handleApiError(err, 'Failed to delete session'))
    } finally {
      setLoadingStates(prev => ({ ...prev, deletingSession: false }))
    }
  }

  const connectToWebSocket = async (sessionId: string) => {
    if (!sessionId) return;
    
    // Disconnect any existing connection
    disconnectWebSocket();
    
    // Reset reconnection attempts counter
    setReconnectionAttempts(0);
    
    try {
      const connection = await connectToMessageUpdates(
        sessionId,
        (message: WebSocketMessage) => {
          // Handle incoming WebSocket messages
          console.log('Received WebSocket message:', message);
          
          // Track heartbeats for connection health monitoring
          if (message.type === 'heartbeat' || message.type === 'pong') {
            setLastHeartbeat(Date.now());
            return; // Don't process heartbeats further
          }
          
          if (message.type === 'messages' && message.data) {
            // Update the current session with new messages
            setCurrentSession(prev => {
              if (!prev || prev.id !== sessionId) return prev;
              
              // Merge new messages with existing ones, avoiding duplicates
              const existingMessageIds = new Set(prev.messages?.map(m => m.id) ?? [])
              const newMessages = message.data.filter((m: Message) => !existingMessageIds.has(m.id));
              
              if (newMessages.length === 0) return prev;
              
              return {
                ...prev,
                messages: [...(prev.messages ?? []), ...newMessages].sort((a, b) => a.sequence - b.sequence)
              };
            });
          } else if (message.type === 'connection_established') {
            console.log('WebSocket connection established with server');
            // Request the latest messages
            if (connection) {
              requestLatestMessages(connection);
            }
          }
        },
        (error) => {
          console.error('WebSocket error:', error);
          setError({
            message: 'Error in real-time connection',
            details: error.message || 'Unknown error'
          });
          
          // Track reconnection attempts for monitoring connection stability
          setReconnectionAttempts(prev => prev + 1);
          
          // If we've had too many reconnection attempts, show a more specific error
          if (reconnectionAttempts > 3) {
            setError({
              message: 'Unstable connection to research service',
              details: `Connection has been lost ${reconnectionAttempts} times. There may be network issues.`
            });
          }
        },
        (connected) => {
          // Handle connection state changes
          console.log(`WebSocket connection state changed: ${connected ? 'connected' : 'disconnected'}`);
          setIsConnected(connected);
          
          if (!connected) {
            setWsConnection(null);
          }
        }
      );
      
      setWsConnection(connection);
      setLastHeartbeat(Date.now()); // Initialize heartbeat timestamp
      
    } catch (error) {
      console.error('Failed to connect to WebSocket:', error);
      setError(handleApiError(error, 'Failed to establish real-time connection'));
      setReconnectionAttempts(prev => prev + 1);
      setIsConnected(false);
    }
  };

  const disconnectWebSocket = () => {
    if (wsConnection) {
      wsConnection.disconnect();
      setWsConnection(null);
      setIsConnected(false);
    }
  };
  
  // Auto-connect to WebSocket when current session changes
  useEffect(() => {
    if (currentSession?.id && !wsConnection) {
      connectToWebSocket(currentSession.id);
    }
    
    // Cleanup on unmount
    return () => {
      disconnectWebSocket();
    };
  }, [currentSession?.id, wsConnection]);

  // Set up auth event listener
  useEffect(() => {
    // Listen for auth events
    const removeListener = authManager.addListener((event) => {
      console.log('Auth event in research context:', event.type);
      
      // Clear cache on sign out or token refresh failure
      if (event.type === 'SIGNED_OUT' || event.type === 'TOKEN_REFRESH_FAILED') {
        console.log('Clearing research cache due to auth event:', event.type);
        cache.clear();
        setSessions([]);
        setCurrentSession(null);
        setTotalSessions(0);
        
        // Close WebSocket connection if open
        if (wsConnection) {
          wsConnection.disconnect();
          setWsConnection(null);
          setIsConnected(false);
        }
      }
    });
    
    // Clean up listener on unmount
    return () => {
      removeListener();
    };
  }, [wsConnection]);

  const clearCache = () => {
    cache.clear();
  }

  return (
    <ResearchContext.Provider
      value={{
        sessions,
        currentSession,
        isLoading,
        loadingStates,
        error,
        createSession,
        sendMessage,
        getSession,
        getSessions,
        updateSession,
        deleteSession: deleteResearchSession,
        clearError,
        totalSessions,
        isConnected,
        connectToWebSocket,
        disconnectWebSocket,
        clearCache
      }}
    >
      {children}
    </ResearchContext.Provider>
  )
}

// Custom hook to use the research context
export function useResearch() {
  const context = useContext(ResearchContext)
  if (context === undefined) {
    throw new Error("useResearch must be used within a ResearchProvider")
  }
  return context
}
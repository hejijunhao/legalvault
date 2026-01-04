// src/contexts/research/research-context.tsx

"use client"

import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react'
import {
  fetchSessions,
  fetchSession,
  createNewSession,
  updateSessionMetadata as updateSessionApi,
  deleteSession as deleteSessionApi,
  sendSessionMessage as sendMessageApi,
  fetchMessagesForSearch,
  cache,
  ApiError,
  MessageListResponse
} from "@/services/research/research-api"
import { supabase } from "@/lib/supabase";
import { addAuthEventListener } from '@/store/auth-store';

// Import types from centralized location
import {
  QueryCategory,
  QueryType,
  QueryStatus,
  Citation,
  Message,
  SearchParams,
  ResearchSession,
  SearchListResponse,
} from "@/types/research"

// Re-export for backwards compatibility
export {
  QueryCategory,
  QueryType,
  QueryStatus,
  type Citation,
  type Message,
  type SearchParams,
  type ResearchSession,
  type SearchListResponse,
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
  getSession: (sessionId: string) => Promise<ResearchSession | null>
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
  setError: React.Dispatch<React.SetStateAction<ErrorType | null>>
  totalSessions: number
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
  
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [authChecked, setAuthChecked] = useState(false)
  
  const POLLING_INTERVAL = 5000
  const [pollingId, setPollingId] = useState<NodeJS.Timeout | null>(null)
  const [pollFailures, setPollFailures] = useState(0)
  const MAX_POLL_FAILURES = 5

  const clearError = useCallback(() => setError(null), [])

  const handleApiError = (err: any, defaultMessage: string): ErrorType => {
    if (!err) {
      console.error(`API Error: ${defaultMessage}`, 'Error object is undefined or null')
      return { message: defaultMessage, details: 'An unknown error occurred', code: 'UNKNOWN_ERROR' }
    }

    console.error(`API Error: ${defaultMessage}`, err)

    if (err instanceof Error && (err as any).code === 'ECONNRESET' || err.message.includes('socket hang up')) {
      return { message: 'Connection Error', details: 'Could not connect to the server.', code: 'CONNECTION_ERROR' }
    }

    if (err instanceof Error && (err.message.toLowerCase().includes('authentication') || (err as any).status === 401)) {
      return { message: 'Authentication Error', details: 'Your session may have expired.', code: 'AUTH_ERROR' }
    }

    // Handle ApiError instances
    if (err instanceof ApiError) {
      return { message: err.message, details: err.details, code: err.code }
    }

    // Handle regular Error instances
    if (err instanceof Error) {
      return { message: err.message || defaultMessage, details: undefined, code: 'UNKNOWN_ERROR' }
    }

    // Fallback for unknown error types
    return { message: defaultMessage, details: 'An unexpected error occurred', code: 'UNKNOWN_ERROR' }
  }

  const updateSessionInList = useCallback((updatedSession: ResearchSession) => {
    setSessions(prev => {
      const index = prev.findIndex(s => s.id === updatedSession.id)
      if (index === -1) return [...prev, updatedSession]
      const newSessions = [...prev]
      newSessions[index] = updatedSession
      return newSessions
    })
  }, []);

  useEffect(() => {
    const checkAuth = async () => {
      const { data: { session } } = await supabase.auth.getSession()
      setIsAuthenticated(!!session)
      setAuthChecked(true)
    }
    checkAuth()

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setIsAuthenticated(!!session)
    })
    return () => subscription.unsubscribe()
  }, [])

  const getSessions = useCallback(async (options?: {
    featuredOnly?: boolean
    status?: QueryStatus
    limit?: number
    offset?: number
    append?: boolean
    skipAuthCheck?: boolean
  }) => {
    if (!options?.skipAuthCheck && !isAuthenticated) {
      setError({ message: 'Authentication required', details: 'Please log in.', code: 'AUTH_REQUIRED' })
      return
    }

    setLoadingStates(prev => ({ ...prev, fetchingSessions: true }))
    setIsLoading(true)
    setError(null)
    
    try {
      const data = await fetchSessions(options)
      const validatedData = {
        items: Array.isArray(data.items) ? data.items : [],
        total: typeof data.total === 'number' ? data.total : 0,
        offset: options?.offset || 0,
        limit: options?.limit || 10
      }
      
      setSessions(prev => options?.append ? [...prev, ...validatedData.items] : validatedData.items)
      setTotalSessions(validatedData.total)
    } catch (err) {
      setError(handleApiError(err, "Failed to fetch sessions"))
      if (!options?.append) {
        setSessions([])
        setTotalSessions(0)
      }
    } finally {
      setLoadingStates(prev => ({ ...prev, fetchingSessions: false }))
      setIsLoading(false)
    }
  }, [isAuthenticated])

  useEffect(() => {
    if (authChecked && isAuthenticated) getSessions()
  }, [authChecked, isAuthenticated, getSessions])

  const getSession = useCallback(async (sessionId: string): Promise<ResearchSession | null> => {
    if (!sessionId?.trim()) {
      setError({ message: "Invalid session ID", details: "Session ID cannot be empty" })
      return null
    }

    setLoadingStates(prev => ({ ...prev, fetchingSession: true }))
    setIsLoading(true)
    setError(null)
    
    try {
      const session = await fetchSession(sessionId)
      setCurrentSession(session)
      updateSessionInList(session)
      return session
    } catch (err) {
      setError(handleApiError(err, 'Failed to fetch session'))
      return null
    } finally {
      setLoadingStates(prev => ({ ...prev, fetchingSession: false }))
      setIsLoading(false)
    }
  }, [updateSessionInList, setError, setCurrentSession, setIsLoading, setLoadingStates])

  const createSession = async (query: string, searchParams?: SearchParams): Promise<string> => {
    const trimmedQuery = query.trim()
    if (!trimmedQuery || trimmedQuery.length < 3) {
      setError({ message: "Invalid query", details: "Query must be at least 3 characters." })
      throw new Error("Invalid query")
    }

    setLoadingStates(prev => ({ ...prev, creatingSession: true }))
    setIsLoading(true)
    setError(null)
    
    try {
      const newSession = await createNewSession(trimmedQuery, searchParams)
      updateSessionInList(newSession)
      cache.invalidateSearch(newSession.id)
      return newSession.id
    } catch (err) {
      setError(handleApiError(err, "Failed to create session"))
      throw new Error("Failed to create session")
    } finally {
      setLoadingStates(prev => ({ ...prev, creatingSession: false }))
      setIsLoading(false)
    }
  }

  const sendMessage = async (sessionId: string, content: string): Promise<void> => {
    const trimmedContent = content.trim()
    if (!sessionId?.trim() || !trimmedContent || trimmedContent.length < 3) {
      setError({ message: "Invalid request", details: "Session ID and message must be valid." })
      return
    }

    if (!currentSession) {
      setError({ message: "No active session", details: "Please select a session." })
      return
    }

    setLoadingStates(prev => ({ ...prev, sendingMessage: true }))
    setIsLoading(true)
    setError(null)
    
    const previousSession = structuredClone(currentSession)
    const optimisticMessage: Message = {
      id: Math.random().toString(36).substr(2, 9),
      role: "user",
      content: { text: trimmedContent },
      sequence: currentSession.messages?.length ?? 0
    }
    
    const optimisticSession: ResearchSession = {
      ...currentSession,
      messages: [...(currentSession.messages ?? []), optimisticMessage],
      updated_at: new Date().toISOString()
    }
    
    setCurrentSession(optimisticSession)
    updateSessionInList(optimisticSession)
    
    try {
      const updatedSession = await sendMessageApi(sessionId, trimmedContent)
      setCurrentSession(updatedSession)
      updateSessionInList(updatedSession)
      cache.invalidateSearch(sessionId)
    } catch (err) {
      setCurrentSession(previousSession)
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
      setError({ message: "Invalid session ID", details: "Session ID cannot be empty" })
      return
    }

    const sessionToUpdate = currentSession?.id === sessionId 
      ? currentSession 
      : sessions.find(s => s.id === sessionId)
    
    if (!sessionToUpdate) {
      setError({ message: "Session not found", details: "Cannot update non-existent session" })
      return
    }

    const previousSession = structuredClone(sessionToUpdate)
    const optimisticSession: ResearchSession = {
      ...sessionToUpdate,
      ...updates,
      updated_at: new Date().toISOString()
    }
    
    if (currentSession?.id === sessionId) setCurrentSession(optimisticSession)
    updateSessionInList(optimisticSession)
    
    setLoadingStates(prev => ({ ...prev, updatingSession: true }))
    setIsLoading(true)
    setError(null)
    
    try {
      const updatedSession = await updateSessionApi(sessionId, updates)
      if (currentSession?.id === updatedSession.id) setCurrentSession(updatedSession)
      updateSessionInList(updatedSession)
      cache.invalidateSearch(sessionId)
    } catch (err) {
      if (currentSession?.id === sessionId) setCurrentSession(previousSession)
      updateSessionInList(previousSession)
      setError(handleApiError(err, "Failed to update session"))
    } finally {
      setLoadingStates(prev => ({ ...prev, updatingSession: false }))
      setIsLoading(false)
    }
  }

  const deleteResearchSession = async (sessionId: string) => {
    if (!sessionId?.trim()) {
      setError({ message: "Invalid session ID", details: "Session ID cannot be empty" })
      return
    }

    setLoadingStates(prev => ({ ...prev, deletingSession: true }))
    setIsLoading(true)
    setError(null)
    
    const previousSessions = [...sessions]
    const previousCurrentSession = currentSession
    const previousTotal = totalSessions
    
    setSessions(prev => prev.filter(s => s.id !== sessionId))
    if (currentSession?.id === sessionId) setCurrentSession(null)
    setTotalSessions(totalSessions - 1)
    
    try {
      await deleteSessionApi(sessionId)
      cache.invalidateSearch(sessionId)
    } catch (err) {
      setSessions(previousSessions)
      setTotalSessions(previousTotal)
      if (currentSession?.id === sessionId) setCurrentSession(previousCurrentSession)
      setError(handleApiError(err, 'Failed to delete session'))
    } finally {
      setLoadingStates(prev => ({ ...prev, deletingSession: false }))
      setIsLoading(false)
    }
  }

  useEffect(() => {
    if (pollingId) {
      clearInterval(pollingId)
      setPollingId(null)
      setPollFailures(0)
    }
    
    if (currentSession?.id && isAuthenticated) {
      const pollMessages = async () => {
        try {
          if (!currentSession?.id) return
          const messageData: MessageListResponse = await fetchMessagesForSearch(currentSession.id, { limit: 100, offset: 0 })
          
          setCurrentSession(prev => {
            if (!prev || prev.id !== currentSession.id) return prev
            
            const messageMap = new Map(prev.messages?.map(m => [m.id, m]) ?? [])
            messageData.items.forEach(m => messageMap.set(m.id, m))
            const updatedMessages = Array.from(messageMap.values()).sort((a, b) => a.sequence - b.sequence)
            
            return { ...prev, messages: updatedMessages }
          })
          
          setPollFailures(0)
        } catch (err) {
          setPollFailures(prev => prev + 1)
          if (pollFailures + 1 >= MAX_POLL_FAILURES) {
            clearInterval(intervalId)
            setPollingId(null)
            setError({ message: 'Polling stopped due to repeated failures', code: 'POLLING_FAILED' })
          }
        }
      }
      
      pollMessages()
      const intervalId = setInterval(pollMessages, POLLING_INTERVAL)
      setPollingId(intervalId)
      
      return () => {
        clearInterval(intervalId)
        setPollingId(null)
        setPollFailures(0)
      }
    }
  }, [currentSession?.id, isAuthenticated])

  useEffect(() => {
    const removeListener = addAuthEventListener((eventType) => {
      if (eventType === 'SIGNED_OUT') {
        cache.clear()
        setSessions([])
        setCurrentSession(null)
        setTotalSessions(0)
        if (pollingId) clearInterval(pollingId)
      }
    })
    return removeListener
  }, [pollingId])

  const clearCache = () => cache.clear()

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
        setError,
        totalSessions,
        clearCache
      }}
    >
      {children}
    </ResearchContext.Provider>
  )
}

export function useResearch() {
  const context = useContext(ResearchContext)
  if (context === undefined) throw new Error("useResearch must be used within a ResearchProvider")
  return context
}
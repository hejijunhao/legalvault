// src/contexts/research/research-context.tsx

"use client"

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react"
import { 
  fetchSessions, 
  fetchSession, 
  createNewSession, 
  sendSessionMessage,
  updateSessionMetadata,
  deleteSession,
  ApiError
} from "@/services/research/research-api"

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
  role: "user" | "assistant" | "system"
  content: { text: string, citations?: Citation[] }
  sequence: number
}

export interface SearchParams {
  temperature?: number
  max_tokens?: number
  top_p?: number
  top_k?: number
  jurisdiction?: string
}

export interface ResearchSession {
  id: string
  title: string
  query: string
  description?: string
  is_featured: boolean
  tags?: string[]
  search_params?: SearchParams
  messages: Message[]
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
  error: ErrorType | null
  createSession: (query: string, searchParams?: SearchParams) => Promise<string>
  sendMessage: (sessionId: string, content: string) => Promise<void>
  getSession: (sessionId: string) => Promise<void>
  getSessions: (options?: {
    featuredOnly?: boolean
    status?: QueryStatus
    limit?: number
    offset?: number
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
}

const ResearchContext = createContext<ResearchContextType | undefined>(undefined)

export function ResearchProvider({ children }: { children: ReactNode }) {
  const [sessions, setSessions] = useState<ResearchSession[]>([])
  const [currentSession, setCurrentSession] = useState<ResearchSession | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<ErrorType | null>(null)
  const [totalSessions, setTotalSessions] = useState(0)

  const clearError = () => setError(null)

  const handleApiError = (err: any, defaultMessage: string): ErrorType => {
    console.error(`API Error: ${defaultMessage}`, err)
    
    if (err && 'status' in err) {
      // Handle ApiError from our API service
      let message = err.message || defaultMessage
      let code = err.status.toString()
      let details = err.details ? JSON.stringify(err.details) : err.statusText
      
      // Handle specific error codes with user-friendly messages
      if (err.code) {
        code = err.code
        
        // Add specific UI actions or guidance based on error code
        switch (err.code) {
          case 'AUTH_REQUIRED':
            message = 'Your session has expired. Please log in again.'
            // Could trigger a redirect to login page here
            break
          case 'PERMISSION_DENIED':
            message = 'You do not have permission to perform this action.'
            details = 'Please contact your administrator if you need access.'
            break
          case 'RATE_LIMITED':
            if (err.retryAfter) {
              message = `Too many requests. Please try again in ${err.retryAfter} seconds.`
            } else {
              message = 'Too many requests. Please try again in a few moments.'
            }
            details = 'Our system limits the number of requests to ensure optimal performance for all users.'
            break
          case 'PERPLEXITY_RATE_LIMITED':
            message = 'The research service is currently at capacity.'
            details = 'Perplexity API rate limit reached. Please try again in a few minutes.'
            break
          case 'SERVER_ERROR':
            message = 'A server error occurred. Our team has been notified.'
            details = 'Please try again later. If the problem persists, contact support.'
            break
        }
      } else if (err.status === 401) {
        message = 'Authentication required. Please log in again.'
        code = 'AUTH_REQUIRED'
      } else if (err.status === 403) {
        message = 'You do not have permission to perform this action.'
        code = 'PERMISSION_DENIED'
      } else if (err.status === 429) {
        message = 'Too many requests. Please try again later.'
        code = 'RATE_LIMITED'
        
        // Check for Perplexity-specific errors in the message
        if (err.message?.toLowerCase().includes('perplexity') || 
            (typeof err.details === 'string' && err.details.toLowerCase().includes('perplexity')) ||
            err.message?.toLowerCase().includes('sonar') ||
            (typeof err.details === 'string' && err.details.toLowerCase().includes('sonar'))) {
          message = 'The research service is currently at capacity.'
          details = 'Please try again in a few minutes.'
          code = 'PERPLEXITY_RATE_LIMITED'
        }
        
        // Handle retry-after information if available
        if (err.retryAfter) {
          message = `Too many requests. Please try again in ${err.retryAfter} seconds.`
        }
      } else if (err.status >= 500) {
        message = 'A server error occurred. Please try again later.'
        code = 'SERVER_ERROR'
      }
      
      return {
        message,
        code,
        details
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

  const getSessions = async (options?: {
    featuredOnly?: boolean
    status?: QueryStatus
    limit?: number
    offset?: number
  }) => {
    setIsLoading(true)
    setError(null)
    
    try {
      // Use the API service to fetch sessions
      const data = await fetchSessions(options)
      setSessions(data.items)
      setTotalSessions(data.total)
    } catch (err) {
      setError(handleApiError(err, "Failed to fetch research searches"))
    } finally {
      setIsLoading(false)
    }
  }

  const getSession = async (sessionId: string) => {
    if (!sessionId?.trim()) {
      setError({
        message: "Invalid search ID",
        details: "Search ID cannot be empty"
      })
      return
    }

    setIsLoading(true)
    setError(null)
    
    try {
      // Use the API service to fetch a session
      const session = await fetchSession(sessionId)
      setCurrentSession(session)
      updateSessionInList(session)
    } catch (err) {
      setError(handleApiError(err, "Failed to fetch research search"))
    } finally {
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

    setIsLoading(true)
    setError(null)
    
    try {
      // Use the API service to create a session
      const newSession = await createNewSession(trimmedQuery, searchParams)
      updateSessionInList(newSession)
      return newSession.id
    } catch (err) {
      const errorData = handleApiError(err, "Failed to create research search")
      setError(errorData)
      throw new Error(errorData.message)
    } finally {
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

    setIsLoading(true)
    setError(null)
    
    // Create optimistic update with user message
    const optimisticMessage: Message = {
      role: "user",
      content: { text: trimmedContent },
      sequence: currentSession.messages.length
    }
    
    // Create optimistic session update
    const optimisticSession: ResearchSession = {
      ...currentSession,
      messages: [...currentSession.messages, optimisticMessage],
      updated_at: new Date().toISOString()
    }
    
    // Apply optimistic update
    setCurrentSession(optimisticSession)
    updateSessionInList(optimisticSession)
    
    try {
      // Use the API service to send a message
      const updatedSession = await sendSessionMessage(sessionId, trimmedContent)
      setCurrentSession(updatedSession)
      updateSessionInList(updatedSession)
    } catch (err) {
      // Revert to previous state on error
      setCurrentSession(currentSession)
      updateSessionInList(currentSession)
      setError(handleApiError(err, "Failed to send message"))
    } finally {
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
    
    setIsLoading(true)
    setError(null)
    
    try {
      const updatedSession = await updateSessionMetadata(sessionId, updates)
      // Update with actual server response
      if (currentSession?.id === updatedSession.id) {
        setCurrentSession(updatedSession)
      }
      updateSessionInList(updatedSession)
    } catch (err) {
      // Revert to previous state on error
      if (currentSession?.id === sessionId) {
        setCurrentSession(sessionToUpdate)
      }
      updateSessionInList(sessionToUpdate)
      setError(handleApiError(err, "Failed to update search"))
    } finally {
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

    setIsLoading(true)
    setError(null)
    
    // Store current state for potential rollback
    const previousSessions = [...sessions]
    const previousCurrentSession = currentSession
    
    // Optimistic update - remove from state immediately
    setSessions(prev => prev.filter(s => s.id !== sessionId))
    if (currentSession?.id === sessionId) {
      setCurrentSession(null)
    }
    
    try {
      await deleteSession(sessionId)
      // Already updated the UI optimistically, no need to do it again
    } catch (err) {
      // Rollback on error
      setSessions(previousSessions)
      setCurrentSession(previousCurrentSession)
      setError(handleApiError(err, "Failed to delete search"))
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <ResearchContext.Provider
      value={{
        sessions,
        currentSession,
        isLoading,
        error,
        createSession,
        sendMessage,
        getSession,
        getSessions,
        updateSession,
        deleteSession: deleteResearchSession,
        clearError,
        totalSessions
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
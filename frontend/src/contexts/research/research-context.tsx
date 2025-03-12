// src/contexts/research/research-context.tsx

"use client"

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react"
import { 
  fetchSessions, 
  fetchSession, 
  createNewSession, 
  sendSessionMessage 
} from "@/services/research/research-api"

export interface Message {
  role: "user" | "assistant" | "system"
  content: { text: string, citations?: Array<{ text: string, url: string }> }
  sequence: number
}

export interface ResearchSession {
  id: string
  title: string
  query: string
  description?: string
  is_featured: boolean
  tags?: string[]
  search_params?: Record<string, any>
  messages: Message[]
  created_at: string
  updated_at: string
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
  createSession: (query: string) => Promise<string>
  sendMessage: (sessionId: string, content: string) => Promise<void>
  getSession: (sessionId: string) => Promise<void>
  getSessions: () => Promise<void>
  clearError: () => void
}

const ResearchContext = createContext<ResearchContextType | undefined>(undefined)

export function ResearchProvider({ children }: { children: ReactNode }) {
  const [sessions, setSessions] = useState<ResearchSession[]>([])
  const [currentSession, setCurrentSession] = useState<ResearchSession | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<ErrorType | null>(null)

  const clearError = () => setError(null)

  // Helper function to handle API errors
  const handleApiError = (err: any, defaultMessage: string): ErrorType => {
    console.error(`API Error: ${defaultMessage}`, err)
    
    if (err instanceof Response) {
      const message =
        err.status === 404 ? "Search not found" :
        err.status === 401 ? "Authentication required" :
        err.status === 403 ? "Not authorized" :
        err.status === 500 ? "Server error" :
        err.status === 503 ? "Service unavailable" : defaultMessage;
      
      return {
        message,
        code: err.status.toString(),
        details: `HTTP error: ${err.statusText}`
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

  // Update sessions list when a session is modified
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

  // Fetch all research sessions for the current user
  const getSessions = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      // Use the API service to fetch sessions
      const data = await fetchSessions()
      setSessions(data)
    } catch (err) {
      setError(handleApiError(err, "Failed to fetch research searches"))
    } finally {
      setIsLoading(false)
    }
  }

  // Get a specific research session by ID
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

  // Create a new research session
  const createSession = async (query: string): Promise<string> => {
    const trimmedQuery = query.trim()
    if (!trimmedQuery) {
      const error = new Error("Query cannot be empty")
      setError(handleApiError(error, "Invalid query"))
      throw error
    }

    setIsLoading(true)
    setError(null)
    
    try {
      // Use the API service to create a session
      const newSession = await createNewSession(trimmedQuery)
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

  // Send a message in a research session
  const sendMessage = async (sessionId: string, content: string) => {
    const trimmedContent = content.trim()
    if (!sessionId?.trim() || !trimmedContent) {
      setError({
        message: "Invalid request",
        details: !sessionId?.trim() ? "Search ID cannot be empty" : "Message content cannot be empty"
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
    
    try {
      // Use the API service to send a message
      const updatedSession = await sendSessionMessage(sessionId, trimmedContent)
      setCurrentSession(updatedSession)
      updateSessionInList(updatedSession)
    } catch (err) {
      setError(handleApiError(err, "Failed to send message"))
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
        clearError
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
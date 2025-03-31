// src/hooks/research/use-research-api.tsx

"use client"

import { useCallback, useRef } from 'react';
import { 
  fetchSessions, 
  fetchSession, 
  createNewSession, 
  updateSessionMetadata, 
  deleteSession as deleteSessionApi, 
  sendSessionMessage,
  cache,
} from '@/services/research/research-api';
import { supabase } from '@/lib/supabase';
import { 
  ResearchSession, 
  SearchParams,
  SearchListResponse,
  QueryStatus,
  Message,
} from '@/services/research/research-api-types';
import {
  LoadingStates,
  ErrorType
} from '@/contexts/research/research-context';

interface ApiError extends Error {
  code?: string;
  status?: number;
  statusText?: string;
  details?: string | Record<string, any>;
  originalError?: any;
}

export function useResearchApi(
  setError: (error: ErrorType | null) => void,
  setSessions: (sessions: ResearchSession[] | ((prev: ResearchSession[]) => ResearchSession[])) => void,
  setCurrentSession: (session: ResearchSession | null | ((prev: ResearchSession | null) => ResearchSession | null)) => void,
  setLoadingStates: (states: LoadingStates | ((prev: LoadingStates) => LoadingStates)) => void,
  setIsLoading: (loading: boolean) => void,
  setTotalSessions: (total: number) => void
) {
  // Keep local refs of loading states to prevent race conditions
  const loadingStatesRef = useRef<LoadingStates>({
    fetchingSessions: false,
    fetchingSession: false,
    creatingSession: false,
    sendingMessage: false,
    updatingSession: false,
    deletingSession: false
  });

  const updateLoadingState = useCallback((key: keyof LoadingStates, value: boolean) => {
    loadingStatesRef.current[key] = value;
    setLoadingStates(prev => ({ ...prev, [key]: value }));
  }, [setLoadingStates]);

  const getSessions = useCallback(async (options?: { 
    featuredOnly?: boolean; 
    status?: QueryStatus; 
    limit?: number; 
    offset?: number; 
    append?: boolean; 
  }) => {
    if (loadingStatesRef.current.fetchingSessions) {
      return;
    }

    updateLoadingState('fetchingSessions', true);
    
    try {
      const data = await fetchSessions(options);
      setSessions(data.items);
      setTotalSessions(data.total);
    } catch (error) {
      setError({ 
        message: 'Failed to fetch sessions',
        details: error instanceof Error ? error.message : 'Unknown error'
      });
    } finally {
      updateLoadingState('fetchingSessions', false);
    }
  }, [setSessions, setTotalSessions, setError, updateLoadingState]);

  const getSession = useCallback(async (sessionId: string, updateSessionInList: (session: ResearchSession) => void) => {
    if (!sessionId?.trim()) {
      const error = { message: "Invalid search ID", details: "Search ID cannot be empty" };
      setError(error);
      throw new Error(error.message);
    }

    updateLoadingState('fetchingSession', true);
    setIsLoading(true);
    setError(null);

    try {
      const session = await fetchSession(sessionId);
      setCurrentSession(session);
      updateSessionInList(session);
      return session;
    } catch (error) {
      const errorData = { 
        message: 'Failed to fetch session',
        details: error instanceof Error ? error.message : 'Unknown error'
      };
      setError(errorData);
      throw new Error(errorData.message);
    } finally {
      updateLoadingState('fetchingSession', false);
      setIsLoading(false);
    }
  }, [setCurrentSession, setIsLoading, setError, updateLoadingState]);

  const createSession = useCallback(async (
    query: string, 
    searchParams: SearchParams | undefined,
    updateSessionInList: (session: ResearchSession) => void
  ) => {
    const trimmedQuery = query.trim();
    if (!trimmedQuery || trimmedQuery.length < 3) {
      const error = { 
        message: "Invalid query", 
        details: trimmedQuery ? "Query must be at least 3 characters long" : "Query cannot be empty" 
      };
      setError(error);
      throw new Error(error.message);
    }

    updateLoadingState('creatingSession', true);
    setIsLoading(true);
    setError(null);

    try {
      const newSession = await createNewSession(trimmedQuery, searchParams);
      updateSessionInList(newSession);
      cache.clear();
      return newSession.id;
    } catch (error) {
      const errorData = { 
        message: 'Failed to create session',
        details: error instanceof Error ? error.message : 'Unknown error'
      };
      setError(errorData);
      throw new Error(errorData.message);
    } finally {
      updateLoadingState('creatingSession', false);
      setIsLoading(false);
    }
  }, [setIsLoading, setError, updateLoadingState]);

  const sendMessage = useCallback(async (
    sessionId: string,
    content: string,
    currentSession: ResearchSession | null,
    updateSessionInList: (session: ResearchSession) => void
  ) => {
    const trimmedContent = content.trim();
    if (!sessionId?.trim() || !trimmedContent || trimmedContent.length < 3) {
      setError({ 
        message: "Invalid request", 
        details: !sessionId?.trim() 
          ? "Search ID cannot be empty" 
          : trimmedContent 
            ? "Message content must be at least 3 characters long" 
            : "Message content cannot be empty" 
      });
      return;
    }

    if (!currentSession) {
      setError({ message: "No active search", details: "Please select a search" });
      return;
    }

    updateLoadingState('sendingMessage', true);
    setIsLoading(true);
    setError(null);

    try {
      const updatedSession = await sendSessionMessage(sessionId, trimmedContent);
      setCurrentSession(updatedSession);
      updateSessionInList(updatedSession);
      cache.invalidateSearch(sessionId);
    } catch (error) {
      setError({ 
        message: 'Failed to send message',
        details: error instanceof Error ? error.message : 'Unknown error'
      });
    } finally {
      updateLoadingState('sendingMessage', false);
      setIsLoading(false);
    }
  }, [setCurrentSession, setIsLoading, setError, updateLoadingState]);

  const updateSession = useCallback(async (
    sessionId: string,
    updates: Partial<ResearchSession>,
    currentSession: ResearchSession | null,
    updateSessionInList: (session: ResearchSession) => void
  ) => {
    if (!sessionId?.trim()) {
      setError({ message: "Invalid search ID", details: "Search ID cannot be empty" });
      return;
    }

    const sessionToUpdate = currentSession?.id === sessionId ? currentSession : null;
    if (!sessionToUpdate) {
      setError({ message: "Session not found", details: "Cannot update a session that doesn't exist" });
      return;
    }

    updateLoadingState('updatingSession', true);
    setIsLoading(true);
    setError(null);

    try {
      const updatedSession = await updateSessionMetadata(sessionId, updates);
      setCurrentSession(updatedSession);
      updateSessionInList(updatedSession);
      cache.invalidateSearch(sessionId);
    } catch (error) {
      setError({ 
        message: 'Failed to update session',
        details: error instanceof Error ? error.message : 'Unknown error'
      });
    } finally {
      updateLoadingState('updatingSession', false);
      setIsLoading(false);
    }
  }, [setCurrentSession, setIsLoading, setError, updateLoadingState]);

  const deleteSession = useCallback(async (
    sessionId: string,
    sessions: ResearchSession[],
    currentSession: ResearchSession | null,
    setTotalSessions: (total: number) => void
  ) => {
    if (!sessionId?.trim()) {
      setError({ message: "Invalid search ID", details: "Search ID cannot be empty" });
      return;
    }

    updateLoadingState('deletingSession', true);
    setIsLoading(true);
    setError(null);

    try {
      await deleteSessionApi(sessionId);
      cache.invalidateSearch(sessionId);
      cache.clear();
      setSessions(sessions.filter(s => s.id !== sessionId));
      setTotalSessions(sessions.length - 1);
    } catch (error) {
      setError({ 
        message: 'Failed to delete session',
        details: error instanceof Error ? error.message : 'Unknown error'
      });
    } finally {
      updateLoadingState('deletingSession', false);
      setIsLoading(false);
    }
  }, [setSessions, setCurrentSession, setIsLoading, setError, updateLoadingState]);

  return {
    getSessions,
    getSession,
    createSession,
    sendMessage,
    updateSession,
    deleteSession,
    clearCache: cache.clear,
  };
}

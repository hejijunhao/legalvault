// src/hooks/research/use-research-api.tsx

"use client"

import { useCallback } from 'react';
import { 
  fetchSessions, 
  fetchSession, 
  createNewSession, 
  updateSessionMetadata, 
  deleteSession as deleteSessionApi, 
  sendSessionMessage,
  cache,
  formatApiError,
} from '@/services/research/research-api';
import { supabase } from '@/lib/supabase';
import { 
  ResearchSession, 
  SearchParams, 
  SearchListResponse, 
  ErrorType, 
  Message,
  QueryStatus,
  LoadingStates 
} from '@/contexts/research/research-context';

interface ApiError extends Error {
  code?: string;
  status?: number;
  statusText?: string;
}

export function useResearchApi(
  setError: (error: ErrorType | null) => void,
  setSessions: (sessions: ResearchSession[] | ((prev: ResearchSession[]) => ResearchSession[])) => void,
  setCurrentSession: (session: ResearchSession | null | ((prev: ResearchSession | null) => ResearchSession | null)) => void,
  setLoadingStates: (states: LoadingStates | ((prev: LoadingStates) => LoadingStates)) => void,
  setIsLoading: (loading: boolean) => void,
  setTotalSessions: (total: number) => void
) {
  const handleApiError = useCallback((err: any, defaultMessage: string): ErrorType => {
    if (!err) {
      console.error(`API Error: ${defaultMessage}`, 'Error object is undefined or null');
      return { message: defaultMessage, details: 'An unknown error occurred', code: 'UNKNOWN_ERROR' };
    }

    console.error(`API Error: ${defaultMessage}`, err);
    const error = err as ApiError;

    if (error instanceof Error && 
        (error.code === 'ECONNRESET' || 
         error.message.includes('socket hang up') ||
         error.message.includes('network') ||
         error.message.includes('connection') ||
         error.message.includes('timeout'))) {
      return {
        message: 'Connection Error',
        details: 'Could not connect to the server. Please check that the backend server is running and try again.',
        code: 'CONNECTION_ERROR'
      };
    }

    if (error instanceof Error && 
        (error.message.toLowerCase().includes('authentication') || 
         error.message.toLowerCase().includes('auth') || 
         error.message.toLowerCase().includes('token') || 
         error.message.toLowerCase().includes('login') || 
         error.message.toLowerCase().includes('unauthorized') || 
         error.message.toLowerCase().includes('sign in') || 
         error.code === 'UNAUTHORIZED' || 
         error.status === 401)) {
      supabase.auth.refreshSession()
        .then(() => console.log('Auth session refreshed after error'))
        .catch(refreshError => console.error('Failed to refresh session:', refreshError));
      
      return {
        message: 'Authentication Error',
        details: 'Your session may have expired. Please try refreshing the page or logging in again.',
        code: 'AUTH_ERROR'
      };
    }

    if (error instanceof Error && 
        (error.message.includes('certificate') || 
         error.message.includes('SSL') || 
         error.message.includes('UNABLE_TO_VERIFY_LEAF_SIGNATURE') || 
         error.code === 'UNABLE_TO_VERIFY_LEAF_SIGNATURE')) {
      return {
        message: 'SSL Certificate Error',
        details: 'There was an issue with the SSL certificate. This is likely a development environment issue. Please check your server configuration.',
        code: 'CERTIFICATE_ERROR'
      };
    }

    if (error && 'status' in error) {
      const formattedError = formatApiError(error, defaultMessage);
      return {
        message: formattedError.message,
        code: formattedError.code,
        details: typeof formattedError.details === 'string' 
          ? formattedError.details 
          : (formattedError.statusText || JSON.stringify(formattedError.details) || 'Unknown error'),
      };
    }

    return { 
      message: defaultMessage, 
      details: error instanceof Error ? error.message : 'Unknown error occurred' 
    };
  }, []);

  const getSessions = useCallback(async (options?: { 
    featuredOnly?: boolean; 
    status?: QueryStatus; 
    limit?: number; 
    offset?: number; 
    append?: boolean; 
  }) => {
    setLoadingStates(prev => ({ ...prev, fetchingSessions: true }));
    setIsLoading(true);
    setError(null);

    try {
      console.log('getSessions called with options:', options);
      const data: SearchListResponse = await fetchSessions(options);

      if (data.items.length === 0 && data.total === 0) {
        console.log('Received empty results, checking if this is due to authentication issues');
        const { data: sessionData } = await supabase.auth.getSession();
        if (!sessionData.session) {
          console.warn('User is not logged in, setting auth error');
          setError({ message: "Please log in to view your research sessions", details: "Your session may have expired", code: "AUTH_REQUIRED" });
          setSessions([]);
          setTotalSessions(0);
          return;
        } else {
          console.log('User is logged in but received empty results, attempting to refresh token');
          try {
            const { data: refreshData, error: refreshError } = await supabase.auth.refreshSession();
            if (refreshError) console.error('Failed to refresh token:', refreshError);
            else if (refreshData.session) {
              console.log('Token refreshed successfully, retrying operation');
              setError({ message: "Authentication refreshed", details: "Please try again", code: "AUTH_REFRESHED" });
            }
          } catch (refreshError) {
            console.error('Error refreshing token:', refreshError);
          }
        }
      }

      const validatedData = {
        items: Array.isArray(data.items) ? data.items : [],
        total: typeof data.total === 'number' ? data.total : 0,
        offset: typeof data.offset === 'number' ? data.offset : (options?.offset || 0),
        limit: typeof data.limit === 'number' ? data.limit : (options?.limit || 10),
      };

      setSessions(prev => options?.append ? [...prev, ...validatedData.items] : validatedData.items);
      setTotalSessions(validatedData.total);
      console.log('Successfully loaded sessions:', { count: validatedData.items.length, total: validatedData.total });
    } catch (err) {
      console.error('Error in getSessions:', err);
      if (!err) setError({ message: "Failed to fetch research searches", details: "An unknown error occurred", code: "UNKNOWN_ERROR" });
      else if (err instanceof Error && err.message.includes('307')) setError({ message: "Temporary Redirect", details: "The server is redirecting your request. Please try again later.", code: "TEMPORARY_REDIRECT" });
      else setError(handleApiError(err, "Failed to fetch research searches"));
      if (!options?.append) {
        setSessions([]);
        setTotalSessions(0);
      }
    } finally {
      setLoadingStates(prev => ({ ...prev, fetchingSessions: false }));
      setIsLoading(false);
    }
  }, [setError, setSessions, setTotalSessions, setLoadingStates, setIsLoading, handleApiError]);

  const getSession = useCallback(async (sessionId: string, updateSessionInList: (session: ResearchSession) => void) => {
    if (!sessionId?.trim()) {
      setError({ message: "Invalid search ID", details: "Search ID cannot be empty" });
      return null;
    }

    setLoadingStates(prev => ({ ...prev, fetchingSession: true }));
    setIsLoading(true);
    setError(null);

    try {
      const cachedSession = cache.getSession(sessionId);
      if (cachedSession) setCurrentSession(cachedSession);

      const session = await fetchSession(sessionId);
      setCurrentSession(session);
      updateSessionInList(session);
      return session;
    } catch (err) {
      console.error('Failed to fetch research search:', err);
      setError(handleApiError(err, 'Failed to fetch research search'));
      return null;
    } finally {
      setLoadingStates(prev => ({ ...prev, fetchingSession: false }));
      setIsLoading(false);
    }
  }, [setCurrentSession, setLoadingStates, setIsLoading, setError, handleApiError]);

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

    setLoadingStates(prev => ({ ...prev, creatingSession: true }));
    setIsLoading(true);
    setError(null);

    try {
      const newSession = await createNewSession(trimmedQuery, searchParams);
      updateSessionInList(newSession);
      cache.clear();
      return newSession.id;
    } catch (err) {
      const errorData = handleApiError(err, "Failed to create research search");
      setError(errorData);
      throw new Error(errorData?.message || "Failed to create research search");
    } finally {
      setLoadingStates(prev => ({ ...prev, creatingSession: false }));
      setIsLoading(false);
    }
  }, [setLoadingStates, setIsLoading, setError, handleApiError]);

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

    setLoadingStates(prev => ({ ...prev, sendingMessage: true }));
    setIsLoading(true);
    setError(null);

    const optimisticMessage: Message = {
      id: Math.random().toString(36).substr(2, 9),
      role: "user",
      content: { text: trimmedContent },
      sequence: currentSession.messages?.length ?? 0,
    };
    const optimisticSession: ResearchSession = {
      ...currentSession,
      messages: [...(currentSession.messages ?? []), optimisticMessage],
      updated_at: new Date().toISOString(),
    };

    setCurrentSession(optimisticSession);
    updateSessionInList(optimisticSession);

    try {
      const updatedSession = await sendSessionMessage(sessionId, trimmedContent);
      setCurrentSession(updatedSession);
      updateSessionInList(updatedSession);
      cache.invalidateSearch(sessionId);
    } catch (err) {
      setCurrentSession(currentSession);
      setError(handleApiError(err, "Failed to send message"));
    } finally {
      setLoadingStates(prev => ({ ...prev, sendingMessage: false }));
      setIsLoading(false);
    }
  }, [setCurrentSession, setLoadingStates, setIsLoading, setError, handleApiError]);

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

    const optimisticSession: ResearchSession = { 
      ...sessionToUpdate, 
      ...updates, 
      updated_at: new Date().toISOString() 
    };
    if (currentSession?.id === sessionId) setCurrentSession(optimisticSession);
    updateSessionInList(optimisticSession);

    setLoadingStates(prev => ({ ...prev, updatingSession: true }));
    setIsLoading(true);
    setError(null);

    try {
      const updatedSession = await updateSessionMetadata(sessionId, updates);
      if (currentSession?.id === updatedSession.id) setCurrentSession(updatedSession);
      updateSessionInList(updatedSession);
      cache.invalidateSearch(sessionId);
    } catch (err) {
      if (currentSession?.id === sessionId) setCurrentSession(sessionToUpdate);
      updateSessionInList(sessionToUpdate);
      setError(handleApiError(err, "Failed to update search"));
    } finally {
      setLoadingStates(prev => ({ ...prev, updatingSession: false }));
      setIsLoading(false);
    }
  }, [setCurrentSession, setLoadingStates, setIsLoading, setError, handleApiError]);

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

    setLoadingStates(prev => ({ ...prev, deletingSession: true }));
    setIsLoading(true);
    setError(null);

    const previousSessions = [...sessions];
    const previousCurrentSession = currentSession;
    const previousTotal = sessions.length;

    setSessions(prev => prev.filter(s => s.id !== sessionId));
    if (currentSession?.id === sessionId) setCurrentSession(null);
    setTotalSessions(previousTotal - 1);

    try {
      await deleteSessionApi(sessionId);
      cache.invalidateSearch(sessionId);
      cache.clear();
    } catch (err) {
      setSessions(previousSessions);
      setTotalSessions(previousTotal);
      if (currentSession?.id === sessionId) setCurrentSession(previousCurrentSession);
      setError(handleApiError(err, 'Failed to delete session'));
    } finally {
      setLoadingStates(prev => ({ ...prev, deletingSession: false }));
      setIsLoading(false);
    }
  }, [setSessions, setCurrentSession, setLoadingStates, setIsLoading, setError, handleApiError]);

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

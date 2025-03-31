// src/contexts/research/research-provider.tsx

"use client"

import { useState, useCallback, useMemo, useEffect, useRef } from 'react';
import { supabase } from '@/lib/supabase';
import authManager from '@/lib/auth-manager';
import { 
  ResearchContext, 
  ResearchSession, 
  ResearchContextType, 
  ResearchProviderProps,
  ErrorType,
  LoadingStates
} from './research-context';
import { useResearchApi } from '@/hooks/research/use-research-api';
import { useSSE } from '@/hooks/research/use-sse';
import { useAuth } from '@/contexts/auth-context';

export function ResearchProvider({ children }: { children: React.ReactNode }) {
  const [sessions, setSessions] = useState<ResearchSession[]>([]);
  const [currentSession, setCurrentSession] = useState<ResearchSession | null>(null);
  const [totalSessions, setTotalSessions] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStates, setLoadingStates] = useState<LoadingStates>({
    fetchingSessions: false,
    fetchingSession: false,
    creatingSession: false,
    sendingMessage: false,
    updatingSession: false,
    deletingSession: false
  });
  const [error, setError] = useState<ErrorType | null>(null);
  const initialFetchRef = useRef(false);

  const { isAuthenticated: authContextIsAuthenticated, isLoading: authLoading } = useAuth();
  const api = useResearchApi(setError, setSessions, setCurrentSession, setLoadingStates, setIsLoading, setTotalSessions);
  const sse = useSSE(currentSession?.id || '', setCurrentSession, setError);

  const clearError = useCallback(() => setError(null), []);

  const updateSessionInList = useCallback((updatedSession: ResearchSession) => {
    setSessions(prev => {
      const index = prev.findIndex(s => s.id === updatedSession.id);
      if (index === -1) return [...prev, updatedSession];
      const newSessions = [...prev];
      newSessions[index] = updatedSession;
      return newSessions;
    });
  }, []);

  const getSessions = useCallback(async (options?: Parameters<ResearchContextType['getSessions']>[0]) => {
    await api.getSessions(options);
  }, [api]);

  useEffect(() => {
    // Only fetch if authenticated and not already fetched
    if (authContextIsAuthenticated && !initialFetchRef.current) {
      initialFetchRef.current = true;
      getSessions();
    }
  }, [authContextIsAuthenticated, getSessions]);

  const getSession = useCallback(async (sessionId: string) => {
    if (loadingStates.fetchingSession && currentSession?.id === sessionId) {
      console.log('Already fetching this session, skipping duplicate request');
      return currentSession;
    }
    return api.getSession(sessionId, updateSessionInList);
  }, [api, loadingStates.fetchingSession, currentSession, updateSessionInList]);

  const createSession = useCallback(async (query: string, searchParams?: any) => {
    return api.createSession(query, searchParams, updateSessionInList);
  }, [api, updateSessionInList]);

  const sendMessage = useCallback(async (sessionId: string, content: string) => {
    await api.sendMessage(sessionId, content, currentSession, updateSessionInList);
  }, [api, currentSession, updateSessionInList]);

  const updateSession = useCallback(async (sessionId: string, updates: Partial<ResearchSession>) => {
    await api.updateSession(sessionId, updates, currentSession, updateSessionInList);
  }, [api, currentSession, updateSessionInList]);

  const deleteSession = useCallback(async (sessionId: string) => {
    await api.deleteSession(sessionId, sessions, currentSession, setTotalSessions);
  }, [api, sessions, currentSession]);

  useEffect(() => {
    const removeListener = authManager.addListener((event) => {
      console.log('Auth event in research context:', event.type);
      if (event.type === 'SIGNED_OUT' || event.type === 'TOKEN_REFRESH_FAILED') {
        console.log('Clearing research cache due to auth event:', event.type);
        api.clearCache();
        setSessions([]);
        setCurrentSession(null);
        setTotalSessions(0);
        sse.disconnectStream();
      }
    });
    return () => removeListener();
  }, [api, sse]);

  const value = useMemo(() => ({
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
    deleteSession,
    clearError,
    totalSessions,
    isConnected: sse.isConnected,
    connectionStatus: sse.connectionStatus,
    connectionMetrics: sse.connectionMetrics,
    connectToStream: sse.connectToStream,
    disconnectStream: sse.disconnectStream,
    clearCache: api.clearCache,
  }), [
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
    deleteSession,
    clearError,
    totalSessions,
    sse.isConnected,
    sse.connectionStatus,
    sse.connectionMetrics,
    sse.connectToStream,
    sse.disconnectStream,
    api.clearCache,
  ]);

  return (
    <ResearchContext.Provider value={value}>
      {children}
    </ResearchContext.Provider>
  );
}
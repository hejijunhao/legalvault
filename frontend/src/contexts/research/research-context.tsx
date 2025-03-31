// src/contexts/research/research-context.tsx

"use client"

import { createContext, useContext, ReactNode } from 'react';

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

export enum ConnectionStatus {
  DISCONNECTED = 'disconnected',
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  RECONNECTING = 'reconnecting',
  ERROR = 'error'
}

export interface Citation {
  text: string;
  url: string;
  metadata?: Record<string, any>;
}

export interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: { text: string; citations?: Citation[] };
  sequence: number;
  status?: QueryStatus;
}

export interface SearchParams {
  temperature?: number;
  max_tokens?: number;
  top_p?: number;
  top_k?: number;
  jurisdiction?: string;
  query_type?: QueryType;
}

export interface ResearchSession {
  id: string;
  title: string;
  query: string;
  description?: string;
  is_featured: boolean;
  tags?: string[];
  search_params?: SearchParams;
  messages?: Message[];
  created_at: string;
  updated_at: string;
  status: QueryStatus;
  category?: QueryCategory;
  query_type?: QueryType;
  user_id: string;
  enterprise_id?: string;
}

export interface SearchListResponse {
  items: ResearchSession[];
  total: number;
  offset: number;
  limit: number;
}

export interface ConnectionMetrics {
  lastHeartbeat: number | null;
  reconnectAttempts: number;
  messageCount: number;
  lastLatency: number;
}

export type ErrorType = {
  message: string;
  code?: string;
  details?: string;
} | null;

export interface LoadingStates {
  fetchingSessions: boolean;
  fetchingSession: boolean;
  creatingSession: boolean;
  sendingMessage: boolean;
  updatingSession: boolean;
  deletingSession: boolean;
}

export interface ResearchContextType {
  sessions: ResearchSession[];
  currentSession: ResearchSession | null;
  isLoading: boolean;
  loadingStates: LoadingStates;
  error: ErrorType | null;
  createSession: (query: string, searchParams?: SearchParams) => Promise<string>;
  sendMessage: (sessionId: string, content: string) => Promise<void>;
  getSession: (sessionId: string) => Promise<ResearchSession | null>;
  getSessions: (options?: {
    featuredOnly?: boolean;
    status?: QueryStatus;
    limit?: number;
    offset?: number;
    append?: boolean;
    skipAuthCheck?: boolean;
  }) => Promise<void>;
  updateSession: (sessionId: string, updates: Partial<ResearchSession>) => Promise<void>;
  deleteSession: (sessionId: string) => Promise<void>;
  clearError: () => void;
  totalSessions: number;
  isConnected: boolean;
  connectionStatus: ConnectionStatus;
  connectionMetrics: ConnectionMetrics;
  connectToStream: (sessionId: string) => Promise<void>;
  disconnectStream: () => void;
  clearCache: () => void;
}

export const ResearchContext = createContext<ResearchContextType | undefined>(undefined);

export function useResearch() {
  const context = useContext(ResearchContext);
  if (context === undefined) {
    throw new Error("useResearch must be used within a ResearchProvider");
  }
  return context;
}

export interface ResearchProviderProps {
  children: ReactNode;
}
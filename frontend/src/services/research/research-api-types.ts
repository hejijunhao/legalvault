// src/services/research/research-api-types.ts

import { QueryCategory, QueryStatus, QueryType } from "@/contexts/research/research-context";

// Re-export types from research-context
export { QueryCategory, QueryStatus, QueryType };

// Cache-related types
export interface CacheConfig {
  ttl: number;
  storageKey: string;
  sanitizeBeforeStorage: boolean;
  sensitiveFields: string[];
}

export interface CacheEntry<T> {
  data: T;
  timestamp: number;
  key: string;
}

export interface CacheStorage {
  sessions: Record<string, CacheEntry<ResearchSession>>;
  sessionLists: Record<string, CacheEntry<SearchListResponse>>;
  messages: Record<string, CacheEntry<Message>>;
  messageLists: Record<string, CacheEntry<MessageListResponse>>;
}

// API response types
export interface SearchListResponse {
  items: ResearchSession[];
  total: number;
  offset: number;
  limit: number;
}

export interface MessageListResponse {
  items: Message[];
  total: number;
  offset: number;
  limit: number;
}

// Domain types
export interface Citation {
  text: string;
  url: string;
  metadata?: Record<string, unknown>;
}

export interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: { text: string; citations?: Citation[] };
  search_id?: string;
  sequence: number;
  status?: QueryStatus;
  created_at?: string;
  updated_at?: string;
}

export interface SearchParams {
  temperature?: number;
  max_tokens?: number;
  top_p?: number;
  top_k?: number;
  jurisdiction?: string;
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

// WebSocket types
export interface WebSocketMessage {
  type: string;
  data?: Record<string, unknown>;
  message?: string;
  search_id?: string;
  status?: string;
  subscribed_to?: string[];
}

export interface WebSocketConnection {
  disconnect: () => void;
  send: (data: Record<string, unknown>) => void;
  isConnected: boolean;
}

// Error types
export interface ApiError extends Error {
  status?: number;
  statusText?: string;
  code?: string;
  details?: string;
  originalError?: Error | unknown;
}
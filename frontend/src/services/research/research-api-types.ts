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
  url: string;
  title: string;
  snippet: string;
}

export interface MessageContent {
  text: string;
  citations?: Citation[];
}

export interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: MessageContent;
  sequence: number;
  created_at: string;
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
  query: string;  // Primary search query
  title?: string; // Optional display title
  description?: string;
  messages: Message[];
  created_at: string;
  updated_at: string;
  is_featured: boolean;
  tags: string[];
  search_params?: SearchParams;
  category?: QueryCategory;
  query_type?: QueryType;
  status: QueryStatus;
  user_id: string;
  enterprise_id?: string;
}

// SSE types
export enum SSEEventType {
  CONNECTION_ESTABLISHED = 'connection_established',
  MESSAGES = 'messages',
  USER_MESSAGE = 'user_message',
  ASSISTANT_CHUNK = 'assistant_chunk',
  ASSISTANT_MESSAGE_COMPLETE = 'assistant_message_complete',
  HEARTBEAT = 'heartbeat',
  ERROR = 'error'
}

export interface SSEMessage {
  type: SSEEventType;
  data: any;
}

export interface SSEOptions {
  onMessage: (data: Message[]) => void;
  onError: (error: Error) => void;
  onConnectionChange: (status: ConnectionStatus) => void;
}

export interface SSEConnection {
  close: () => void;
  isConnected: () => boolean;
}

export enum ConnectionStatus {
  CONNECTED = 'connected',
  DISCONNECTED = 'disconnected',
  CONNECTING = 'connecting',
  ERROR = 'error'
}

export type ApiError = {
  message: string;
  code?: string;
};
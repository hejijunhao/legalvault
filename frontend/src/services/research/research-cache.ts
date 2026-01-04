// src/services/research/research-cache.ts

import {
  CacheConfig,
  CacheEntry,
  CacheStorage,
  ResearchSession,
  Message,
  SearchListResponse,
  MessageListResponse
} from './research-api-types';
import { apiClient } from '@/lib/api-client';

/**
 * Cache for research sessions and messages
 */
export class ResearchCache {
  sessionCache: Map<string, CacheEntry<ResearchSession>> = new Map();
  sessionListCache: Map<string, CacheEntry<SearchListResponse>> = new Map();
  messageCache: Map<string, CacheEntry<Message>> = new Map();
  messageListCache: Map<string, CacheEntry<MessageListResponse>> = new Map();
  private pendingFetches: Map<string, Promise<any>> = new Map(); // For deduplication
  
  config: CacheConfig = {
    ttl: 5 * 60 * 1000, // 5 minutes
    storageKey: 'research_cache',
    sanitizeBeforeStorage: true,
    sensitiveFields: ['content', 'messages', 'query']
  };
  
  constructor() {
    this.loadFromStorage();
  }
  
  /**
   * Load cache from localStorage (client-side only)
   */
  loadFromStorage(): void {
    if (typeof window === 'undefined') {
      this.sessionCache = new Map();
      this.messageCache = new Map();
      return;
    }

    try {
      const storedData = localStorage.getItem(this.config.storageKey);
      if (!storedData) return;
      
      const parsed = JSON.parse(storedData) as CacheStorage;
      
      if (parsed.sessions) {
        Object.values(parsed.sessions).forEach(entry => {
          this.sessionCache.set(entry.key, entry);
        });
      }
      
      if (parsed.messages) {
        Object.values(parsed.messages).forEach(entry => {
          this.messageCache.set(entry.key, entry);
        });
      }
    } catch (error) {
      console.error('Error loading cache from storage:', error);
      localStorage.removeItem(this.config.storageKey);
    }
  }
  
  /**
   * Save cache to localStorage (client-side only)
   */
  saveToStorage(): void {
    if (typeof window === 'undefined') {
      return;
    }

    try {
      const sessionsObj: Record<string, CacheEntry<ResearchSession>> = {};
      const messagesObj: Record<string, CacheEntry<Message>> = {};
      
      this.sessionCache.forEach((entry, key) => {
        const storageEntry = { ...entry };
        
        if (this.config.sanitizeBeforeStorage && entry.data) {
          storageEntry.data = this.sanitizeForStorage(entry.data);
        }
        
        sessionsObj[key] = storageEntry;
      });
      
      this.messageCache.forEach((entry, key) => {
        const storageEntry = { ...entry };
        
        if (this.config.sanitizeBeforeStorage && entry.data) {
          storageEntry.data = this.sanitizeForStorage(entry.data);
        }
        
        messagesObj[key] = storageEntry;
      });
      
      const storage: CacheStorage = {
        sessions: sessionsObj,
        messages: messagesObj,
        sessionLists: {},
        messageLists: {}
      };
      
      localStorage.setItem(this.config.storageKey, JSON.stringify(storage));
    } catch (error) {
      console.error('Error saving cache to storage:', error);
    }
  }
  
  /**
   * Sanitize sensitive data before storage
   */
  private sanitizeForStorage<T>(data: T): T {
    if (!data || typeof data !== 'object') return data;
    
    const sanitized = { ...data } as any;
    
    this.config.sensitiveFields.forEach(field => {
      if (field in sanitized) {
        if (Array.isArray(sanitized[field])) {
          sanitized[field] = [`[ENCRYPTED: ${sanitized[field].length} items]`];
        } else if (typeof sanitized[field] === 'object') {
          sanitized[field] = { _encrypted: true };
        } else {
          sanitized[field] = `[ENCRYPTED: ${typeof sanitized[field]}]`;
        }
      }
    });
    
    return sanitized;
  }
  
  /**
   * Check if a cache entry is still valid
   */
  private isValid<T>(entry: CacheEntry<T> | undefined): boolean {
    if (!entry) return false;
    return Date.now() - entry.timestamp < this.config.ttl;
  }
  
  /**
   * Check session cache without fetching
   */
  checkSessionCache(sessionId: string): ResearchSession | null {
    const entry = this.sessionCache.get(sessionId);
    if (this.isValid(entry) && entry) {
      console.log(`Cache hit for session ${sessionId}`);
      return entry.data;
    }
    return null;
  }
  
  /**
   * Get a session from cache or fetch it
   */
  async getSession(sessionId: string): Promise<ResearchSession | null> {
    const entry = this.sessionCache.get(sessionId);
    if (this.isValid(entry) && entry) {
      console.log(`Cache hit for session ${sessionId}`);
      return entry.data;
    }

    const key = `session_${sessionId}`;
    if (this.pendingFetches.has(key)) {
      console.log(`Waiting for pending fetch for session ${sessionId}`);
      return this.pendingFetches.get(key);
    }

    const promise = (async () => {
      try {
        console.log('fetchSession URL:', `/api/research/searches/${sessionId}`);
        const data = await apiClient.get<ResearchSession>(`/api/research/searches/${sessionId}`);

        if (data) {
          this.setSession(data);
        }
        return data;
      } catch (err) {
        throw err;
      } finally {
        this.pendingFetches.delete(key);
      }
    })();

    this.pendingFetches.set(key, promise);
    console.log(`Initiating fetch for session ${sessionId}`);
    return promise;
  }
  
  /**
   * Set a session in cache
   */
  setSession(session: ResearchSession): void {
    if (!session?.id) return;
    const key = session.id;
    const entry: CacheEntry<ResearchSession> = {
      data: session,
      timestamp: Date.now(),
      key
    };
    this.sessionCache.set(key, entry);
    this.saveToStorage();
  }
  
  /**
   * Get a session list from cache
   */
  getSessionList(options?: {
    featuredOnly?: boolean;
    status?: string;
    limit?: number;
    offset?: number;
  } | null): SearchListResponse | null {
    const key = this.getSessionListCacheKey(options);
    const entry = this.sessionListCache.get(key);
    if (this.isValid(entry) && entry) {
      console.log(`Cache hit for session list ${key}`);
      return entry.data;
    }
    return null;
  }
  
  /**
   * Set a session list in cache
   */
  setSessionList(data: SearchListResponse, options?: {
    featuredOnly?: boolean;
    status?: string;
    limit?: number;
    offset?: number;
  } | null): void {
    const key = this.getSessionListCacheKey(options);
    const entry: CacheEntry<SearchListResponse> = {
      data,
      timestamp: Date.now(),
      key
    };
    this.sessionListCache.set(key, entry);
  }
  
  /**
   * Get a message from cache
   */
  getMessage(messageId: string): Message | null {
    const entry = this.messageCache.get(messageId);
    if (this.isValid(entry) && entry) {
      console.log(`Cache hit for message ${messageId}`);
      return entry.data;
    }
    return null;
  }
  
  /**
   * Set a message in cache
   */
  setMessage(message: Message): void {
    if (!message?.id) return;
    const key = message.id;
    const entry: CacheEntry<Message> = {
      data: message,
      timestamp: Date.now(),
      key
    };
    this.messageCache.set(key, entry);
    this.saveToStorage();
  }
  
  /**
   * Delete a message from cache
   */
  deleteMessage(messageId: string): void {
    this.messageCache.delete(messageId);
    this.saveToStorage();
  }
  
  /**
   * Check message list cache without fetching
   */
  checkMessageListCache(searchId: string, options?: {
    limit?: number;
    offset?: number;
  } | null): MessageListResponse | null {
    const key = this.getMessageListCacheKey(searchId, options);
    const entry = this.messageListCache.get(key);
    if (this.isValid(entry) && entry) {
      console.log(`Cache hit for message list ${key}`);
      return entry.data;
    }
    return null;
  }
  
  /**
   * Get a message list from cache or fetch it
   */
  async getMessageList(searchId: string, options?: {
    limit?: number;
    offset?: number;
  } | null): Promise<MessageListResponse | null> {
    const key = this.getMessageListCacheKey(searchId, options);
    const entry = this.messageListCache.get(key);
    if (this.isValid(entry) && entry) {
      console.log(`Cache hit for message list ${key}`);
      return entry.data;
    }

    const fetchKey = `messages_${key}`;
    if (this.pendingFetches.has(fetchKey)) {
      console.log(`Waiting for pending fetch for message list ${key}`);
      return this.pendingFetches.get(fetchKey);
    }

    const promise = (async () => {
      try {
        const url = `/api/research/messages/search/${searchId}`;
        console.log('fetchMessagesForSearch URL:', url);

        const data = await apiClient.get<MessageListResponse>(url, {
          limit: options?.limit,
          offset: options?.offset
        });

        if (data) {
          this.setMessageList(searchId, data, options);
        }
        return data;
      } catch (err) {
        throw err;
      } finally {
        this.pendingFetches.delete(fetchKey);
      }
    })();

    this.pendingFetches.set(fetchKey, promise);
    console.log(`Initiating fetch for message list ${key}`);
    return promise;
  }
  
  /**
   * Set a message list in cache
   */
  setMessageList(searchId: string, data: MessageListResponse, options?: {
    limit?: number;
    offset?: number;
  } | null): void {
    const key = this.getMessageListCacheKey(searchId, options);
    const entry: CacheEntry<MessageListResponse> = {
      data,
      timestamp: Date.now(),
      key
    };
    this.messageListCache.set(key, entry);
  }
  
  /**
   * Generate a cache key for session lists
   */
  private getSessionListCacheKey(options?: {
    featuredOnly?: boolean;
    status?: string;
    limit?: number;
    offset?: number;
  } | null): string {
    if (!options) return 'all';
    return `${options.featuredOnly ? 'featured' : 'all'}_${options.status || 'any'}_${options.limit || 'default'}_${options.offset || 0}`;
  }
  
  /**
   * Generate a cache key for message lists
   */
  private getMessageListCacheKey(searchId: string, options?: {
    limit?: number;
    offset?: number;
  } | null): string {
    if (!options) return `search_${searchId}`;
    return `search_${searchId}_${options.limit || 'default'}_${options.offset || 0}`;
  }
  
  /**
   * Invalidate cache for a specific search
   */
  invalidateSearch(searchId: string): void {
    this.sessionCache.delete(searchId);
    
    const messageListKeys = Array.from(this.messageListCache.keys())
      .filter(key => key.startsWith(`search_${searchId}`));
    
    messageListKeys.forEach(key => {
      this.messageListCache.delete(key);
    });
    
    this.saveToStorage();
  }
  
  /**
   * Invalidate message list cache for a specific search
   */
  invalidateMessageList(searchId: string): void {
    const messageListKeys = Array.from(this.messageListCache.keys())
      .filter(key => key.startsWith(`search_${searchId}`));
    
    messageListKeys.forEach(key => {
      this.messageListCache.delete(key);
    });
  }
  
  /**
   * Clear session list cache
   */
  clearSessionListCache(): void {
    this.sessionListCache.clear();
  }
  
  /**
   * Clear message cache
   */
  clearMessageCache(): void {
    this.messageCache.clear();
    this.messageListCache.clear();
    this.saveToStorage();
  }
  
  /**
   * Clear all cache
   */
  clear(): void {
    this.sessionCache.clear();
    this.sessionListCache.clear();
    this.messageCache.clear();
    this.messageListCache.clear();
    this.pendingFetches.clear();
    if (typeof window !== 'undefined') {
      localStorage.removeItem(this.config.storageKey);
    }
  }
  
  /**
   * Refresh cache if it's getting close to expiration
   */
  refreshCacheIfNeeded<T>(
    cacheMap: Map<string, CacheEntry<T>>, 
    key: string, 
    refreshThreshold: number, 
    refreshFn: () => Promise<T>
  ): Promise<T> | null {
    const entry = cacheMap.get(key);
    
    if (!entry) return null;
    
    const age = Date.now() - entry.timestamp;
    const timeUntilExpiration = this.config.ttl - age;
    
    if (timeUntilExpiration < refreshThreshold) {
      console.log(`Cache entry for ${key} is close to expiration, refreshing...`);
      return refreshFn();
    }
    
    return null;
  }
}

// Create a singleton instance
export const researchCache = new ResearchCache();
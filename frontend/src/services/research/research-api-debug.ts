// src/services/research/research-api-debug.ts

import { researchCache } from './research-cache';

/**
 * Debug utilities for the research API
 * These functions are only meant to be used during development
 */

/**
 * Log the current state of the cache
 */
export function logCacheState(): void {
  console.group('Research Cache State');
  
  console.log('Session Cache:', {
    size: researchCache.sessionCache.size,
    keys: Array.from(researchCache.sessionCache.keys())
  });
  
  console.log('Session List Cache:', {
    size: researchCache.sessionListCache.size,
    keys: Array.from(researchCache.sessionListCache.keys())
  });
  
  console.log('Message Cache:', {
    size: researchCache.messageCache.size,
    keys: Array.from(researchCache.messageCache.keys())
  });
  
  console.log('Message List Cache:', {
    size: researchCache.messageListCache.size,
    keys: Array.from(researchCache.messageListCache.keys())
  });
  
  console.groupEnd();
}

/**
 * Monitor cache operations
 * @param enable Whether to enable monitoring
 */
export function monitorCacheOperations(enable: boolean = true): void {
  if (!enable) {
    console.log('Cache operation monitoring disabled');
    return;
  }
  
  console.log('Cache operation monitoring enabled');
  
  // Monkey patch cache methods to log operations
  const originalSetSession = researchCache.setSession;
  researchCache.setSession = function(session) {
    console.log(`Cache: Setting session ${session.id}`);
    return originalSetSession.call(this, session);
  };
  
  const originalGetSession = researchCache.getSession;
  researchCache.getSession = async function(sessionId) {
    const result = await originalGetSession.call(this, sessionId);
    console.log(`Cache: Getting session ${sessionId} - ${result ? 'HIT' : 'MISS'}`);
    return result;
  };
  
  const originalCheckSessionCache = researchCache.checkSessionCache;
  researchCache.checkSessionCache = function(sessionId) {
    const result = originalCheckSessionCache.call(this, sessionId);
    console.log(`Cache: Checking session cache ${sessionId} - ${result ? 'HIT' : 'MISS'}`);
    return result;
  };
  
  const originalSetMessage = researchCache.setMessage;
  researchCache.setMessage = function(message) {
    console.log(`Cache: Setting message ${message.id}`);
    return originalSetMessage.call(this, message);
  };
  
  const originalGetMessage = researchCache.getMessage;
  researchCache.getMessage = function(messageId) {
    const result = originalGetMessage.call(this, messageId);
    console.log(`Cache: Getting message ${messageId} - ${result ? 'HIT' : 'MISS'}`);
    return result;
  };
  
  const originalGetMessageList = researchCache.getMessageList;
  researchCache.getMessageList = async function(searchId, options) {
    const result = await originalGetMessageList.call(this, searchId, options);
    console.log(`Cache: Getting message list for search ${searchId} - ${result ? 'HIT' : 'MISS'}`);
    return result;
  };
  
  const originalCheckMessageListCache = researchCache.checkMessageListCache;
  researchCache.checkMessageListCache = function(searchId, options) {
    const result = originalCheckMessageListCache.call(this, searchId, options);
    console.log(`Cache: Checking message list cache for search ${searchId} - ${result ? 'HIT' : 'MISS'}`);
    return result;
  };
  
  const originalInvalidateSearch = researchCache.invalidateSearch;
  researchCache.invalidateSearch = function(searchId) {
    console.log(`Cache: Invalidating search ${searchId}`);
    return originalInvalidateSearch.call(this, searchId);
  };
  
  const originalClear = researchCache.clear;
  researchCache.clear = function() {
    console.log('Cache: Clearing all cache');
    return originalClear.call(this);
  };
}

/**
 * Simulate network latency for API calls
 * @param minDelay Minimum delay in milliseconds
 * @param maxDelay Maximum delay in milliseconds
 */
export function simulateNetworkLatency(minDelay: number = 200, maxDelay: number = 1000): void {
  const originalFetch = window.fetch;
  
  window.fetch = async function(...args) {
    const delay = Math.random() * (maxDelay - minDelay) + minDelay;
    console.log(`Simulating network latency: ${Math.round(delay)}ms for ${args[0]}`);
    
    await new Promise(resolve => setTimeout(resolve, delay));
    return originalFetch.apply(this, args);
  };
  
  console.log(`Network latency simulation enabled (${minDelay}-${maxDelay}ms)`);
}

/**
 * Restore original fetch behavior
 */
export function restoreOriginalFetch(): void {
  // This assumes the fetch function hasn't been modified elsewhere
  delete (window as any).__fetchWithLatency;
  console.log('Original fetch behavior restored');
}
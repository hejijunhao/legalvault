// src/lib/auth-manager.ts

import { supabase } from './supabase';
import { User, Session } from '@supabase/supabase-js';

// Event types for auth state changes
export type AuthEventType = 
  | 'SIGNED_IN'
  | 'SIGNED_OUT'
  | 'TOKEN_REFRESHED'
  | 'TOKEN_REFRESH_FAILED'
  | 'USER_UPDATED';

export interface AuthEvent {
  type: AuthEventType;
  session?: Session | null;
  user?: User | null;
  error?: Error | null;
}

type AuthEventListener = (event: AuthEvent) => void;

class AuthManager {
  private listeners: AuthEventListener[] = [];
  private refreshTimerId: ReturnType<typeof setTimeout> | null = null;
  private isRefreshing: boolean = false;
  
  constructor() {
    this.initialize();
  }
  
  /**
   * Initialize the auth manager by setting up Supabase auth listeners
   */
  private initialize(): void {
    // Listen for auth state changes from Supabase
    supabase.auth.onAuthStateChange((event, session) => {
      console.log(`Auth state changed: ${event}`);
      
      switch (event) {
        case 'SIGNED_IN':
          this.notifyListeners({
            type: 'SIGNED_IN',
            session,
            user: session?.user
          });
          this.scheduleTokenRefresh(session);
          break;
          
        case 'SIGNED_OUT':
          this.notifyListeners({
            type: 'SIGNED_OUT',
            session: null,
            user: null
          });
          this.clearRefreshTimer();
          break;
          
        case 'TOKEN_REFRESHED':
          this.notifyListeners({
            type: 'TOKEN_REFRESHED',
            session,
            user: session?.user
          });
          this.scheduleTokenRefresh(session);
          break;
          
        case 'USER_UPDATED':
          this.notifyListeners({
            type: 'USER_UPDATED',
            session,
            user: session?.user
          });
          break;
      }
    });
    
    // Check current session on initialization
    this.getCurrentSession().then(session => {
      if (session) {
        this.scheduleTokenRefresh(session);
      }
    });
  }
  
  /**
   * Get the current session
   * @returns Promise resolving to the current session or null
   */
  async getCurrentSession(): Promise<Session | null> {
    try {
      const { data, error } = await supabase.auth.getSession();
      if (error) {
        console.error('Error getting session:', error);
        return null;
      }
      return data.session;
    } catch (error) {
      console.error('Error getting session:', error);
      return null;
    }
  }
  
  /**
   * Schedule a token refresh before the token expires
   * @param session Current session with expiry information
   */
  private scheduleTokenRefresh(session: Session | null): void {
    if (!session) return;
    
    this.clearRefreshTimer();
    
    try {
      // Get token expiry time
      const expiresAt = session.expires_at;
      if (!expiresAt) {
        console.warn('No expiration time found in session');
        return;
      }
      
      // Calculate time until expiry (in milliseconds)
      const expiresAtMs = expiresAt * 1000; // Convert from seconds to milliseconds
      const now = Date.now();
      const timeUntilExpiry = expiresAtMs - now;
      
      // Schedule refresh at 75% of the token's lifetime
      // This gives us a buffer to ensure the token is refreshed before it expires
      const refreshBuffer = timeUntilExpiry * 0.25; // 25% before expiry
      const refreshTime = Math.max(timeUntilExpiry - refreshBuffer, 0);
      
      console.log(`Scheduling token refresh in ${Math.floor(refreshTime / 1000)} seconds`);
      
      this.refreshTimerId = setTimeout(() => {
        this.refreshToken();
      }, refreshTime);
    } catch (error) {
      console.error('Error scheduling token refresh:', error);
    }
  }
  
  /**
   * Clear the token refresh timer
   */
  private clearRefreshTimer(): void {
    if (this.refreshTimerId) {
      clearTimeout(this.refreshTimerId);
      this.refreshTimerId = null;
    }
  }
  
  /**
   * Refresh the auth token
   */
  async refreshToken(): Promise<void> {
    if (this.isRefreshing) return;
    
    this.isRefreshing = true;
    
    try {
      console.log('Refreshing auth token...');
      const { data, error } = await supabase.auth.refreshSession();
      
      if (error) {
        console.error('Error refreshing token:', error);
        this.notifyListeners({
          type: 'TOKEN_REFRESH_FAILED',
          error
        });
      } else {
        console.log('Token refreshed successfully');
        this.notifyListeners({
          type: 'TOKEN_REFRESHED',
          session: data.session,
          user: data.user
        });
        
        // Schedule the next refresh
        this.scheduleTokenRefresh(data.session);
      }
    } catch (error) {
      console.error('Error refreshing token:', error);
      this.notifyListeners({
        type: 'TOKEN_REFRESH_FAILED',
        error: error instanceof Error ? error : new Error(String(error))
      });
    } finally {
      this.isRefreshing = false;
    }
  }
  
  /**
   * Add a listener for auth events
   * @param listener Function to call when auth events occur
   * @returns Function to remove the listener
   */
  addListener(listener: AuthEventListener): () => void {
    this.listeners.push(listener);
    
    // Return a function to remove this listener
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }
  
  /**
   * Notify all listeners of an auth event
   * @param event The auth event to notify about
   */
  private notifyListeners(event: AuthEvent): void {
    this.listeners.forEach(listener => {
      try {
        listener(event);
      } catch (error) {
        console.error('Error in auth event listener:', error);
      }
    });
  }
}

// Create a singleton instance
const authManager = new AuthManager();

export default authManager;
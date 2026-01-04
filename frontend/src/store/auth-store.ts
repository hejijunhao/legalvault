// src/store/auth-store.ts

import { create } from 'zustand'
import { supabase } from '@/lib/supabase'

// User type matching backend UserProfile
export interface AuthUser {
  id: string
  auth_user_id: string
  email: string
  first_name: string
  last_name: string
  name: string
  role: string
  virtual_paralegal_id?: string
  enterprise_id?: string
  created_at: string
  last_login?: string
}

// Auth event types for external listeners (e.g., cache clearing)
export type AuthEventType = 'SIGNED_IN' | 'SIGNED_OUT' | 'TOKEN_REFRESHED' | 'USER_UPDATED'

interface AuthState {
  user: AuthUser | null
  isLoading: boolean
  isAuthenticated: boolean
  isInitialized: boolean
}

interface AuthActions {
  initialize: () => Promise<void>
  login: (email: string, password: string) => Promise<boolean>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
  getAccessToken: () => Promise<string | null>
}

type AuthEventListener = (event: AuthEventType) => void

// Store for managing auth event listeners (for cache clearing, etc.)
const authEventListeners: Set<AuthEventListener> = new Set()

export function addAuthEventListener(listener: AuthEventListener): () => void {
  authEventListeners.add(listener)
  return () => authEventListeners.delete(listener)
}

function notifyAuthEvent(event: AuthEventType) {
  authEventListeners.forEach(listener => {
    try {
      listener(event)
    } catch (error) {
      console.error('Error in auth event listener:', error)
    }
  })
}

export const useAuthStore = create<AuthState & AuthActions>((set, get) => ({
  // State
  user: null,
  isLoading: true,
  isAuthenticated: false,
  isInitialized: false,

  // Initialize auth state and set up listeners
  initialize: async () => {
    if (get().isInitialized) return

    try {
      // Get current session
      const { data: { session }, error } = await supabase.auth.getSession()

      if (error) {
        console.error('Error getting session:', error)
        set({ isLoading: false, isInitialized: true })
        return
      }

      if (session) {
        // Store token and fetch user profile
        localStorage.setItem('auth_token', session.access_token)
        await get().refreshUser()
      }

      // Set up auth state change listener
      supabase.auth.onAuthStateChange(async (event, session) => {
        console.log(`Auth state changed: ${event}`)

        switch (event) {
          case 'SIGNED_IN':
            if (session) {
              localStorage.setItem('auth_token', session.access_token)
              await get().refreshUser()
              notifyAuthEvent('SIGNED_IN')
            }
            break

          case 'SIGNED_OUT':
            localStorage.removeItem('auth_token')
            set({ user: null, isAuthenticated: false })
            notifyAuthEvent('SIGNED_OUT')
            break

          case 'TOKEN_REFRESHED':
            if (session) {
              localStorage.setItem('auth_token', session.access_token)
              notifyAuthEvent('TOKEN_REFRESHED')
            }
            break

          case 'USER_UPDATED':
            await get().refreshUser()
            notifyAuthEvent('USER_UPDATED')
            break
        }
      })
    } catch (error) {
      console.error('Auth initialization error:', error)
    } finally {
      set({ isLoading: false, isInitialized: true })
    }
  },

  // Login with email and password
  login: async (email: string, password: string): Promise<boolean> => {
    try {
      set({ isLoading: true })

      const { data: { session }, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      })

      if (error) {
        console.error('Login error:', error)
        return false
      }

      if (!session) {
        console.error('No session after login')
        return false
      }

      localStorage.setItem('auth_token', session.access_token)
      await get().refreshUser()

      return true
    } catch (error) {
      console.error('Login error:', error)
      return false
    } finally {
      set({ isLoading: false })
    }
  },

  // Logout
  logout: async () => {
    try {
      await supabase.auth.signOut()
      localStorage.removeItem('auth_token')
      set({ user: null, isAuthenticated: false })
    } catch (error) {
      console.error('Logout error:', error)
    }
  },

  // Refresh user profile from backend
  refreshUser: async () => {
    try {
      const token = localStorage.getItem('auth_token')

      if (!token) {
        set({ user: null, isAuthenticated: false })
        return
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        throw new Error('Failed to fetch user profile')
      }

      const userData: AuthUser = await response.json()
      set({ user: userData, isAuthenticated: true })
    } catch (error) {
      console.error('Error refreshing user:', error)
      localStorage.removeItem('auth_token')
      set({ user: null, isAuthenticated: false })
    }
  },

  // Get current access token
  getAccessToken: async (): Promise<string | null> => {
    const { data: { session } } = await supabase.auth.getSession()
    return session?.access_token || null
  },
}))

// Convenience hook with same API as old useAuth
export function useAuth() {
  const store = useAuthStore()

  return {
    user: store.user,
    isLoading: store.isLoading,
    isAuthenticated: store.isAuthenticated,
    login: store.login,
    logout: store.logout,
    refreshUser: store.refreshUser,
  }
}

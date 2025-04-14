// src/contexts/auth-context.tsx

"use client"

import { createContext, useContext, useEffect, useState, ReactNode } from "react"
import { useRouter } from "next/navigation"
import { supabase } from '../lib/supabase'

// Define the User type based on your UserProfile from the backend
type User = {
  id: string
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

// Define the auth context type
type AuthContextType = {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<boolean>
  logout: () => void
  refreshUser: () => Promise<void>
}

// Create the auth context with a default value
const AuthContext = createContext<AuthContextType>({
  user: null,
  isLoading: true,
  isAuthenticated: false,
  login: async () => false,
  logout: () => {},
  refreshUser: async () => {},
})

// Custom hook to use the auth context
export const useAuth = () => useContext(AuthContext)

// Auth provider component
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  // Check if user is authenticated on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        // Get Supabase session
        const { data: { session }, error } = await supabase.auth.getSession()
        if (error) throw error

        if (!session) {
          setIsLoading(false)
          return
        }

        // Store Supabase token
        localStorage.setItem("auth_token", session.access_token)
        
        // Fetch user profile
        await refreshUser()
      } catch (error) {
        console.error("Authentication error:", error)
        localStorage.removeItem("auth_token")
      } finally {
        setIsLoading(false)
      }
    }

    checkAuth()

    // Subscribe to auth state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      if (event === 'SIGNED_IN' && session) {
        localStorage.setItem("auth_token", session.access_token)
        await refreshUser()
      } else if (event === 'SIGNED_OUT') {
        localStorage.removeItem("auth_token")
        setUser(null)
      }
    })

    return () => {
      subscription.unsubscribe()
    }
  }, [])

  // Login function
  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      setIsLoading(true)
      
      // Sign in with Supabase
      const { data: { session }, error } = await supabase.auth.signInWithPassword({
        email,
        password
      })

      if (error) throw error

      if (!session) {
        throw new Error("No session after login")
      }

      // Store token in localStorage
      localStorage.setItem("auth_token", session.access_token)
      
      // Fetch user profile
      await refreshUser()
      
      return true
    } catch (error) {
      console.error("Login error:", error)
      return false
    } finally {
      setIsLoading(false)
    }
  }

  // Logout function
  const logout = async () => {
    try {
      await supabase.auth.signOut()
      localStorage.removeItem("auth_token")
      setUser(null)
      router.push("/login")
    } catch (error) {
      console.error("Logout error:", error)
    }
  }

  // Refresh user profile
  const refreshUser = async (): Promise<void> => {
    try {
      const token = localStorage.getItem("auth_token")
      if (!token) {
        setUser(null)
        return
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        throw new Error("Failed to fetch user profile")
      }

      const userData = await response.json()
      setUser(userData)
    } catch (error) {
      console.error("Error refreshing user:", error)
      setUser(null)
      localStorage.removeItem("auth_token")
    }
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}
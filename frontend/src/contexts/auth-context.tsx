// src/contexts/auth-context.tsx
"use client"

import { createContext, useContext, useEffect, useState, ReactNode } from "react"
import { useRouter } from "next/navigation"

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
        // Check if token exists in localStorage
        const token = localStorage.getItem("auth_token")
        if (!token) {
          setIsLoading(false)
          return
        }

        // Fetch user profile
        await refreshUser()
      } catch (error) {
        console.error("Authentication error:", error)
        // Clear invalid token
        localStorage.removeItem("auth_token")
      } finally {
        setIsLoading(false)
      }
    }

    checkAuth()
  }, [])

  // Login function
  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      setIsLoading(true)
      
      // Log the API URL for debugging
      const apiUrl = `${process.env.NEXT_PUBLIC_API_URL}/api/auth/login`
      console.log('Attempting to connect to:', apiUrl)
      
      // Call the login API
      const response = await fetch(apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || "Login failed")
      }

      const data = await response.json()
      
      // Store token in localStorage
      localStorage.setItem("auth_token", data.access_token)
      
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
  const logout = () => {
    localStorage.removeItem("auth_token")
    setUser(null)
    router.push("/login")
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
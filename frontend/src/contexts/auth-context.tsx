// src/contexts/auth-context.tsx
// Thin wrapper around auth store for backwards compatibility
// New code should use `import { useAuth } from '@/store/auth-store'` directly

"use client"

import { useEffect, ReactNode } from "react"
import { useAuthStore, useAuth } from "@/store/auth-store"

// Re-export useAuth for backwards compatibility
export { useAuth } from "@/store/auth-store"

// Re-export AuthUser type
export type { AuthUser as User } from "@/store/auth-store"

// Auth provider - now just initializes the store
export function AuthProvider({ children }: { children: ReactNode }) {
  const initialize = useAuthStore((state) => state.initialize)

  useEffect(() => {
    initialize()
  }, [initialize])

  return <>{children}</>
}

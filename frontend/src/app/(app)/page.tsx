// src/app/(app)/page.tsx
"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/contexts/auth-context"

export default function Home() {
  const router = useRouter()
  const { isAuthenticated, isLoading } = useAuth()

  useEffect(() => {
    // Only redirect if user is authenticated and page has loaded
    if (isAuthenticated && !isLoading) {
      router.push("/research")
    }
  }, [isAuthenticated, isLoading, router])

  return (
    <div className="min-h-[calc(100vh-4rem)]" />
  )
}
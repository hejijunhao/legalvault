// src/app/(auth)/logout/page.tsx

"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/contexts/auth-context"

export default function LogoutPage() {
  const { logout } = useAuth()
  const router = useRouter()

  useEffect(() => {
    logout()
    router.push("/login")
  }, [logout, router])

  return (
    <div className="flex h-screen items-center justify-center">
      <p className="text-lg text-white/70">Logging out...</p>
    </div>
  )
}
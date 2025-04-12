// src/components/login/login-form.tsx

"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Image from "next/image"
import { motion } from "framer-motion"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/contexts/auth-context"

export function LoginForm() {
  const router = useRouter()
  const { login, isLoading } = useAuth()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")

    try {
      const success = await login(email, password)
      
      if (success) {
        // Redirect to research page on successful login
        router.push("/research")
      } else {
        setError("Invalid email or password")
      }
    } catch (err) {
      setError("An error occurred during login")
      console.error(err)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, ease: [0.04, 0.62, 0.23, 0.98] }}
      className="relative w-full max-w-[400px]"
    >
      {/* Login Card */}
      <div className="rounded-xl border border-white/10 bg-white/5 p-8 backdrop-blur-xl">
        {/* Logo */}
        <div className="mb-8 flex justify-center">
          <Image src="/images/legalvault-logo.svg" alt="LegalVault" width={180} height={40} className="h-10 w-auto" />
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="rounded-md bg-red-500/10 p-3 text-center text-sm text-red-500">
              {error}
            </div>
          )}
          
          <div className="space-y-4">
            <Input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="h-12 border-white/10 bg-white/5 text-white placeholder:text-white/40"
              required
            />
            <Input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="h-12 border-white/10 bg-white/5 font-mono text-white placeholder:text-white/40"
              required
              style={{
                letterSpacing: "0.5em",
              }}
            />
          </div>

          <Button
            type="submit"
            className="h-12 w-full bg-black font-medium text-white hover:bg-black/90"
            disabled={isLoading}
          >
            {isLoading ? "Accessing..." : "Access"}
          </Button>
        </form>
      </div>

      {/* Decorative elements */}
      <div className="absolute -inset-0.5 -z-10 rounded-xl bg-gradient-to-b from-white/15 to-white/5 blur-sm" />
      <div className="absolute -inset-1 -z-20 rounded-xl bg-gradient-to-b from-white/10 to-transparent blur-md" />
    </motion.div>
  )
}
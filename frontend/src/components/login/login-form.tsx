// src/components/login/login-form.tsx

"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Image from "next/image"
import { motion } from "framer-motion"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

export function LoginForm() {
  const router = useRouter()
  const [email, setEmail] = useState("")
  const [key, setKey] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  // Temporary login handler that redirects to workspace
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    // Simulate loading state
    await new Promise((resolve) => setTimeout(resolve, 800))

    // Redirect to workspace (this will be replaced with actual auth later)
    router.push("/workspace")
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
              placeholder="Key"
              value={key}
              onChange={(e) => setKey(e.target.value)}
              className="h-12 border-white/10 bg-white/5 font-mono text-white placeholder:text-white/40"
              required
              // Custom password masking
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


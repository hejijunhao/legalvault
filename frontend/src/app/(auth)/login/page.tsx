// src/app/(auth)/login/page.tsx

"use client"

import { LoginForm } from "@/components/login/login-form"

export default function LoginPage() {
  return (
    <div
      className="min-h-screen w-full flex items-center justify-center"
      style={{
        background: `
          linear-gradient(
            135deg,
            rgb(37, 38, 44) 0%,
            rgb(50, 55, 65) 50%,
            rgb(37, 38, 44) 100%
          )
        `,
      }}
    >
      {/* Gradient overlay for depth */}
      <div className="absolute inset-0 bg-gradient-to-br from-transparent via-black/5 to-black/20" />

      {/* Animated background patterns */}
      <div className="absolute inset-0 opacity-30">
        <div className="absolute inset-0 bg-[radial-gradient(circle_500px_at_50%_200px,#3e4451,transparent)]" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_800px_at_100%_200px,#4a515e,transparent)]" />
      </div>

      <LoginForm />
    </div>
  )
}
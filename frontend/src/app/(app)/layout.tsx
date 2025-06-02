// src/app/(app)/layout.tsx

// Removed "use client" - this is now a Server Component again

import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "../globals.css"
// MainHeader will be handled by AppClientLayout
import { ProtectedRoute } from "@/components/auth/protected-route"
import { ResearchProvider } from "@/contexts/research/research-context"
// We will create and import AppClientLayout
import AppClientLayout from "@/components/layout/app-client-layout" // Adjusted path

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "LegalVault",
  description: "The intelligent lawyer's workstation",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  // Pathname logic removed from here

  return (
    <ProtectedRoute>
      <ResearchProvider>
        {/* AppClientLayout will now handle the conditional header and main content structure */}
        <AppClientLayout>{children}</AppClientLayout>
      </ResearchProvider>
    </ProtectedRoute>
  )
}

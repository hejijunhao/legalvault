// src/app/(app)/layout.tsx

import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "../globals.css"
import { MainHeader } from "@/components/ui/main-header"
import { ProtectedRoute } from "@/components/auth/protected-route"
import { ResearchProvider } from "@/contexts/research/research-context"

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
  return (
    <ProtectedRoute>
      <ResearchProvider>
        <div className={`${inter.className} min-h-screen flex flex-col bg-gradient-to-b from-[#EFF2F5] via-[#E3E7EB] to-[#D9DEE3]`}>
          <MainHeader />
          <main className="flex-1 w-full">{children}</main>
        </div>
      </ResearchProvider>
    </ProtectedRoute>
  )
}


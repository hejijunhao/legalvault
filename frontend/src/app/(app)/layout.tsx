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
    <html lang="en">
      <body>
        <ProtectedRoute>
          <ResearchProvider>
            <div className={inter.className}>
              <MainHeader />
              <main className="mx-auto max-w-[1440px] px-4">{children}</main>
            </div>
          </ResearchProvider>
        </ProtectedRoute>
      </body>
    </html>
  )
}

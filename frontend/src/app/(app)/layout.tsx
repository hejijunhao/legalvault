// src/app/(app)/layout.tsx

import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "../globals.css"
import { MainHeader } from "@/components/ui/main-header"

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
  // Check if the current page is an auth page
  const isAuthPage =
    typeof window !== "undefined"
      ? window.location.pathname.includes("/login") || window.location.pathname.includes("/logout")
      : false

  return (
    <html lang="en">
    <body className={inter.className}>
    {!isAuthPage && <MainHeader />}
    {isAuthPage ? children : <main className="mx-auto max-w-[1440px] px-4">{children}</main>}
    </body>
    </html>
  )
}
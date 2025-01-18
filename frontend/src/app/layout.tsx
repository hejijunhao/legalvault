// src/app/layout.tsx

import type { Metadata } from "next"
import { Inter } from 'next/font/google'
import "./globals.css"
import { MainHeader } from "@/components/ui/main-header"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "LegalVault",
  description: "A productivity app for lawyers",
}

export default function RootLayout({
                                     children,
                                   }: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
    <body className={inter.className}>
    <MainHeader />
    <div className="relative">
      <main className="mx-auto max-w-[1440px] px-4">{children}</main>
    </div>
    </body>
    </html>
  )
}
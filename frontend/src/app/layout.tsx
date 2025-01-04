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
    <body className={`${inter.className} min-h-screen bg-gray-50`}>
    <MainHeader />
    <main className="container mx-auto px-4 py-8">{children}</main>
    </body>
    </html>
  )
}
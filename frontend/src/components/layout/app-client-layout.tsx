// src/components/layout/app-client-layout.tsx

"use client"

import { usePathname } from 'next/navigation'
import { MainHeader } from "@/components/ui/main-header"
import { Inter } from "next/font/google" // If font class is needed here

// It's good practice to ensure font consistency if the parent layout used it.
const inter = Inter({ subsets: ["latin"] })

export default function AppClientLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()

  // Regex to check if the path is a research thread page, e.g., /research/some-uuid-string
  const isResearchThreadPage = /^\/research\/[^\/]+$/.test(pathname)

  return (
    <div className={`${inter.className} min-h-screen flex flex-col bg-gradient-to-b from-[#EFF2F5] via-[#E3E7EB] to-[#D9DEE3]`}>
      {!isResearchThreadPage && <MainHeader />}
      <main className="flex-1 w-full">{children}</main>
    </div>
  )
}

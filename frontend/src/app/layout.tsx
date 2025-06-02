// src/app/layout.tsx

import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { AuthProvider } from "@/contexts/auth-context"


const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "LegalVault",
  description: "A productivity app for lawyers",
  icons: {
    icon: "/favicon.ico"
  }
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${inter.className} flex flex-col min-h-screen`}>
        <AuthProvider>
          <main className="flex-grow">{children}</main>
          <footer className="fixed bottom-0 left-0 right-0 bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300 text-xs p-2 border-t border-gray-200 dark:border-gray-700 flex justify-end items-center">
            <div className="flex items-center space-x-4">
              <div>
                <span>System Status: </span>
                <span className="text-green-500">Online</span>
              </div>
              <div>
                <span>Version: 1.0.8-beta</span>
              </div>
              <div>
                <a href="/changelog" className="hover:underline text-blue-500 dark:text-blue-400">
                  Changelog
                </a>
              </div>
            </div>
          </footer>
        </AuthProvider>
      </body>
    </html>
  )
}
"use client"

import { useSupabaseTest } from '@/hooks/use-supabase-test'

export default function TestPage() {
  const { isConnected, error } = useSupabaseTest()

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm">
        <h1 className="text-2xl mb-4">Supabase Connection Test</h1>

        {error && (
          <div className="p-4 mb-4 text-red-500 bg-red-100 rounded">
            Error: {error.message}
          </div>
        )}

        {isConnected === null ? (
          <div className="text-blue-500">Testing connection...</div>
        ) : (
          <div className={isConnected ? "text-green-500" : "text-red-500"}>
            {isConnected ? "✓ Connected to Supabase!" : "✗ Failed to connect to Supabase"}
          </div>
        )}
      </div>
    </main>
  )
}
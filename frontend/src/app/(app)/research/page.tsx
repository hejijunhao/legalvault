// src/app/(app)/research/page.tsx

"use client"

import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { useRouter } from "next/navigation"
import { ResearchSearch } from "@/components/research/research-search"
import { ResearchBanner } from "@/components/research/research-banner"
import { BookmarksBlock } from "@/components/research/bookmarks-block"
import { useResearch } from "@/contexts/research/research-context"
import { Button } from "@/components/ui/button"
import { Loader2, AlertCircle } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"

export default function ResearchPage() {
  const [query, setQuery] = useState("")
  const { createSession, isLoading, error, clearError } = useResearch()
  const router = useRouter()

  // Clear context error when component mounts or unmounts
  useEffect(() => {
    clearError()
    return () => clearError()
  }, [])

  const handleSearch = async () => {
    const trimmedQuery = query.trim()
    if (!trimmedQuery || trimmedQuery.length < 5) return
    
    try {
      const sessionId = await createSession(trimmedQuery)
      router.push(`/research/${sessionId}`)
    } catch (err) {
      console.error("Failed to create research session:", err)
    }
  }

  return (
    <div className="flex min-h-[calc(100vh-4rem)] flex-col items-center justify-start px-4 py-16">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-3xl space-y-12"
      >
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="text-center text-[32px] font-normal italic leading-6 text-[#111827] font-['Libre_Baskerville']"
        >
          What legal insights do you need?
        </motion.h1>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="space-y-8"
        >
          <div className="relative">
            <ResearchSearch query={query} onQueryChange={setQuery} />
            
            {error && (
              <Alert variant="destructive" className="mt-4">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error.message}</AlertDescription>
              </Alert>
            )}
            
            {query.trim() && (
              <div className="mt-4 flex justify-end">
                <Button 
                  onClick={handleSearch} 
                  disabled={isLoading || !query.trim() || query.trim().length < 5}
                  className="bg-[#95C066] hover:bg-[#85b056] text-white"
                  aria-label="Search for legal insights"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Searching...
                    </>
                  ) : (
                    "Search"
                  )}
                </Button>
              </div>
            )}
          </div>
          <BookmarksBlock />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <ResearchBanner />
        </motion.div>
      </motion.div>
    </div>
  )
}
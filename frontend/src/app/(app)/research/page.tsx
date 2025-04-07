// src/app/(app)/research/page.tsx

"use client"

import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { useRouter } from "next/navigation"
import { ResearchSearch } from "@/components/research/research-search"
import { ResearchPromptSuggestions } from "@/components/research/research-prompt-suggestions"
import { PastSearchesGrid } from "@/components/research/past-searches-grid"
import { useResearch, QueryType } from "@/contexts/research/research-context"
import { AlertCircle } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"

export default function ResearchPage() {
  const [query, setQuery] = useState("")
  const { createSession, getSessions, isLoading, error, clearError } = useResearch()
  const router = useRouter()

  // Clear context error when component mounts or unmounts
  useEffect(() => {
    clearError()
    // Only clear on unmount, not on every render
    return () => {}
  }, [clearError]) // Add clearError as dependency since it's memoized

  // Fetch sessions when component mounts
  useEffect(() => {
    getSessions({ limit: 12, skipAuthCheck: true }) // Show up to 12 recent searches
  }, []) // Empty dependency array to run only on mount

  const handleSearch = async (queryType: QueryType | null) => {
    const trimmedQuery = query.trim()
    if (!trimmedQuery || trimmedQuery.length < 5) return
    
    try {
      // Create session with search parameters
      const sessionId = await createSession(trimmedQuery, {
        // Search parameters
        temperature: 0.7, // Default temperature for balanced responses
        max_tokens: 2048, // Reasonable length limit
        top_p: 0.95, // High value for more focused responses
        top_k: 50, // Standard value for diverse but relevant results
        query_type: queryType || QueryType.GENERAL // Pass queryType if provided
      })
      router.push(`/research/${sessionId}?initialQuery=${encodeURIComponent(trimmedQuery)}&queryType=${queryType || QueryType.GENERAL}`)
    } catch (err) {
      // Error is already handled by the context provider
      console.error("Failed to create research session:", err)
    }
  }

  const handleSelectPrompt = (prompt: string) => {
    setQuery(prompt)
  }

  return (
    <div className="flex min-h-[calc(100vh-4rem)] flex-col items-center justify-start py-16">
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
          <div className="relative space-y-2">
            <ResearchSearch 
              query={query} 
              onQueryChange={setQuery} 
              onSubmit={handleSearch}
              isLoading={isLoading}
            />
            
            {/* Add the prompt suggestions component right after the search bar */}
            <ResearchPromptSuggestions onSelectPrompt={handleSelectPrompt} />
            
            {error && (
              <Alert variant="destructive" className="mt-4">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error.message}</AlertDescription>
              </Alert>
            )}
          </div>
          
          {/* Past searches grid will handle its own loading and error states */}
          <PastSearchesGrid />
        </motion.div>
      </motion.div>
    </div>
  )
}
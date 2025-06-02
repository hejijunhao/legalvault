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
  }, [getSessions]) // Add getSessions to dependency array

  const handleSearch = (queryType: QueryType | null) => { 
    const trimmedQuery = query.trim()
    if (!trimmedQuery || trimmedQuery.length < 5) return
    
    const queryParams = new URLSearchParams()
    queryParams.append("initialQuery", trimmedQuery)
    queryParams.append("queryType", queryType || QueryType.GENERAL)

    router.push(`/research/new?${queryParams.toString()}`)
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
          Legal AI that searches the web for you
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
            
            <ResearchPromptSuggestions onSelectPrompt={handleSelectPrompt} />
            
            {error && (
              <Alert variant="destructive" className="mt-4">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error.message}</AlertDescription>
              </Alert>
            )}
          </div>
          
          <PastSearchesGrid />
        </motion.div>
      </motion.div>
    </div>
  )
}
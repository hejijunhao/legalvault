// frontend/src/app/(app)/research/new/page.tsx

"use client"

import { useEffect, useState } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import Link from "next/link"
import { useResearch, QueryType } from "@/contexts/research/research-context"
import { Loader2, AlertCircle } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

export default function NewResearchPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { createSession, isLoading, error: contextError, clearError } = useResearch()
  const [pageError, setPageError] = useState<string | null>(null)

  useEffect(() => {
    // Clear any previous errors from the context and page state when this page loads
    clearError()
    setPageError(null)

    const initialQuery = searchParams.get("initialQuery")
    const queryTypeParam = searchParams.get("queryType") as QueryType | null

    // Validate the initialQuery (e.g., length, content)
    // This check should align with the validation in the original handleSearch function.
    if (!initialQuery || initialQuery.trim().length < 5) {
      setPageError("Invalid or too short query provided. Please return and try again with a more detailed query.")
      return
    }

    const queryType = queryTypeParam || QueryType.GENERAL

    const performCreateSession = async () => {
      try {
        const sessionId = await createSession(initialQuery, {
          // Standard research parameters, matching original implementation
          temperature: 0.7,
          max_tokens: 2048,
          top_p: 0.95,
          top_k: 50,
          type: queryType,
        })
        // Use replace to avoid adding /research/new to browser history
        router.replace(`/research/${sessionId}?initialQuery=${encodeURIComponent(initialQuery)}&queryType=${queryType}`)
      } catch (err: any) {
        console.error("Failed to create research session on /research/new:", err)
        // The useResearch hook's error state (contextError) might be set by createSession itself.
        // We can also set a page-specific error.
        setPageError(err.message || "An unexpected error occurred while creating your research session.")
      }
    }

    performCreateSession()

    // Cleanup function for useEffect
    return () => {
      // If component unmounts before session creation (e.g. user navigates away),
      // clear any context errors that might have been set during the attempt.
      clearError()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]) // Dependencies: searchParams. router, createSession, clearError are assumed stable.

  // Determine the error message to display
  const displayErrorMessage = pageError || contextError?.message

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[calc(100vh-4rem)] p-4 text-center">
        <Loader2 className="h-12 w-12 animate-spin text-primary mb-4" />
        <h1 className="text-xl font-semibold text-gray-800">Creating Your Research Session</h1>
        <p className="mt-2 text-gray-600">Please wait a moment while we prepare your research environment.</p>
      </div>
    )
  }

  if (displayErrorMessage) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[calc(100vh-4rem)] p-4">
        <Alert variant="destructive" className="w-full max-w-lg">
          <AlertCircle className="h-5 w-5" />
          <AlertTitle>Error Creating Session</AlertTitle>
          <AlertDescription>
            {displayErrorMessage}
          </AlertDescription>
        </Alert>
        <Link 
          href="/research"
          className="mt-6 inline-flex items-center justify-center rounded-md bg-primary px-6 py-2.5 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50"
        >
          Return to Research Page
        </Link>
      </div>
    )
  }

  // Fallback / initial render before useEffect kicks in fully.
  // This state should ideally not be visible for long, or only briefly.
  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-4rem)] p-4 text-center">
      <Loader2 className="h-12 w-12 animate-spin text-primary mb-4" />
      <h1 className="text-xl font-semibold text-gray-800">Initializing Research</h1>
      <p className="mt-2 text-gray-600">Getting things ready...</p>
    </div>
  )
}

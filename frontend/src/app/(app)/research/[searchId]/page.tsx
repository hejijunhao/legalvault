// src/app/(app)/research/[searchId]/page.tsx

"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { ResearchInput } from "@/components/research/search/research-input"
import { BackButton } from "@/components/ui/back-button"
import { ResearchTabs } from "@/components/research/search/research-tabs"
import { useResearch } from "@/contexts/research/research-context"
import { Loader2, AlertCircle } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"

export default function ResearchPage() {
  const params = useParams()
  const router = useRouter()
  const searchId = params.searchId as string
  const { 
    currentSession, 
    getSession, 
    isLoading, 
    error, 
    sendMessage, 
    clearError 
  } = useResearch()
  const [isMounted, setIsMounted] = useState(true)

  useEffect(() => {
    clearError()
    return () => {
      clearError()
      setIsMounted(false)
    }
  }, [clearError])

  useEffect(() => {
    if (!searchId?.trim() || !isMounted) return
    
    if (isLoading) {
      console.log('Already loading, skipping fetch')
      return
    }
    
    if (currentSession?.id === searchId) {
      console.log('Session already loaded')
      return
    }
    
    console.log(`Fetching session data for ${searchId}`)
    
    getSession(searchId)
      .then(session => {
        if (!isMounted) return
        if (!session) {
          console.error('No session data returned')
          router.push('/research')
        }
      })
      .catch(err => {
        if (!isMounted) return
        console.error('Error fetching session:', err)
        router.push('/research')
      })
  }, [searchId, getSession, currentSession, isLoading, router, isMounted])

  const handleSendMessage = async (content: string) => {
    if (!searchId || !content.trim()) return
    
    try {
      await sendMessage(searchId, content)
    } catch (err) {
      console.error("Error sending message:", err)
    }
  }

  const handleBackClick = () => {
    router.push("/research")
  }

  if (isLoading && !currentSession) {
    return (
      <div className="flex min-h-screen items-center justify-center" aria-live="polite" aria-busy="true">
        <div className="flex flex-col items-center">
          <Loader2 className="h-8 w-8 animate-spin text-[#95C066]" aria-hidden="true" />
          <p className="mt-4 text-gray-600">Loading research session...</p>
        </div>
      </div>
    )
  }

  if (!currentSession && !isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center" aria-live="polite">
        <div className="flex flex-col items-center max-w-md w-full px-4">
          <Alert variant="destructive" className="mb-4 w-full">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              {error ? error.message : "Session not found"}
            </AlertDescription>
          </Alert>
          <BackButton 
            customText="Back to Research" 
            className="mt-4" 
            onClick={handleBackClick}
            aria-label="Return to research page"
          />
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen pb-20" aria-live="polite">
      <div className="mx-auto max-w-[1440px] px-8">
        <div className="flex flex-col gap-6 pt-8">
          <BackButton 
            customText="Back to Research" 
            onClick={handleBackClick}
            aria-label="Return to research page"
            className="w-fit"
          />

          <div className="mx-auto max-w-3xl w-full">
            {currentSession && (
              <>
                <h1 className="text-title font-baskerville text-2xl leading-8 text-left italic mb-6">
                  {currentSession.query}
                </h1>
                
                {error && (
                  <Alert variant="destructive" className="my-4">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>{error.message}</AlertDescription>
                  </Alert>
                )}
                
                <ResearchTabs messages={currentSession.messages || []} />
              </>
            )}
          </div>
        </div>
      </div>
      <ResearchInput 
        onSendMessage={handleSendMessage} 
        isLoading={isLoading} 
      />
    </div>
  )
}
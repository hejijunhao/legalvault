// src/app/(app)/research/[searchId]/page.tsx

"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { ResearchInput } from "@/components/research/search/research-input"
import { BackButton } from "@/components/ui/back-button"
import { ResearchTabs } from "@/components/research/search/research-tabs"
import { useResearch } from "@/contexts/research/research-context"
import { Loader2, AlertCircle, ArrowLeft } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { UserMessages } from "@/components/research/search/user-messages"

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
  const [activeTab, setActiveTab] = useState<"answer" | "sources">("answer")

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

  const handleTabChange = (tab: "answer" | "sources") => {
    setActiveTab(tab)
  }

  if (isLoading && !currentSession) {
    return (
      <div className="container mx-auto px-4 py-6 space-y-6">
        <div className="flex items-center space-x-4">
          <div className="w-8 h-8 rounded bg-gray-200 animate-pulse" />
          <div className="h-8 w-64 rounded bg-gray-200 animate-pulse" />
        </div>
        
        <div className="space-y-4">
          <div className="h-12 w-3/4 rounded bg-gray-200 animate-pulse" />
          <div className="space-y-3">
            <div className="h-20 w-full rounded bg-gray-200 animate-pulse" />
            <div className="h-20 w-11/12 rounded bg-gray-200 animate-pulse" />
            <div className="h-20 w-10/12 rounded bg-gray-200 animate-pulse" />
          </div>
        </div>
        
        <div className="fixed bottom-0 left-0 right-0 p-4 bg-white border-t">
          <div className="container mx-auto">
            <div className="h-12 w-full rounded bg-gray-200 animate-pulse" />
          </div>
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
      <div className="mx-auto max-w-[1440px] px-2"> 
        <div className="flex flex-col gap-6 pt-16">
          <div className="flex items-center">
            <BackButton 
              customText="Back to Research" 
              onClick={handleBackClick}
              aria-label="Return to research page"
              className="w-fit"
            />
          </div>

          <div className="mx-auto max-w-3xl w-full -mt-11">
            {currentSession && (
              <>
                <div className="max-w-full break-words">
                  <h1 
                    className="text-left text-[32px] font-normal italic break-words whitespace-pre-wrap leading-[1.3] text-[#111827] font-['Libre_Baskerville'] mb-6" 
                    style={{ 
                      overflowWrap: 'break-word',
                      wordBreak: 'break-word'
                    }}
                  >
                    {currentSession.title || currentSession.query}
                  </h1>
                </div>
                {error && (
                  <Alert variant="destructive" className="my-4">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>{error.message}</AlertDescription>
                  </Alert>
                )}
                
                <div className="mb-4">
                  <ResearchTabs 
                    messages={currentSession.messages || []} 
                    activeTab={activeTab}
                    onTabChange={handleTabChange}
                  />
                </div>
                
                <div className="tab-content mb-32">
                  {activeTab === "answer" && (
                    <div role="tabpanel" aria-labelledby="answer-tab" />
                  )}

                  {activeTab === "sources" && (
                    <div role="tabpanel" aria-labelledby="sources-tab" />
                  )}
                </div>
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
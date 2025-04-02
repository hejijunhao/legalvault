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

  // Get citations for the sources tab
  const citations = currentSession?.messages
    ?.filter(m => m.role === "assistant" && Array.isArray(m.content?.citations) && m.content.citations.length > 0)
    ?.flatMap(m => m.content.citations || [])
    ?.map((citation, index) => ({
      id: String(index),
      ...citation
    })) || []

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
                <h1 className="text-left text-[32px] font-normal italic leading-10 text-[#111827] font-['Libre_Baskerville'] mb-6">
                  {currentSession.title || currentSession.query}
                </h1>
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
                
                {/* Tab content is always visible */}
                <div className="tab-content mb-32">
                  {activeTab === "answer" && (
                    <div role="tabpanel" aria-labelledby="answer-tab">
                      {/* Removed duplicate UserMessages */}
                    </div>
                  )}

                  {activeTab === "sources" && (
                    <div role="tabpanel" aria-labelledby="sources-tab" className="p-2">
                      {citations.length > 0 ? (
                        <div className="space-y-4">
                          {citations.map((citation, index) => (
                            <div key={citation.id} className="flex items-start p-3 border-b border-gray-100 last:border-0">
                              <div className="flex-shrink-0 flex items-center justify-center w-6 h-6 rounded-full bg-gray-200 text-xs font-medium mr-3">
                                {index + 1}
                              </div>
                              <div className="flex-1">
                                <a 
                                  href={citation.url} 
                                  target="_blank" 
                                  rel="noopener noreferrer"
                                  className="text-sm font-medium text-blue-600 hover:underline"
                                >
                                  {citation.text}
                                </a>
                                <p className="text-xs text-gray-500 mt-1 break-all">{citation.url}</p>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="text-center py-8 text-gray-500">
                          <p>No sources available for this research.</p>
                        </div>
                      )}
                    </div>
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
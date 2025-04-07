// src/app/(app)/research/[searchId]/page.tsx

"use client"

import { useEffect, useState, useRef } from "react"
import { useParams, useRouter } from "next/navigation"
import { ResearchInput } from "@/components/research/search/research-input"
import { BackButton } from "@/components/ui/back-button"
import { ResearchTabs } from "@/components/research/search/research-tabs"
import { useResearch } from "@/contexts/research/research-context"
import { Loader2, AlertCircle, ArrowLeft } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { UserMessages } from "@/components/research/search/user-messages"
import { cn } from "@/lib/utils"
import { Message } from "@/services/research/research-api-types";

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
  const headerRef = useRef<HTMLDivElement>(null)
  const [isScrolled, setIsScrolled] = useState(false)

  useEffect(() => {
    clearError()
    return () => {
      clearError()
      setIsMounted(false)
    }
  }, [clearError])

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10)
    }
    
    window.addEventListener('scroll', handleScroll)
    handleScroll() // Check initial scroll position
    
    return () => {
      window.removeEventListener('scroll', handleScroll)
    }
  }, [])

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
      <div 
        ref={headerRef}
        className={cn(
          "sticky top-16 z-40 w-full transition-all duration-300",
          isScrolled
            ? "bg-white/25 backdrop-blur-3xl backdrop-saturate-150 border-b border-white/5 shadow-[0_8px_32px_rgba(0,0,0,0.02)] bg-gradient-to-b from-white/30 to-white/20"
            : "bg-transparent"
        )}
      >
        <div className="flex items-center mx-auto w-full max-w-[1440px] px-4 py-2">
          <div className="">
            <BackButton 
              customText="Back to Research" 
              onClick={handleBackClick}
              aria-label="Return to research page"
              className="w-fit"
            />
          </div>

          <div className="mx-auto max-w-3xl w-full">
            {currentSession && (
              <>
                <div className="relative">
                  <h1 
                    className="w-full text-left text-[24px] font-normal italic break-words whitespace-normal leading-10 text-[#111827] font-['Libre_Baskerville']" 
                  >
                    {(currentSession.title || currentSession.query || '').replace(/\u00A0/g, ' ')}
                  </h1>
                </div>
                <div className="mt-4 flex border-b border-gray-200">
                  <button
                    onClick={() => handleTabChange("answer")}
                    className={cn(
                      "py-2 px-4 text-sm font-medium",
                      activeTab === "answer" 
                        ? "border-b-2 border-black text-black" 
                        : "text-gray-500 hover:text-gray-700"
                    )}
                    aria-selected={activeTab === "answer"}
                    role="tab"
                  >
                    Answer
                  </button>
                  <button
                    onClick={() => handleTabChange("sources")}
                    className={cn(
                      "py-2 px-4 text-sm font-medium flex items-center gap-2",
                      activeTab === "sources" 
                        ? "border-b-2 border-black text-black" 
                        : "text-gray-500 hover:text-gray-700"
                    )}
                    aria-selected={activeTab === "sources"}
                    role="tab"
                  >
                    Sources
                    {(currentSession.messages || [])
                      .filter((m): m is Message => {
                        return m.role === "assistant" && 
                               Array.isArray(m.content?.citations) && 
                               m.content.citations.length > 0;
                      })
                      .flatMap(m => m.content.citations || []).length > 0 && (
                      <span className="inline-flex items-center justify-center w-5 h-5 text-xs font-medium rounded-full bg-gray-200">
                        {(currentSession.messages || [])
                          .filter((m): m is Message => {
                            return m.role === "assistant" && 
                                   Array.isArray(m.content?.citations) && 
                                   m.content.citations.length > 0;
                          })
                          .flatMap(m => m.content.citations || []).length}
                      </span>
                    )}
                  </button>
                </div>
                {error && (
                  <Alert variant="destructive" className="my-4">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>{error.message}</AlertDescription>
                  </Alert>
                )}
              </>
            )}
          </div>
        </div>
      </div>

      <div className="mx-auto w-full max-w-[1440px] px-4">
        <div className="mx-auto max-w-3xl w-full">
          {currentSession && (
            <>
              <div className="tab-content mb-32">
                {activeTab === "answer" && (
                  <div role="tabpanel" aria-labelledby="answer-tab">
                    <UserMessages messages={currentSession.messages || []} />
                  </div>
                )}

                {activeTab === "sources" && (
                  <div role="tabpanel" aria-labelledby="sources-tab" className="p-2">
                    {(currentSession.messages || [])
                      .filter((m): m is Message => {
                        return m.role === "assistant" && 
                               Array.isArray(m.content?.citations) && 
                               m.content.citations.length > 0;
                      })
                      .flatMap(m => m.content.citations || [])
                      ?.map((citation, index) => (
                        <div key={index} className="flex items-start p-3 border-b border-gray-100 last:border-0">
                          <div className="flex-shrink-0 flex items-center justify-center w-6 h-6 rounded-full bg-gray-200 text-xs font-medium mr-3">
                            {index + 1}
                          </div>
                          <div className="flex-1">
                            <a 
                              href={citation.url} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="text-sm text-gray-900 font-medium hover:underline"
                            >
                              {citation.url}
                            </a>
                            <p className="text-sm text-gray-500 mt-1">{citation.text}</p>
                          </div>
                        </div>
                      ))}
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </div>
      <ResearchInput 
        onSendMessage={handleSendMessage} 
        isLoading={isLoading} 
      />
    </div>
  )
}
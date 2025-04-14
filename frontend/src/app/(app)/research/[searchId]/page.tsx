// src/app/(app)/research/[searchId]/page.tsx
"use client"

import { useEffect, useState, useRef, useCallback } from "react"
import { useParams, useRouter, useSearchParams } from "next/navigation"
import { ResearchInput } from "@/components/research/search/research-input"
import { BackButton } from "@/components/ui/back-button"
import { useResearch } from "@/contexts/research/research-context"
import { AlertCircle } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { UserMessages } from "@/components/research/search/user-messages"
import { TypingIndicator } from "@/components/research/search/TypingIndicator"
import { cn } from "@/lib/utils"
import { Message, QueryStatus } from "@/services/research/research-api-types"
import { Skeleton } from '@/components/ui/skeleton'

export default function ResearchPage() {
  console.log("ResearchPage: Component rendering");
  const params = useParams()
  const router = useRouter()
  const searchParams = useSearchParams()
  const searchId = params.searchId as string
  console.log("ResearchPage: searchId =", searchId);
  const initialQuery = searchParams.get("initialQuery")
  console.log("ResearchPage: initialQuery =", initialQuery);
  const { 
    currentSession, 
    getSession, 
    isLoading, 
    error, 
    sendMessage, 
    clearError, 
    setError 
  } = useResearch()
  console.log("ResearchPage: useResearch hook initialized, isLoading =", isLoading, "error =", error);
  const isMountedRef = useRef(true) // Changed from useState
  console.log("ResearchPage: isMountedRef initialized to", isMountedRef.current);
  const [activeTab, setActiveTab] = useState<"answer" | "sources">("answer")
  console.log("ResearchPage: activeTab initialized to", activeTab);
  const headerRef = useRef<HTMLDivElement>(null)
  const [isScrolled, setIsScrolled] = useState(false)
  console.log("ResearchPage: isScrolled initialized to", isScrolled);
  const [messages, setMessages] = useState<Message[]>(initialQuery ? [{
    id: `temp-${Date.now()}`,
    role: "user",
    content: { text: initialQuery },
    sequence: 0,
    status: QueryStatus.PENDING
  }] : [])
  console.log("ResearchPage: messages initialized with", messages.length, "items");
  const [isResponsePending, setIsResponsePending] = useState(!!initialQuery)
  console.log("ResearchPage: isResponsePending initialized to", isResponsePending);
  const [isSessionLoading, setIsSessionLoading] = useState(true)
  console.log("ResearchPage: isSessionLoading initialized to", isSessionLoading);

  useEffect(() => {
    console.log("ResearchPage: Mounting effect - clearing error");
    clearError()
    isMountedRef.current = true // Set ref on mount
    return () => {
      console.log("ResearchPage: Unmounting - clearing error and setting isMountedRef to false");
      clearError()
      isMountedRef.current = false // Set ref on unmount
    }
  }, [clearError])

  useEffect(() => {
    console.log("ResearchPage: Scroll effect - adding scroll event listener");
    const handleScroll = () => {
      const scrolled = window.scrollY > 10;
      console.log("ResearchPage: handleScroll - scrollY =", window.scrollY, "isScrolled =", scrolled);
      setIsScrolled(scrolled)
    }
    window.addEventListener("scroll", handleScroll)
    handleScroll()
    return () => {
      console.log("ResearchPage: Scroll effect cleanup - removing scroll event listener");
      window.removeEventListener("scroll", handleScroll)
    }
  }, [])

  const loadSession = useCallback(async () => {
    console.log("ResearchPage: loadSession - called with searchId =", searchId, "isMounted =", isMountedRef.current);
    if (!searchId?.trim() || !isMountedRef.current) {
      console.log("ResearchPage: loadSession - aborting: invalid searchId or not mounted");
      return false
    }
    const maxLoadAttempts = 3
    let attempts = 0
    let delay = 1000

    while (attempts < maxLoadAttempts) {
      try {
        console.log(`ResearchPage: loadSession - Attempt ${attempts + 1}: Fetching session ${searchId}`);
        const session = await getSession(searchId);
        console.log("ResearchPage: loadSession - Response received:", JSON.stringify(session, null, 2));
        if (!session) {
          console.error(`ResearchPage: loadSession - Attempt ${attempts + 1}: No session data returned`);
          attempts++;
          await new Promise(resolve => setTimeout(resolve, delay));
          delay *= 2;
          continue;
        }
        console.log(`ResearchPage: loadSession - Session loaded: ${session.id}, Messages: ${session.messages?.length || 0}`);
        if (isMountedRef.current) { // Guard state updates
          setMessages(session.messages || []);
          console.log("ResearchPage: loadSession - Updated messages state with", session.messages?.length || 0, "messages");
          setIsResponsePending(false);
          console.log("ResearchPage: loadSession - Set isResponsePending to false");
        }
        return true;
      } catch (err: any) {
        console.error(`ResearchPage: loadSession - Attempt ${attempts + 1} failed:`, {
          message: err.message,
          status: err.status,
          response: err.response ? JSON.stringify(err.response, null, 2) : 'No response'
        });
        attempts++;
        if (attempts < maxLoadAttempts) {
          console.log(`ResearchPage: loadSession - Waiting ${delay}ms before retry`);
          await new Promise(resolve => setTimeout(resolve, delay));
          delay *= 2;
        }
      }
    }
    console.error("ResearchPage: loadSession - All attempts failed to load session");
    if (isMountedRef.current) { // Guard state update
      setError({ message: "Failed to load session. Please try again or return to the research page." });
      console.log("ResearchPage: loadSession - Set error state due to failure");
    }
    return false;
  }, [searchId, getSession, setError]);

  useEffect(() => {
    console.log("ResearchPage: Session load effect - triggered with searchId =", searchId, "isMounted =", isMountedRef.current);
    if (!searchId?.trim() || !isMountedRef.current) {
      console.log("ResearchPage: Session load effect - aborting: invalid searchId or not mounted");
      return
    }

    setIsSessionLoading(true)
    console.log("ResearchPage: Session load effect - Set isSessionLoading to true");
    loadSession().then(success => {
      console.log("ResearchPage: Session load effect - loadSession completed, success =", success);
      if (isMountedRef.current) { // Guard state update
        setIsSessionLoading(false)
        console.log("ResearchPage: Session load effect - Set isSessionLoading to false");
      }
      if (!success && isMountedRef.current) {
        console.log("ResearchPage: Session load effect - Redirecting to /research due to failure");
        router.push("/research")
      } else {
        console.log("ResearchPage: Session load effect - Session loaded successfully, checking for messages");
        console.log("ResearchPage: Session load effect - Current messages length =", messages.length);
      }
    })
  }, [searchId, loadSession, router])

  useEffect(() => {
    console.log("ResearchPage: Current session effect - checking currentSession.id =", currentSession?.id, "searchId =", searchId);
    if (currentSession?.id === searchId && currentSession.messages && currentSession.messages.length > 0 && isMountedRef.current) {
      console.log(`ResearchPage: Current session effect - Current session updated with ${currentSession.messages.length} messages`);
      setMessages(currentSession.messages)
      console.log("ResearchPage: Current session effect - Updated messages state with", currentSession.messages.length, "messages");
      setIsResponsePending(false)
      console.log("ResearchPage: Current session effect - Set isResponsePending to false");
      setIsSessionLoading(false)
      console.log("ResearchPage: Current session effect - Set isSessionLoading to false");
    } else {
      console.log("ResearchPage: Current session effect - No messages to update or session mismatch");
      console.log("ResearchPage: Current session effect - currentSession =", currentSession ? JSON.stringify(currentSession, null, 2) : null);
      console.log("ResearchPage: Current session effect - Attempting to fetch messages for searchId =", searchId);
      console.log("ResearchPage: Current session effect - Should call fetchMessagesForSearch for searchId =", searchId);
    }
  }, [currentSession, searchId])

  const handleSendMessage = async (content: string) => {
    console.log("ResearchPage: handleSendMessage - called with content =", content);
    if (!searchId || !content.trim() || !isMountedRef.current) {
      console.log("ResearchPage: handleSendMessage - aborted: invalid searchId, empty content, or not mounted");
      return
    }

    console.log("ResearchPage: handleSendMessage - Adding temporary user message");
    if (isMountedRef.current) { // Guard state update
      setMessages(prev => {
        const newMessages = [...prev, {
          id: `temp-${Date.now()}`,
          role: "user" as "user",
          content: { text: content },
          sequence: 0,
          status: QueryStatus.PENDING
        }]
        console.log("ResearchPage: handleSendMessage - Updated messages state with", newMessages.length, "messages");
        return newMessages;
      })
      setIsResponsePending(true)
      console.log("ResearchPage: handleSendMessage - Set isResponsePending to true");
    }

    try {
      console.log("ResearchPage: handleSendMessage - Sending message to API");
      await sendMessage(searchId, content)
      console.log("ResearchPage: handleSendMessage - Message sent successfully");
      setTimeout(async () => {
        console.log("ResearchPage: handleSendMessage - Checking for updated session after 500ms");
        if (isMountedRef.current) { // Guard state updates
          if (currentSession?.id === searchId && currentSession.messages) {
            console.log("ResearchPage: handleSendMessage - Updating messages from currentSession");
            setMessages(currentSession.messages)
            console.log("ResearchPage: handleSendMessage - Updated messages state with", currentSession.messages.length, "messages");
          } else {
            console.log("ResearchPage: handleSendMessage - Fetching updated session");
            const updatedSession = await getSession(searchId)
            if (updatedSession?.messages) {
              console.log("ResearchPage: handleSendMessage - Updating messages from fetched session");
              setMessages(updatedSession.messages)
              console.log("ResearchPage: handleSendMessage - Updated messages state with", updatedSession.messages.length, "messages");
            } else {
              console.log("ResearchPage: handleSendMessage - No messages in updated session");
            }
            setIsResponsePending(false)
            console.log("ResearchPage: handleSendMessage - Set isResponsePending to false");
          }
        }
      }, 500)
    } catch (err) {
      console.error("ResearchPage: handleSendMessage - Error sending message:", err)
      if (isMountedRef.current) { // Guard state update
        setIsResponsePending(false)
        console.log("ResearchPage: handleSendMessage - Set isResponsePending to false due to error");
      }
    }
  }

  const handleBackClick = () => {
    console.log("ResearchPage: handleBackClick - Redirecting to /research");
    router.push("/research")
  }
  const handleTabChange = (tab: "answer" | "sources") => {
    console.log("ResearchPage: handleTabChange - Switching to tab", tab);
    setActiveTab(tab)
  }

  const handleRetryLoading = () => {
    console.log("ResearchPage: handleRetryLoading - Initiating session reload");
    setIsSessionLoading(true)
    console.log("ResearchPage: handleRetryLoading - Set isSessionLoading to true");
    loadSession().then(success => {
      console.log("ResearchPage: handleRetryLoading - loadSession completed, success =", success);
      if (isMountedRef.current) { // Guard state update
        setIsSessionLoading(false)
        console.log("ResearchPage: handleRetryLoading - Set isSessionLoading to false");
      }
      if (!success) {
        console.log("ResearchPage: handleRetryLoading - Redirecting to /research due to failure");
        router.push("/research")
      }
    })
  }

  console.log("ResearchPage: Rendering with currentSession =", !!currentSession, "initialQuery =", initialQuery, "isLoading =", isLoading, "isSessionLoading =", isSessionLoading, "messages.length =", messages.length);
  if (!currentSession && !initialQuery && !isLoading && !isSessionLoading && messages.length === 0) {
    console.log("ResearchPage: Rendering error state - no session or messages");
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

  if (isSessionLoading || isLoading) {
    console.log("ResearchPage: Rendering loading skeleton");
    return (
      <div className="flex h-screen flex-col bg-gray-50">
        <header className="sticky top-0 z-10 border-b bg-white px-4 py-3 shadow-sm sm:px-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Skeleton className="h-5 w-5 rounded-full" />
              <Skeleton className="h-6 w-48 rounded" />
            </div>
          </div>
          <Skeleton className="mt-1 h-4 w-64 rounded" />
        </header>
        <div className="flex-1 overflow-y-auto px-4 pb-20 pt-4 sm:px-6 space-y-4">
          <div className="flex justify-start">
            <Skeleton className="h-16 w-3/4 rounded-lg" />
          </div>
          <div className="flex justify-end">
            <Skeleton className="h-12 w-2/3 rounded-lg" />
          </div>
          <div className="flex justify-start">
            <Skeleton className="h-20 w-4/5 rounded-lg" />
          </div>
          <div className="flex justify-end">
            <Skeleton className="h-10 w-1/2 rounded-lg" />
          </div>
        </div>
        <div className="sticky bottom-0 border-t bg-white px-4 py-4 sm:px-6">
          <Skeleton className="h-10 w-full rounded" />
        </div>
      </div>
    )
  }

  console.log("ResearchPage: Rendering main content with activeTab =", activeTab);
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
          <BackButton 
            customText="Back to Research" 
            onClick={handleBackClick}
            aria-label="Return to research page"
            className="w-fit"
          />
          <div className="mx-auto max-w-3xl w-full">
            <h1 className="text-left text-[24px] font-normal italic break-words whitespace-normal leading-10 text-[#111827] font-['Libre_Baskerville']">
              {initialQuery || currentSession?.title || currentSession?.query || "Research Session"}
            </h1>
            <div className="mt-4 flex border-b border-gray-200">
              <button
                onClick={() => handleTabChange("answer")}
                className={cn(
                  "py-2 px-4 text-sm font-medium",
                  activeTab === "answer" ? "border-b-2 border-black text-black" : "text-gray-500 hover:text-gray-700"
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
                  activeTab === "sources" ? "border-b-2 border-black text-black" : "text-gray-500 hover:text-gray-700"
                )}
                aria-selected={activeTab === "sources"}
                role="tab"
              >
                Sources
                {messages.filter(m => m.role === "assistant" && Array.isArray(m.content?.citations) && m.content.citations.length > 0)
                  .flatMap(m => m.content.citations || []).length > 0 && (
                  <span className="inline-flex items-center justify-center w-5 h-5 text-xs font-medium rounded-full bg-gray-200">
                    {messages.filter(m => m.role === "assistant" && Array.isArray(m.content?.citations) && m.content.citations.length > 0)
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
          </div>
        </div>
      </div>

      <div className="mx-auto w-full max-w-[1440px] px-4">
        <div className="mx-auto max-w-3xl w-full">
          <div className="tab-content mb-32">
            {activeTab === "answer" && (
              <div role="tabpanel" aria-labelledby="answer-tab">
                {messages.length > 0 ? (
                  <UserMessages messages={messages} />
                ) : (
                  <div className="py-10 text-center text-gray-500">
                    <p>No messages available for this search.</p>
                    <p className="mt-2 text-sm">If you believe this is an error, you can try refreshing.</p>
                    <button 
                      onClick={handleRetryLoading}
                      className="mt-4 text-sm px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
                    >
                      Reload Messages
                    </button>
                  </div>
                )}
                {isResponsePending && <TypingIndicator />}
              </div>
            )}
            {activeTab === "sources" && (
              <div role="tabpanel" aria-labelledby="sources-tab" className="p-2">
                {messages.filter(m => m.role === "assistant" && Array.isArray(m.content?.citations) && m.content.citations.length > 0)
                  .flatMap(m => m.content.citations || [])
                  .map((citation, index) => (
                    <div key={index} className="flex items-start p-3 border-b border-gray-100 last:border-0">
                      <div className="flex-shrink-0 flex items-center justify-center w-6 h-6 rounded-full bg-gray-200 text-xs font-medium mr-3">
                        {index + 1}
                      </div>
                      <div className="flex-1">
                        <a href={citation.url} target="_blank" rel="noopener noreferrer" className="text-sm text-gray-900 font-medium hover:underline">
                          {citation.url}
                        </a>
                        <p className="text-sm text-gray-500 mt-1">{citation.text}</p>
                      </div>
                    </div>
                  ))}
              </div>
            )}
          </div>
        </div>
      </div>
      <ResearchInput 
        onSubmit={handleSendMessage} 
        isLoading={isLoading} 
      />
    </div>
  )
}
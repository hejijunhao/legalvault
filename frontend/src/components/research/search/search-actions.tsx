// src/components/research/search/search-actions.tsx

"use client"

import { useState } from "react"
import { Bookmark, Share2, FolderPlus, FileText, RefreshCw } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import { useResearch, QueryStatus } from "@/contexts/research/research-context"
import { toast } from "sonner"

interface SearchActionsProps {
  sessionId: string
}

export function SearchActions({ sessionId }: SearchActionsProps) {
  const [showCitations, setShowCitations] = useState(false)
  const { currentSession, sendMessage, isLoading } = useResearch()
  
  // Check if the session has failed or needs clarification
  const hasFailedStatus = currentSession?.status === QueryStatus.FAILED ||
    currentSession?.status === QueryStatus.NEEDS_CLARIFICATION

  const handleRetry = async () => {
    if (!currentSession?.messages) {
      toast.error("No messages to retry")
      return
    }
    
    try {
      const failedMessage = currentSession.messages.find(m => 
        m.role === "user" && m.status === QueryStatus.FAILED
      )
      
      if (!failedMessage?.content?.text) {
        toast.error("No failed message to retry")
        return
      }
      
      await sendMessage(sessionId, failedMessage.content.text)
      toast.success("Message resent successfully")
    } catch (error) {
      console.error("Error retrying message:", error)
    }
  }

  // Get citations from the current session if available
  const citations = currentSession?.messages
    ?.filter(m => m.role === "assistant" && Array.isArray(m.content?.citations) && m.content.citations.length > 0)
    ?.flatMap(m => m.content.citations || [])
    ?.map((citation, index) => ({
      id: String(index),
      title: citation.text.substring(0, 50) + (citation.text.length > 50 ? "..." : ""),
      url: citation.url,
      publisher: citation.metadata?.publisher || "Source",
      date: citation.metadata?.date || new Date().getFullYear().toString()
    })) || []

  return (
    <div className="mb-6">
      <div className="flex justify-center gap-2">
        {hasFailedStatus && (
          <button 
            className="flex items-center gap-[6px] rounded-[12px] bg-[rgba(239,68,68,0.15)] px-2 py-1 hover:bg-[rgba(239,68,68,0.25)]"
            onClick={handleRetry}
            disabled={isLoading}
            aria-label="Retry failed message"
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            <span className="text-sm text-[#1C1C1C]">Retry</span>
          </button>
        )}
        <button className="flex items-center gap-[6px] rounded-[12px] bg-[rgba(137,146,169,0.30)] px-2 py-1">
          <Bookmark className="h-4 w-4" />
          <span className="text-sm text-[#1C1C1C]">Bookmark</span>
        </button>
        <button className="flex items-center gap-[6px] rounded-[12px] bg-[rgba(137,146,169,0.30)] px-2 py-1">
          <FolderPlus className="h-4 w-4" />
          <span className="text-sm text-[#1C1C1C]">Add to Workspace</span>
        </button>
        <button className="flex items-center gap-[6px] rounded-[12px] bg-[rgba(137,146,169,0.30)] px-2 py-1">
          <Share2 className="h-4 w-4" />
          <span className="text-sm text-[#1C1C1C]">Share</span>
        </button>
        <button
          className="flex items-center gap-[6px] rounded-[12px] bg-[rgba(159,232,112,0.20)] px-2 py-1 hover:bg-[rgba(159,232,112,0.30)]"
          onClick={() => setShowCitations(!showCitations)}
          disabled={citations.length === 0}
        >
          <FileText className="h-4 w-4" />
          <span className="text-sm text-[#1C1C1C]">Citations</span>
        </button>
      </div>

      <AnimatePresence>
        {showCitations && citations.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="mt-4 overflow-hidden"
          >
            <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
              <h3 className="mb-3 text-sm font-medium text-gray-700">Sources & Citations</h3>
              <div className="space-y-3">
                {citations.map((citation) => (
                  <div key={citation.id} className="text-sm">
                    <a
                      href={citation.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="font-medium text-blue-600 hover:underline"
                    >
                      {citation.title}
                    </a>
                    <p className="text-xs text-gray-500">
                      {citation.publisher}, {citation.date}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

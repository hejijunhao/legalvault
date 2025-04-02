// src/components/research/search/search-actions.tsx

"use client"

import { useState } from "react"
import { Bookmark, Share2, FolderPlus, FileText, RefreshCw } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import { useResearch, QueryStatus } from "@/contexts/research/research-context"
import { toast } from "sonner"
import { cn } from "@/lib/utils"

interface SearchActionsProps {
  sessionId: string
}

export function SearchActions({ sessionId }: SearchActionsProps) {
  const [showCitations, setShowCitations] = useState(false)
  const { currentSession, sendMessage, isLoading } = useResearch()
  
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

  const citations = currentSession?.messages
    ?.filter(m => m.role === "assistant" && Array.isArray(m.content?.citations) && m.content.citations.length > 0)
    ?.flatMap(m => m.content.citations || [])
    ?.map((citation, index) => ({
      id: String(index),
      ...citation
    })) || []

  const baseButtonClasses = "flex items-center gap-[6px] px-2 py-1 rounded-[12px] bg-[rgba(137,146,169,0.30)] text-[#1C1C1C]"

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={() => setShowCitations(!showCitations)}
        className={cn(
          "flex items-center gap-[6px] px-2 py-1 rounded-[12px] text-[#1C1C1C]",
          showCitations ? "bg-[#9FE870]" : "bg-[rgba(159,232,112,0.20)] hover:bg-[rgba(159,232,112,0.30)]"
        )}
      >
        <FileText className="h-4 w-4" />
        <span className="text-sm">Citations</span>
      </button>

      <button
        onClick={() => {
          toast.info("Share feature coming soon")
        }}
        className={baseButtonClasses}
      >
        <Share2 className="h-4 w-4" />
        <span className="text-sm">Share</span>
      </button>

      <button
        onClick={() => {
          toast.info("Add to workspace feature coming soon")
        }}
        className={baseButtonClasses}
      >
        <FolderPlus className="h-4 w-4" />
        <span className="text-sm">Add to Workspace</span>
      </button>

      <button
        onClick={() => {
          toast.info("Bookmark feature coming soon")
        }}
        className={baseButtonClasses}
      >
        <Bookmark className="h-4 w-4" />
        <span className="text-sm">Bookmark</span>
      </button>

      {hasFailedStatus && (
        <button
          onClick={handleRetry}
          disabled={isLoading}
          className={cn(baseButtonClasses, "bg-[rgba(239,68,68,0.15)] hover:bg-[rgba(239,68,68,0.25)]")}
        >
          <RefreshCw className={cn("h-4 w-4", isLoading && "animate-spin")} />
          <span className="text-sm">Retry</span>
        </button>
      )}

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
                    <p className="text-xs text-gray-500">{citation.url}</p>
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

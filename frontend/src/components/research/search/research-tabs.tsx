// src/components/research/search/research-tabs.tsx

"use client"

import { useState, useEffect } from "react"
import { cn } from "@/lib/utils"
import { UserMessages } from "./user-messages"
import { Message, Citation } from "@/contexts/research/research-context"

interface ResearchTabsProps {
  messages: Message[]
  activeTab?: "answer" | "sources"
  onTabChange?: (tab: "answer" | "sources") => void
}

export function ResearchTabs({ messages, activeTab: externalActiveTab, onTabChange }: ResearchTabsProps) {
  const [internalActiveTab, setInternalActiveTab] = useState<"answer" | "sources">("answer")
  
  // Determine which active tab state to use (internal or external)
  const activeTab = externalActiveTab !== undefined ? externalActiveTab : internalActiveTab

  // Sync internal state with external state when provided
  useEffect(() => {
    if (externalActiveTab !== undefined) {
      setInternalActiveTab(externalActiveTab)
    }
  }, [externalActiveTab])

  // Handle tab change
  const handleTabChange = (tab: "answer" | "sources") => {
    setInternalActiveTab(tab)
    if (onTabChange) {
      onTabChange(tab)
    }
  }

  // Extract citations from assistant messages
  const citations = messages
    ?.filter(m => m.role === "assistant" && Array.isArray(m.content?.citations) && m.content.citations.length > 0)
    ?.flatMap(m => m.content.citations || [])
    ?.map((citation, index) => ({
      id: String(index),
      ...citation
    })) || []

  return (
    <div className="w-full">
      <div className="flex border-b border-gray-200 mb-4">
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
          {citations.length > 0 && (
            <span className="inline-flex items-center justify-center w-5 h-5 text-xs font-medium rounded-full bg-gray-200">
              {citations.length}
            </span>
          )}
        </button>
      </div>

      <div className="tab-content">
        {activeTab === "answer" && (
          <div role="tabpanel" aria-labelledby="answer-tab">
            <UserMessages messages={messages} />
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
    </div>
  )
}
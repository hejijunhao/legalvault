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
          <div role="tabpanel" aria-labelledby="sources-tab" className="px-1">
            {citations.length > 0 ? (
              <div className="space-y-4">
                {citations.map((citation, index) => (
                  <div key={citation.id} className="group flex items-start gap-3 py-2 px-3 -mx-3 rounded hover:bg-gray-50/50 transition-colors">
                    <div className="flex-shrink-0 flex items-center justify-center w-6 h-6 rounded-full bg-gray-100 text-xs font-medium text-gray-600 mt-0.5">
                      {index + 1}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-1.5 mb-1">
                        <img 
                          src={`https://www.google.com/s2/favicons?domain=${new URL(citation.url).hostname}&sz=32`}
                          alt=""
                          className="w-3.5 h-3.5"
                          onError={(e) => {
                            e.currentTarget.src = '/fallback-favicon.png'
                            e.currentTarget.onerror = null
                          }}
                        />
                        <span className="text-xs text-gray-500 truncate">
                          {new URL(citation.url).hostname.replace('www.', '')}
                        </span>
                      </div>
                      <a 
                        href={citation.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="block"
                      >
                        <h3 className="text-sm font-medium text-gray-900 group-hover:text-blue-600 mb-1 line-clamp-2">
                          {citation.text}
                        </h3>
                        <p className="text-xs text-gray-600 line-clamp-2">
                          {citation.metadata?.snippet || 'No preview available'}
                        </p>
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-6 text-sm text-gray-500">
                <p>No sources available for this research.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
// src/components/research/search/citation-hovercard.tsx

"use client"

import { Citation } from "@/contexts/research/research-context"
import { HoverCard, HoverCardTrigger, HoverCardContent } from "@/components/ui/hover-card"

interface CitationHovercardProps {
  index: number
  citation: Citation
}

export function CitationHovercard({ index, citation }: CitationHovercardProps) {
  return (
    <HoverCard openDelay={0} closeDelay={0}>
      <HoverCardTrigger asChild>
        <button
          className="inline-flex h-[18px] min-w-[18px] select-none items-center justify-center rounded-[4px] bg-blue-50 px-1.5 text-xs font-medium text-gray-900 hover:bg-blue-100 transition-colors"
        >
          ({index})
        </button>
      </HoverCardTrigger>
      <HoverCardContent 
        align="start" 
        className="w-80 p-4 bg-white rounded-lg border border-gray-200 shadow-lg"
        sideOffset={5}
      >
        <div className="space-y-2">
          <p className="text-sm text-gray-600 leading-relaxed">{citation.text}</p>
          {citation.url && (
            <a 
              href={citation.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-blue-600 hover:underline inline-flex items-center gap-1"
            >
              View source
              <svg className="h-3 w-3" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M5.22 14.78a.75.75 0 001.06 0l7.22-7.22v5.69a.75.75 0 001.5 0v-7.5a.75.75 0 00-.75-.75h-7.5a.75.75 0 000 1.5h5.69l-7.22 7.22a.75.75 0 000 1.06z" />
              </svg>
            </a>
          )}
        </div>
      </HoverCardContent>
    </HoverCard>
  )
}
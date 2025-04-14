// src/components/research/search/citation-hovercard.tsx

"use client"

import { Citation } from "@/contexts/research/research-context"
import { HoverCard, HoverCardTrigger, HoverCardContent } from "@/components/ui/hover-card"

interface CitationHovercardProps {
  index: number
  citation: Citation
}

export function CitationHovercard({ index, citation }: CitationHovercardProps) {
  // Extract domain from URL if available
  const domain = citation.url ? new URL(citation.url).hostname.replace('www.', '') : null

  return (
    <HoverCard openDelay={0} closeDelay={0}>
      <HoverCardTrigger asChild>
        <button
          className="inline-flex h-[18px] min-w-[18px] select-none items-center justify-center rounded-sm bg-[#F0F7FF] px-[5px] text-[11px] font-medium text-[#0066CC] hover:bg-[#E0EFFF] transition-colors mx-[3px] border border-[#E0EFFF] relative top-[1px]"
        >
          {index}
        </button>
      </HoverCardTrigger>
      <HoverCardContent 
        align="start" 
        className="w-[400px] p-4 bg-white rounded-lg border border-gray-200 shadow-lg"
        sideOffset={5}
      >
        <div className="space-y-3">
          {/* Source Info */}
          {domain && (
            <div className="flex items-center gap-1.5 text-xs text-gray-500">
              <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
              </svg>
              <span>{domain}</span>
            </div>
          )}

          {/* Citation Text */}
          <div className="text-sm text-gray-600 leading-relaxed">
            <span className="line-clamp-4">{citation.text}</span>
          </div>

          {/* Source Link */}
          {citation.url && (
            <a 
              href={citation.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-3 py-1.5 text-sm text-blue-600 hover:text-blue-700 bg-blue-50 hover:bg-blue-100 rounded-md transition-colors"
            >
              View full source
              <svg className="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M5.22 14.78a.75.75 0 001.06 0l7.22-7.22v5.69a.75.75 0 001.5 0v-7.5a.75.75 0 00-.75-.75h-7.5a.75.75 0 000 1.5h5.69l-7.22 7.22a.75.75 0 000 1.06z" />
              </svg>
            </a>
          )}
        </div>
      </HoverCardContent>
    </HoverCard>
  )
}
// src/components/research/search/source-citations.tsx

"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Copy, CheckCircle2, ExternalLink } from "lucide-react"
import { Button } from "@/components/ui/button"
import { HoverCard, HoverCardContent, HoverCardTrigger } from "@/components/ui/hover-card"
import { toast } from "sonner"
import { cn } from "@/lib/utils"
import { Citation } from "@/contexts/research/research-context"

interface SourceCitationsProps {
  sources: Citation[]
  isLoading?: boolean
}

export function SourceCitations({ sources, isLoading = false }: SourceCitationsProps) {
  const [copiedUrl, setCopiedUrl] = useState<string | null>(null)

  const handleCopy = async (citation: Citation) => {
    try {
      const citationText = `${citation.text}\nSource: ${citation.url}`
      await navigator.clipboard.writeText(citationText)
      setCopiedUrl(citation.url)
      toast.success("Citation copied to clipboard")
      setTimeout(() => setCopiedUrl(null), 2000)
    } catch (error) {
      toast.error("Failed to copy citation")
      console.error("Error copying citation:", error)
    }
  }

  const handleVisit = (url: string) => {
    window.open(url, "_blank", "noopener,noreferrer")
  }

  const getDisplayName = (url: string): string => {
    try {
      const hostname = new URL(url).hostname
      // Remove www. and .com/.org etc
      return hostname.replace(/^www\./, "").replace(/\.[^.]+$/, "")
    } catch {
      return url
    }
  }

  if (isLoading) {
    return (
      <div className="mb-6 flex animate-pulse space-x-2">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="h-6 w-24 rounded-full bg-gray-200"
          />
        ))}
      </div>
    )
  }

  if (!sources?.length) {
    return null
  }

  return (
    <div className="mb-6 flex flex-wrap gap-2">
      {sources.map((source, index) => (
        <HoverCard key={`${source.url}-${index}`}>
          <HoverCardTrigger asChild>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              className={cn(
                "group relative inline-flex items-center gap-2",
                "rounded-full bg-white px-3 py-1.5",
                "shadow-sm transition-all duration-200",
                "hover:shadow-md hover:ring-1 hover:ring-[#95C066]/20"
              )}
            >
              <span className="text-xs text-gray-700 line-clamp-1">
                {getDisplayName(source.url)}
              </span>
              
              <div className="flex items-center gap-1">
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="h-5 w-5 p-0 opacity-0 transition-opacity group-hover:opacity-100"
                  onClick={(e) => {
                    e.preventDefault()
                    handleCopy(source)
                  }}
                  aria-label="Copy citation"
                >
                  {copiedUrl === source.url ? (
                    <CheckCircle2 className="h-3 w-3 text-green-500" />
                  ) : (
                    <Copy className="h-3 w-3 text-gray-500" />
                  )}
                </Button>

                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="h-5 w-5 p-0 opacity-0 transition-opacity group-hover:opacity-100"
                  onClick={(e) => {
                    e.preventDefault()
                    handleVisit(source.url)
                  }}
                  aria-label="Visit source"
                >
                  <ExternalLink className="h-3 w-3 text-gray-500" />
                </Button>
              </div>
            </motion.div>
          </HoverCardTrigger>

          <HoverCardContent 
            align="start" 
            className="w-80 p-4"
            style={{ zIndex: 100 }}
          >
            <div className="space-y-2">
              <p className="text-xs text-gray-500 line-clamp-3">
                {source.text}
              </p>
              <p className="text-xs text-[#95C066]">
                {getDisplayName(source.url)}
              </p>
            </div>
          </HoverCardContent>
        </HoverCard>
      ))}
    </div>
  )
}

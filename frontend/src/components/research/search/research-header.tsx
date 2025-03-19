// src/components/research/search/research-header.tsx

"use client"

import { Share2, Copy, CheckCircle2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { toast } from "sonner"
import { cn } from "@/lib/utils"
import { QueryStatus, QueryType } from "@/contexts/research/research-context"

interface ResearchHeaderProps {
  query: string
  queryType?: QueryType
  status?: QueryStatus
  createdAt?: string
  className?: string
}

const queryTypeLabels: Record<QueryType, string> = {
  [QueryType.COURT_CASE]: "Court Case",
  [QueryType.LEGISLATIVE]: "Legislative",
  [QueryType.COMMERCIAL]: "Commercial",
  [QueryType.GENERAL]: "General"
}

export function ResearchHeader({
  query,
  queryType,
  status = QueryStatus.COMPLETED,
  createdAt,
  className
}: ResearchHeaderProps) {
  const handleShare = async () => {
    try {
      await navigator.share({
        title: "Research Query",
        text: query
      })
      toast.success("Query shared successfully")
    } catch (error) {
      if ((error as Error).name !== "AbortError") {
        toast.error("Failed to share query")
      }
    }
  }

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(query)
      toast.success("Query copied to clipboard")
    } catch (error) {
      toast.error("Failed to copy query")
    }
  }

  const getQueryTypeLabel = () => {
    if (!queryType) return null;
    return queryTypeLabels[queryType];
  };

  const getStatusColor = () => {
    switch (status) {
      case QueryStatus.COMPLETED:
        return "bg-[#95C066]";
      case QueryStatus.FAILED:
        return "bg-red-500";
      case QueryStatus.NEEDS_CLARIFICATION:
        return "bg-yellow-500";
      case QueryStatus.IRRELEVANT:
        return "bg-gray-400";
      default:
        return "bg-gray-400";
    }
  };

  return (
    <div className={cn("relative", className)}>
      {/* Status Indicator */}
      <div className="absolute -left-4 top-3">
        <div className={cn("h-2 w-2 rounded-full", getStatusColor())} />
      </div>

      {/* Query Title */}
      <div className="space-y-1">
        <h1 className={cn(
          "text-[32px] font-normal italic leading-normal text-[#1c1c1c]",
          "font-['Libre_Baskerville']"
        )}>
          {query}
        </h1>

        {getQueryTypeLabel() && (
          <p className="text-sm text-gray-500">
            {getQueryTypeLabel()}
          </p>
        )}
      </div>

      {/* Action Buttons */}
      <div className="absolute -right-2 top-2 flex items-center gap-1">
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="h-8 w-8"
          onClick={handleCopy}
          aria-label="Copy query"
        >
          <Copy className="h-4 w-4" />
        </Button>

        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="h-8 w-8"
          onClick={handleShare}
          aria-label="Share query"
        >
          <Share2 className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}

// src/components/library/search/sources-block.tsx

"use client"

import { useState } from "react"
import { SourceBlock } from "./source-block"

interface Source {
  id: string
  title: string
  type: string
  date: string
  url?: string
  fileSize?: string
  lastModified?: string
  creator?: string
}

interface SourcesBlockProps {
  sources: Source[]
}

export function SourcesBlock({ sources }: SourcesBlockProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null)

  const toggleExpand = (id: string) => {
    setExpandedId(expandedId === id ? null : id)
  }

  return (
    <div className="space-y-2">
      {sources.map((source) => (
        <SourceBlock
          key={source.id}
          {...source}
          isExpanded={expandedId === source.id}
          onToggle={() => toggleExpand(source.id)}
        />
      ))}
    </div>
  )
}


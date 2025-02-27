// src/components/research/search/source-citations.tsx

"use client"

import { motion } from "framer-motion"

interface Source {
  id: string
  title: string
  url: string
}

interface SourceCitationsProps {
  sources: Source[]
}

export function SourceCitations({ sources }: SourceCitationsProps) {
  return (
    <div className="mb-6 flex flex-wrap gap-2">
      {sources.map((source, index) => (
        <motion.a
          key={source.id}
          href={source.url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center rounded-full bg-white px-3 py-1 text-xs text-gray-700 shadow-sm hover:bg-gray-50"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: index * 0.1 }}
        >
          {source.title}
        </motion.a>
      ))}
    </div>
  )
}


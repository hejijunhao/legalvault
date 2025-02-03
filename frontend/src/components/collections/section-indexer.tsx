// src/components/collections/section-indexer.tsx

"use client"

import { useRef } from "react"
import { motion } from "framer-motion"
import { cn } from "@/lib/utils"

interface Section {
  id: string
  title: string
  ref?: React.RefObject<HTMLElement>
}

interface SectionIndexerProps {
  sections: Section[]
  currentSectionId: string
  onSectionClick: (sectionId: string) => void
}

export function SectionIndexer({ sections, currentSectionId, onSectionClick }: SectionIndexerProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  // Find the current section index
  const currentIndex = sections.findIndex((section) => section.id === currentSectionId)

  return (
    <div ref={containerRef} className="w-full">
      <div className="relative rounded-2xl border border-white/20 bg-white/80 px-4 py-6 shadow-lg backdrop-blur-lg">
        {/* Sections list */}
        <div className="relative space-y-4">
          {sections.map((section) => {
            const isActive = section.id === currentSectionId

            return (
              <motion.button
                key={section.id}
                className={cn(
                  "relative block w-full cursor-pointer rounded-lg px-4 py-2 text-left text-sm transition-colors",
                  "hover:bg-black/5",
                  isActive ? "bg-blue-50 font-medium text-blue-500" : "text-gray-600 hover:bg-gray-100",
                )}
                onClick={() => onSectionClick(section.id)}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                {section.title}
              </motion.button>
            )
          })}
        </div>
      </div>
    </div>
  )
}




// src/components/library/section-nav.tsx

"use client"

import { motion } from "framer-motion"
import { cn } from "@/lib/utils"
import type React from "react" // Import React

interface Section {
  id: string
  name: string
  icon: React.ElementType
  count: number
}

interface SectionNavProps {
  sections: Section[]
  activeSection: string
  onSectionClick: (sectionId: string) => void
}

export function SectionNav({ sections, activeSection, onSectionClick }: SectionNavProps) {
  return (
    <nav className="h-full space-y-3 p-6" aria-label="Section navigation">
      {sections.map((section) => {
        const Icon = section.icon
        return (
          <motion.button
            key={section.id}
            onClick={() => onSectionClick(section.id)}
            className={cn(
              "flex w-full items-center gap-3 rounded-lg px-4 py-3 text-sm transition-colors",
              "hover:bg-neutral-100",
              activeSection === section.id ? "bg-blue-50 text-blue-600" : "text-neutral-600",
            )}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <Icon className="h-4 w-4" />
            <span className="flex-1 text-left">{section.name}</span>
            <span className="text-xs tabular-nums text-neutral-400">{section.count}</span>
          </motion.button>
        )
      })}
    </nav>
  )
}


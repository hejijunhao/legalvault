// src/components/library/type-categories.tsx

"use client"

import { useRef, useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Card } from "@/components/ui/card"
import {
  FileText,
  FileType,
  FileTextIcon as TextFile,
  FileCode,
  Table2,
  FileSpreadsheet,
  FileInput,
  Image,
  Video,
  Camera,
  Music,
  Mail,
  MessageSquare,
  Phone,
  StickyNote,
  BookOpen,
  Paperclip,
  ClipboardList,
  Expand,
  Minimize2,
} from "lucide-react"

const categories = [
  {
    name: "Documents",
    icon: FileText,
    bgColor: "bg-blue-50",
    textColor: "text-blue-500",
    description: "Document file formats",
    types: [
      { name: "Word/Pages", icon: FileType },
      { name: "PDF", icon: FileText },
      { name: "Text Files", icon: TextFile },
      { name: "Markdown", icon: FileCode },
    ],
  },
  {
    name: "Spreadsheets",
    icon: Table2,
    bgColor: "bg-green-50",
    textColor: "text-green-500",
    description: "Data and calculations",
    types: [
      { name: "Excel/Numbers", icon: FileSpreadsheet },
      { name: "CSV", icon: Table2 },
      { name: "Google Sheets", icon: FileInput },
    ],
  },
  {
    name: "Media",
    icon: Image,
    bgColor: "bg-purple-50",
    textColor: "text-purple-500",
    description: "Rich media content",
    types: [
      { name: "Images/Photos", icon: Image },
      { name: "Videos", icon: Video },
      { name: "Screenshots", icon: Camera },
      { name: "Audio/Voice", icon: Music },
    ],
  },
  {
    name: "Communications",
    icon: MessageSquare,
    bgColor: "bg-amber-50",
    textColor: "text-amber-500",
    description: "Communication records",
    types: [
      { name: "Emails", icon: Mail },
      { name: "Chat Logs", icon: MessageSquare },
      { name: "Call Records", icon: Phone },
    ],
  },
  {
    name: "Notes & Snippets",
    icon: StickyNote,
    bgColor: "bg-rose-50",
    textColor: "text-rose-500",
    description: "Quick information capture",
    types: [
      { name: "Meeting Notes", icon: BookOpen },
      { name: "Research Notes", icon: Paperclip },
      { name: "Web Clips", icon: ClipboardList },
      { name: "Quick Notes", icon: StickyNote },
    ],
  },
]

export function TypeCategories() {
  const [isExpanded, setIsExpanded] = useState(false)
  const [activeIndex, setActiveIndex] = useState(0)
  const toggleExpansion = () => setIsExpanded(!isExpanded)
  const containerRef = useRef<HTMLDivElement>(null)

  const handleScroll = () => {
    if (containerRef.current && isExpanded) {
      const scrollPosition = containerRef.current.scrollLeft
      const cardWidth = containerRef.current.offsetWidth / 4
      const newActiveIndex = Math.round(scrollPosition / cardWidth)
      setActiveIndex(newActiveIndex)
    }
  }

  return (
    <div className="relative h-full w-full">
      <AnimatePresence>
        <motion.div
          layout
          initial={false}
          animate={{
            width: isExpanded ? "100%" : "100%",
            transition: { type: "spring", stiffness: 300, damping: 30 },
          }}
          className={`relative h-full overflow-hidden rounded-xl border border-white/20 bg-white/90 backdrop-blur-md transition-all duration-500`}
        >
          {/* Header */}
          <motion.div
            layout
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
            className="flex items-center justify-between border-b border-white/10 p-4"
          >
            <div>
              <motion.h2
                layout
                transition={{ type: "spring", stiffness: 300, damping: 30 }}
                className="text-lg font-medium text-[#1C1C1C]"
              >
                Types
              </motion.h2>
              <motion.p
                layout
                transition={{ type: "spring", stiffness: 300, damping: 30 }}
                className="text-sm text-[#8992A9]"
              >
                {isExpanded ? "Browse all file types" : "Click to explore all types"}
              </motion.p>
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation()
                toggleExpansion()
              }}
              className="p-2 hover:bg-gray-100 rounded-full transition-colors"
            >
              {isExpanded ? (
                <Minimize2 className="h-5 w-5 text-[#8992A9]" />
              ) : (
                <Expand className="h-5 w-5 text-[#8992A9]" />
              )}
            </button>
          </motion.div>

          {isExpanded ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3, ease: "easeInOut" }}
              className="h-full overflow-hidden"
            >
              <div
                ref={containerRef}
                className="flex h-full snap-x snap-mandatory overflow-x-auto pb-12 pt-4"
                style={{ scrollSnapType: "x mandatory", scrollbarWidth: "none", msOverflowStyle: "none" }}
                onScroll={handleScroll}
              >
                {categories.map((category, index) => (
                  <motion.div
                    key={category.name}
                    className="w-1/4 flex-shrink-0 snap-start px-2"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.05 }}
                  >
                    <Card className="group h-full cursor-pointer overflow-hidden bg-white p-4 text-[#1C1C1C] transition-all duration-500 hover:shadow-[0_8px_20px_rgba(0,0,0,0.1)] hover:translate-y-[-2px]">
                      <div className="flex h-full flex-col">
                        <div
                          className={`mb-3 flex h-10 w-10 items-center justify-center rounded-xl ${category.bgColor}`}
                        >
                          <category.icon className={`h-5 w-5 ${category.textColor}`} />
                        </div>
                        <h3 className="mb-2 text-base font-semibold">{category.name}</h3>
                        <p className="mb-4 text-sm text-gray-500">{category.description}</p>
                        <div className="mb-4 grid grid-cols-2 gap-2">
                          {category.types.map((type) => (
                            <div
                              key={type.name}
                              className="flex items-center gap-2 rounded-lg bg-gray-50 p-2 text-xs text-gray-600"
                            >
                              <type.icon className="h-4 w-4" />
                              <span>{type.name}</span>
                            </div>
                          ))}
                        </div>
                        <button
                          className="mt-auto rounded-full bg-gray-900 px-4 py-2 text-sm text-white transition-colors hover:bg-gray-800"
                          onClick={(e) => e.stopPropagation()}
                        >
                          View All
                        </button>
                      </div>
                    </Card>
                  </motion.div>
                ))}
              </div>

              {/* Dots navigation */}
              <div className="absolute bottom-4 left-0 flex w-full justify-center">
                {Array.from({ length: Math.ceil(categories.length / 4) }).map((_, index) => (
                  <button
                    key={index}
                    className={`mx-1 h-1.5 rounded-full transition-all ${
                      index === Math.floor(activeIndex / 4) ? "bg-black w-4" : "bg-gray-300 w-1.5"
                    }`}
                    onClick={(e) => {
                      e.stopPropagation()
                      if (containerRef.current) {
                        containerRef.current.scrollTo({
                          left: index * containerRef.current.offsetWidth,
                          behavior: "smooth",
                        })
                      }
                    }}
                  />
                ))}
              </div>
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3, ease: "easeInOut" }}
              className="grid h-full grid-cols-3 gap-2 overflow-hidden p-4"
            >
              {categories.slice(0, 9).map((category, index) => (
                <motion.div
                  key={category.name}
                  className="flex cursor-pointer flex-col items-center justify-center gap-2 rounded-lg p-2 text-center transition-colors hover:bg-black/5"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2, delay: index * 0.05 }}
                >
                  <div className={`flex h-12 w-12 items-center justify-center rounded-xl ${category.bgColor}`}>
                    <category.icon className={`h-6 w-6 ${category.textColor}`} />
                  </div>
                  <span className="text-xs font-medium text-[#1C1C1C]">{category.name}</span>
                </motion.div>
              ))}
              <motion.div
                className="col-span-3 flex items-center justify-center text-sm text-[#8992A9]"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
              >
                +{categories.length - 9} more types
              </motion.div>
            </motion.div>
          )}
        </motion.div>
      </AnimatePresence>
    </div>
  )
}




// src/components/library/type-categories.tsx

"use client"

import { useState } from "react"
import { motion } from "framer-motion"
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
} from "lucide-react"

const categories = [
  {
    name: "Documents",
    icon: FileText,
    iconColor: "text-gray-600",
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
    iconColor: "text-green-600",
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
    iconColor: "text-purple-600",
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
    iconColor: "text-amber-600",
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
    iconColor: "text-rose-600",
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
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null)

  return (
    <div className="w-full">
      <div className="flex items-center justify-between border-b border-[#dddddd] p-4">
        <div>
          <h2 className="text-lg font-medium text-[#1C1C1C]">Types</h2>
          <p className="text-sm text-[#8992A9]">Browse all file types</p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 p-4">
        {categories.map((category, index) => (
          <motion.div
            key={category.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.05 }}
            className="group relative"
            onHoverStart={() => setHoveredIndex(index)}
            onHoverEnd={() => setHoveredIndex(null)}
          >
            <div className="h-full cursor-pointer overflow-hidden rounded-lg border border-gray-200 bg-white p-4 transition-all duration-300 hover:shadow-md">
              <motion.div
                className="absolute inset-0 bg-gray-50 opacity-0 transition-opacity duration-300"
                animate={{ opacity: hoveredIndex === index ? 1 : 0 }}
              />
              <div className="relative z-10 flex h-full flex-col">
                <div className="mb-2 flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gray-100 shadow-sm">
                    <category.icon className={`h-5 w-5 ${category.iconColor}`} />
                  </div>
                  <span className="text-sm font-medium text-[#1c1c1c]">{category.name}</span>
                </div>
                <p className="mb-2 text-xs text-[#525766]">{category.description}</p>
                <div className="space-y-1">
                  {category.types.map((type) => (
                    <div key={type.name} className="flex items-center gap-2 text-xs text-[#525766]">
                      <type.icon className="h-3 w-3" />
                      <span>{type.name}</span>
                    </div>
                  ))}
                </div>
                <motion.div
                  className="mt-auto flex items-center justify-end"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: hoveredIndex === index ? 1 : 0, y: hoveredIndex === index ? 0 : 10 }}
                  transition={{ duration: 0.2 }}
                >
                  <button className="text-xs font-medium text-blue-600 hover:text-blue-800 transition-colors">
                    View All
                  </button>
                </motion.div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}





// src/components/library/type-categories.tsx

"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import Link from "next/link"
import {
  FileType,
  FileText,
  FileTextIcon as TextFile,
  Table2,
  FileSpreadsheet,
  FileInput,
  Image,
  Video,
  Music,
  Mail,
  MessageSquare,
  Phone,
  StickyNote,
  BookOpen,
  Paperclip,
  ArrowRight,
} from "lucide-react"

const categories = [
  {
    name: "Documents",
    types: [
      { name: "Word/Pages", icon: FileType },
      { name: "PDF", icon: FileText },
      { name: "Text Files", icon: TextFile },
    ],
  },
  {
    name: "Spreadsheets",
    types: [
      { name: "Excel/Numbers", icon: FileSpreadsheet },
      { name: "CSV", icon: Table2 },
      { name: "Google Sheets", icon: FileInput },
    ],
  },
  {
    name: "Media",
    types: [
      { name: "Images/Photos", icon: Image },
      { name: "Videos", icon: Video },
      { name: "Audio/Voice", icon: Music },
    ],
  },
  {
    name: "Comms",
    types: [
      { name: "Emails", icon: Mail },
      { name: "Chat Logs", icon: MessageSquare },
      { name: "Call Records", icon: Phone },
    ],
  },
  {
    name: "Notes",
    types: [
      { name: "Minutes", icon: BookOpen },
      { name: "Snippets", icon: Paperclip },
      { name: "Notes", icon: StickyNote },
    ],
  },
]

const getGradient = (index: number) => {
  const gradients = [
    "from-[#93c5fd]/20 to-[#bfdbfe]/20",
    "from-[#9fe870]/20 to-[#bfdbfe]/20",
    "from-[#bfdbfe]/20 to-[#93c5fd]/20",
    "from-[#9fe870]/20 to-[#93c5fd]/20",
    "from-[#93c5fd]/20 to-[#9fe870]/20",
  ]
  return gradients[index % gradients.length]
}

export function TypeCategories() {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null)

  return (
    <div className="w-full">
      <div className="mb-2">
        <h2 className="text-[10px] font-light tracking-[1px] text-[#1C1C1C]">FILE TYPES</h2>
      </div>
      <div className="grid grid-cols-5 gap-4">
        {categories.map((category, index) => (
          <Link href={`/library/${category.name.toLowerCase()}`} key={category.name}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.05 }}
              className="group relative"
              onHoverStart={() => setHoveredIndex(index)}
              onHoverEnd={() => setHoveredIndex(null)}
            >
              <div
                className={`h-full cursor-pointer overflow-hidden rounded-xl border border-white/20 bg-gradient-to-br ${getGradient(index)} p-2.5 transition-all duration-300 hover:shadow-lg`}
              >
                <motion.div
                  className="absolute inset-0 bg-white opacity-70 transition-opacity duration-300 rounded-xl"
                  animate={{ opacity: hoveredIndex === index ? 0.6 : 0.7 }}
                />
                <div className="relative z-10 flex h-full flex-col items-start">
                  <div className="mb-2">
                    <span className="text-sm font-medium text-black/80">{category.name}</span>
                  </div>
                  <div className="space-y-1.5 flex-grow text-left">
                    {category.types.map((type) => (
                      <div key={type.name} className="flex items-center gap-1.5 text-xs text-black/70">
                        <type.icon className="h-3 w-3" />
                        <span>{type.name}</span>
                      </div>
                    ))}
                  </div>
                  <motion.div
                    className="absolute bottom-2 right-2"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: hoveredIndex === index ? 1 : 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    <ArrowRight className="h-4 w-4 text-black/70" />
                  </motion.div>
                </div>
              </div>
            </motion.div>
          </Link>
        ))}
      </div>
    </div>
  )
}


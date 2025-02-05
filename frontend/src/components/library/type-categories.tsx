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
    "from-blue-400 via-purple-400 to-pink-400",
    "from-green-400 via-teal-400 to-blue-400",
    "from-yellow-400 via-orange-400 to-red-400",
    "from-pink-400 via-rose-400 to-indigo-400",
    "from-indigo-400 via-cyan-400 to-emerald-400",
  ]
  return gradients[index % gradients.length]
}

export function TypeCategories() {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null)

  return (
    <div className="w-full">
      <div className="grid grid-cols-5 gap-4 p-4">
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
                className={`h-full cursor-pointer overflow-hidden rounded-xl border border-white/20 bg-gradient-to-br ${getGradient(index)} p-6 transition-all duration-300 hover:shadow-lg`}
              >
                <motion.div
                  className="absolute inset-0 bg-white opacity-70 transition-opacity duration-300 rounded-xl"
                  animate={{ opacity: hoveredIndex === index ? 0.6 : 0.7 }}
                />
                <div className="relative z-10 flex h-full flex-col items-start">
                  <div className="mb-4">
                    <span className="text-base font-medium text-black">{category.name}</span>
                  </div>
                  <div className="space-y-2 flex-grow text-left">
                    {category.types.map((type) => (
                      <div key={type.name} className="flex items-center gap-2 text-sm text-black/70">
                        <type.icon className="h-4 w-4" />
                        <span>{type.name}</span>
                      </div>
                    ))}
                  </div>
                  <motion.div
                    className="mt-4 pt-2 border-t border-black/10"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: hoveredIndex === index ? 1 : 0, y: hoveredIndex === index ? 0 : 10 }}
                    transition={{ duration: 0.2 }}
                  >
                    <span className="text-sm font-medium text-black/90 hover:text-black transition-colors">
                      View All →
                    </span>
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





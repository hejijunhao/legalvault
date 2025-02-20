// src/components/library/quick-access.tsx

"use client"

import { motion } from "framer-motion"
import Link from "next/link"
import { Search, Bookmark, FolderOpen } from "lucide-react"
import React from "react"

const sections = [
  {
    id: "searches",
    title: "Past Searches",
    href: "/library/searches",
    icon: Search,
  },
  {
    id: "bookmarks",
    title: "Bookmarks",
    href: "/library/bookmarks",
    icon: Bookmark,
  },
  {
    id: "collections",
    title: "Collections",
    href: "/library/collections",
    icon: FolderOpen,
  },
]

export function QuickAccessSections() {
  return (
    <motion.div
      className="w-full max-w-[600px]"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="flex items-stretch rounded-lg bg-white/20 backdrop-blur-sm p-1 shadow-[0_2px_8px_rgba(0,0,0,0.03)] border border-white/20">
        {sections.map((section, index) => {
          const Icon = section.icon
          return (
            <React.Fragment key={section.id}>
              {index > 0 && <div className="w-px bg-gray-100" />}
              <Link href={section.href} className="flex-1">
                <motion.div
                  className="flex h-10 w-full items-center justify-center gap-2 rounded-md px-4 py-2 text-sm text-[#1C1C1C] transition-colors"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <Icon className="h-4 w-4" />
                  {section.title}
                </motion.div>
              </Link>
            </React.Fragment>
          )
        })}
      </div>
    </motion.div>
  )
}




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
      className="mx-auto max-w-2xl"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="flex items-stretch rounded-full bg-white p-1.5 shadow-[0_2px_12px_rgba(0,0,0,0.08)]">
        {sections.map((section, index) => {
          const Icon = section.icon
          return (
            <React.Fragment key={section.id}>
              {index > 0 && <div className="w-px bg-gray-200" />}
              <Link href={section.href} className="flex-1">
                <motion.button
                  className="flex h-12 w-full items-center justify-center gap-2 rounded-full px-6 py-3 text-sm text-gray-700 transition-colors hover:bg-gray-100"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <Icon className="h-5 w-5" />
                  {section.title}
                </motion.button>
              </Link>
            </React.Fragment>
          )
        })}
      </div>
    </motion.div>
  )
}


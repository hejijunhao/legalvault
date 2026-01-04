// src/components/research/bookmarks-block.tsx

"use client"

import { motion } from "framer-motion"
import { animations, withStaggerIndex } from "@/lib/animations"
import { Card } from "@/components/ui/card"
import { BookmarkIcon, SearchIcon } from "lucide-react"

const bookmarks = [
  {
    icon: BookmarkIcon,
    label: "Bookmarks",
    type: "bookmark",
  },
  {
    icon: SearchIcon,
    label: "Past Searches",
    type: "search",
  },
]

export function BookmarksBlock() {
  return (
    <div className="w-full mt-6">
      <div className="flex justify-between space-x-4">
        {bookmarks.map((bookmark, index) => (
          <motion.div
            key={bookmark.label}
            {...withStaggerIndex(animations.fadeInUp, index, 0.1)}
            className="group relative flex-1"
          >
            {/* Stacked cards effect */}
            <div className="absolute inset-0 translate-y-2 rounded-lg bg-gray-200 opacity-70" />
            <div className="absolute inset-0 translate-y-1 rounded-lg bg-gray-100 opacity-85" />

            {/* Main card */}
            <Card className="relative overflow-hidden rounded-lg border-white/20 bg-white shadow-md hover:shadow-lg transition-all duration-300">
              <div className="p-4">
                <h2 className="text-[10px] font-light tracking-[1px] text-[#1C1C1C] mb-2">
                  {bookmark.label.toUpperCase()}
                </h2>
                <div className="flex items-center gap-2">
                  <bookmark.icon className="h-4 w-4 text-gray-600" />
                  <span className="text-sm font-medium text-gray-800">No recent {bookmark.type}s</span>
                </div>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  )
}


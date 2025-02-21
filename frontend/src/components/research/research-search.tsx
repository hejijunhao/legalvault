// src/components/research/research-search.tsx

"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Search, Globe, Paperclip, ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"

interface ResearchSearchProps {
  query: string
  onQueryChange: (query: string) => void
}

export function ResearchSearch({ query, onQueryChange }: ResearchSearchProps) {
  const [mode, setMode] = useState("auto")

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="relative w-full"
    >
      <div className="relative flex items-center rounded-xl border border-gray-200 bg-white shadow-sm">
        <div className="flex h-14 items-center gap-2 border-r border-gray-100 px-4">
          <button
            onClick={() => setMode(mode === "auto" ? "manual" : "auto")}
            className="flex items-center gap-1.5 rounded-lg bg-gray-50 px-3 py-1.5 text-sm text-gray-700 transition-colors hover:bg-gray-100"
          >
            <Search className="h-4 w-4" />
            <span>{mode === "auto" ? "Auto" : "Manual"}</span>
          </button>
        </div>
        <input
          type="text"
          value={query}
          onChange={(e) => onQueryChange(e.target.value)}
          placeholder="Research legal precedents, analyze cases, or explore regulations..."
          className="flex-1 bg-transparent px-4 text-base text-gray-900 placeholder-gray-400 focus:outline-none"
        />
        <div className="flex items-center gap-2 px-4">
          <button className="rounded-lg p-2 text-gray-400 transition-colors hover:bg-gray-50 hover:text-gray-600">
            <Globe className="h-5 w-5" />
          </button>
          <button className="rounded-lg p-2 text-gray-400 transition-colors hover:bg-gray-50 hover:text-gray-600">
            <Paperclip className="h-5 w-5" />
          </button>
          <Button size="icon" className="h-9 w-9 rounded-lg bg-[#9FE870] text-[#09332B] hover:bg-[#9FE870]/90">
            <ArrowRight className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </motion.div>
  )
}


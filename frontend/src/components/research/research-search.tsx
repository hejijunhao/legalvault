// src/components/research/research-search.tsx

"use client"

import { useState, useRef, type ChangeEvent } from "react"
import { motion } from "framer-motion"
import { ArrowRight, Link2, Globe, Shuffle } from "lucide-react"

interface ResearchSearchProps {
  query: string
  onQueryChange: (value: string) => void
}

export function ResearchSearch({ query, onQueryChange }: ResearchSearchProps) {
  const [isFocused, setIsFocused] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleTextareaChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    onQueryChange(e.target.value)

    if (textareaRef.current) {
      textareaRef.current.style.height = "auto"
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="relative w-full"
    >
      <div
        className={`flex flex-col rounded-2xl border bg-white p-4 shadow-[0_0_10px_rgba(0,0,0,0.05)] transition-all ${
          isFocused ? "border-gray-300" : "border-gray-200"
        }`}
      >
        <textarea
          ref={textareaRef}
          value={query}
          onChange={handleTextareaChange}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder="Ask anything..."
          className="mb-3 w-full resize-none border-0 bg-transparent text-lg text-gray-900 placeholder:text-gray-500 focus:outline-none focus:ring-0"
          style={{ minHeight: "24px", maxHeight: "200px" }}
        />

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button className="flex items-center gap-2 rounded-full bg-gray-50 px-4 py-2 text-sm text-gray-600">
              <Shuffle className="h-4 w-4" />
              Auto
            </button>
            <button className="rounded-lg p-2 text-gray-400 hover:text-gray-600">
              <Globe className="h-5 w-5" />
            </button>
          </div>

          <div className="flex items-center gap-3">
            <button className="rounded-lg p-2 text-gray-400 hover:text-gray-600">
              <Link2 className="h-5 w-5" />
            </button>
            <button
              className={`rounded-full p-2 transition-colors ${
                query.trim() ? "bg-[#95C066] text-white" : "bg-gray-100 text-gray-400"
              }`}
            >
              <ArrowRight className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  )
}


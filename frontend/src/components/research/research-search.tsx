// src/components/research/research-search.tsx

"use client"

import { useState, useRef, type ChangeEvent, KeyboardEvent } from "react"
import { motion } from "framer-motion"
import { ArrowRight, Gavel, BookText, Building2, Loader2 } from "lucide-react"
import { QueryType } from "@/contexts/research/research-context"

interface ResearchSearchProps {
  query: string
  onQueryChange: (value: string) => void
  onSubmit?: (queryType: QueryType | null) => void
  isLoading?: boolean
}

export function ResearchSearch({ 
  query, 
  onQueryChange, 
  onSubmit, 
  isLoading = false 
}: ResearchSearchProps) {
  const [isFocused, setIsFocused] = useState(false)
  const [selectedType, setSelectedType] = useState<QueryType | null>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleTextareaChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    onQueryChange(e.target.value)

    if (textareaRef.current) {
      textareaRef.current.style.height = "auto"
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Submit on Enter key (without Shift)
    if (e.key === "Enter" && !e.shiftKey && query.trim() && query.trim().length >= 5) {
      e.preventDefault()
      onSubmit?.(selectedType)
    }
  }

  const toggleQueryType = (type: QueryType) => {
    setSelectedType(selectedType === type ? null : type)
  }

  const handleSubmit = () => {
    if (query.trim() && query.trim().length >= 5 && !isLoading && onSubmit) {
      onSubmit(selectedType)
    }
  }

  const isValidQuery = query.trim() && query.trim().length >= 5

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
          onKeyDown={handleKeyDown}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder="Ask anything..."
          className="mb-3 w-full resize-none border-0 bg-transparent text-lg text-gray-900 placeholder:text-gray-500 focus:outline-none focus:ring-0"
          style={{ minHeight: "24px", maxHeight: "200px" }}
        />

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {/* Courts Toggle */}
            <button
              onClick={() => toggleQueryType(QueryType.COURT_CASE)}
              className={`flex items-center gap-2 rounded-full px-3 py-1.5 text-sm transition-colors ${
                selectedType === QueryType.COURT_CASE
                  ? "bg-[#9FE870] text-[#1A2E0D]"
                  : "bg-gray-50 text-gray-600 hover:bg-gray-100"
              }`}
              aria-pressed={selectedType === QueryType.COURT_CASE}
              title="Search court cases and legal precedents"
            >
              <Gavel className="h-4 w-4" />
              <span>Courts</span>
            </button>

            {/* Legislative Toggle */}
            <button
              onClick={() => toggleQueryType(QueryType.LEGISLATIVE)}
              className={`flex items-center gap-2 rounded-full px-3 py-1.5 text-sm transition-colors ${
                selectedType === QueryType.LEGISLATIVE
                  ? "bg-[#9FE870] text-[#1A2E0D]"
                  : "bg-gray-50 text-gray-600 hover:bg-gray-100"
              }`}
              aria-pressed={selectedType === QueryType.LEGISLATIVE}
              title="Search legislation, statutes and regulations"
            >
              <BookText className="h-4 w-4" />
              <span>Legislative</span>
            </button>

            {/* Commercial Toggle */}
            <button
              onClick={() => toggleQueryType(QueryType.COMMERCIAL)}
              className={`flex items-center gap-2 rounded-full px-3 py-1.5 text-sm transition-colors ${
                selectedType === QueryType.COMMERCIAL
                  ? "bg-[#9FE870] text-[#1A2E0D]"
                  : "bg-gray-50 text-gray-600 hover:bg-gray-100"
              }`}
              aria-pressed={selectedType === QueryType.COMMERCIAL}
              title="Search commercial law and business regulations"
            >
              <Building2 className="h-4 w-4" />
              <span>Commercial</span>
            </button>
          </div>

          <div className="flex items-center">
            <button
              onClick={handleSubmit}
              disabled={!isValidQuery || isLoading}
              className={`rounded-full p-2 transition-colors ${
                isValidQuery && !isLoading
                  ? "bg-[#9FE870] text-[#1A2E0D] hover:bg-[#8ad460] cursor-pointer"
                  : "bg-gray-100 text-gray-400 cursor-not-allowed"
              }`}
              aria-label="Search for legal insights"
            >
              {isLoading ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <ArrowRight className="h-5 w-5" />
              )}
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

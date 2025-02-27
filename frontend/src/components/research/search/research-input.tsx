// src/components/research/search/research-input.tsx

"use client"

import type React from "react"

import { useState, useRef, type ChangeEvent } from "react"
import { motion } from "framer-motion"
import { ArrowRight } from "lucide-react"

export function ResearchInput() {
  const [input, setInput] = useState("")
  const [isFocused, setIsFocused] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleTextareaChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value)

    if (textareaRef.current) {
      textareaRef.current.style.height = "auto"
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    console.log("Submitted:", input)
    setInput("")
  }

  return (
    <form onSubmit={handleSubmit} className="fixed bottom-8 left-0 right-0 z-50">
      <div className="mx-auto max-w-[800px] px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="relative w-full"
        >
          <div
            className={`flex items-center rounded-2xl border bg-white p-4 shadow-[0_0_10px_rgba(0,0,0,0.05)] transition-all ${
              isFocused ? "border-gray-300" : "border-gray-200"
            }`}
          >
            <textarea
              ref={textareaRef}
              value={input}
              onChange={handleTextareaChange}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              placeholder="Ask anything..."
              className="flex-1 resize-none border-0 bg-transparent text-sm text-gray-900 placeholder:text-gray-500 focus:outline-none focus:ring-0"
              style={{ minHeight: "24px", maxHeight: "200px" }}
            />
            <button
              type="submit"
              className={`ml-4 rounded-full p-2 transition-colors ${
                input.trim() ? "bg-[#9FE870] text-white" : "bg-gray-100 text-gray-400"
              }`}
            >
              <ArrowRight className="h-5 w-5" />
            </button>
          </div>
        </motion.div>
      </div>
    </form>
  )
}


// src/components/library/search/follow-up-search.tsx

"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Send } from "lucide-react"

export function FollowUpSearch() {
  const [query, setQuery] = useState("")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Handle the search query submission here
    console.log("Submitted query:", query)
    setQuery("")
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="fixed bottom-8 left-0 right-0 z-50"
    >
      <form onSubmit={handleSubmit} className="mx-auto max-w-2xl px-4">
        <div className="relative">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Type a message..."
            className="w-full rounded-full border-none bg-white py-3 pl-6 pr-12 text-[#1c1c1c] shadow-[0_2px_12px_rgba(0,0,0,0.08)] placeholder:text-[#8992a9] focus:ring-1 focus:ring-[#4ade80] focus:ring-offset-0"
          />
          <button
            type="submit"
            className="absolute right-2 top-1/2 -translate-y-1/2 rounded-full bg-[#4ade80] p-2 text-white transition-colors hover:bg-[#4ade80]/90 focus:outline-none focus:ring-2 focus:ring-[#4ade80] focus:ring-offset-2"
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
      </form>
    </motion.div>
  )
}


// src/app/(app)/research/page.tsx

"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { ResearchSearch } from "@/components/research/research-search"
import { ResearchBanner } from "@/components/research/research-banner"
import { BookmarksBlock } from "@/components/research/bookmarks-block"

export default function ResearchPage() {
  const [query, setQuery] = useState("")

  return (
    <div className="flex min-h-[calc(100vh-4rem)] flex-col items-center justify-start px-4 py-16">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-3xl space-y-12"
      >
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="text-center text-[32px] font-normal italic leading-6 text-[#111827] font-['Libre_Baskerville']"
        >
          What legal insights do you need?
        </motion.h1>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="space-y-8"
        >
          <ResearchSearch query={query} onQueryChange={setQuery} />
          <BookmarksBlock />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <ResearchBanner />
        </motion.div>
      </motion.div>
    </div>
  )
}



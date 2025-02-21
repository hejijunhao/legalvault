// src/app/(app)/research/page.tsx

"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { ResearchSearch } from "@/components/research/research-search"
import { ResearchBanner } from "@/components/research/research-banner"
import { LegalNewsFeed } from "@/components/research/legal-news-feed"

export default function ResearchPage() {
  const [query, setQuery] = useState("")

  return (
    <div className="flex min-h-[calc(100vh-4rem)] flex-col items-center justify-start px-4 pt-16">
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
          className="text-center text-4xl font-medium text-[#1C1C1C]"
        >
          What legal insights do you need?
        </motion.h1>

        <ResearchSearch query={query} onQueryChange={setQuery} />
        <ResearchBanner />
        <LegalNewsFeed />
      </motion.div>
    </div>
  )
}





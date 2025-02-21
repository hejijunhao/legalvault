// src/components/research/research-banner.tsx

"use client"

import { motion } from "framer-motion"
import { Sparkles } from "lucide-react"

export function ResearchBanner() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.3 }}
      className="relative overflow-hidden rounded-xl bg-gradient-to-r from-[#93C5FD]/20 to-[#BFDBFE]/20 p-4"
    >
      {/* Background pattern */}
      <div className="absolute right-0 top-0 h-32 w-32 opacity-10">
        <div className="absolute right-0 top-0 h-full w-full rotate-45 bg-gradient-to-r from-white/0 to-white/50" />
      </div>

      <div className="flex items-start gap-3">
        <div className="rounded-lg bg-white/80 p-2">
          <Sparkles className="h-5 w-5 text-blue-500" />
        </div>
        <div className="flex-1">
          <h3 className="text-sm font-medium text-gray-900">Introducing Deep Legal Research</h3>
          <p className="mt-1 text-sm text-gray-600">
            The most powerful way to conduct comprehensive legal research and analysis across multiple jurisdictions and
            sources.
          </p>
        </div>
      </div>
    </motion.div>
  )
}


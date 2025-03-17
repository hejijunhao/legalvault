// src/components/research/past-searches-grid.tsx

"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { ArrowUpRight, BookmarkIcon } from "lucide-react"
import { useRouter } from "next/navigation"
import { ResearchSession } from "@/contexts/research/research-context"

export function PastSearchesGrid() {
  // For now, just use an empty array since the API integration isn't complete
  const [pastSearches] = useState<ResearchSession[]>([])
  const router = useRouter()

  const handleSearchClick = (id: string) => {
    router.push(`/research/${id}`)
  }

  // If there are no past searches, render nothing
  if (pastSearches.length === 0) {
    return null
  }

  return (
    <div className="mt-8 w-full">
      <h2 className="mb-4 text-sm font-medium text-gray-700">Recent Searches</h2>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
        {pastSearches.map((search, index) => (
          <motion.div
            key={search.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
            className="group relative cursor-pointer"
            onClick={() => handleSearchClick(search.id)}
          >
            <div className="overflow-hidden rounded-lg border border-gray-200 bg-white p-4 shadow-sm transition-all duration-300 hover:border-gray-300 hover:shadow-md">
              <div className="mb-2 flex items-center justify-between">
                <span className="text-xs text-gray-500">
                  {new Date(search.created_at).toLocaleDateString()}
                </span>
                {search.is_featured && (
                  <BookmarkIcon className="h-4 w-4 text-[#95C066]" />
                )}
              </div>
              <p className="mb-3 line-clamp-2 text-sm text-gray-800">{search.query}</p>
              <div className="flex items-center justify-end">
                <div className="rounded-full bg-gray-50 p-1.5 transition-colors group-hover:bg-[#95C066] group-hover:text-white">
                  <ArrowUpRight className="h-3.5 w-3.5" />
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
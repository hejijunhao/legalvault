// src/components/research/past-searches-grid.tsx

"use client"

import { useEffect, useRef, useState } from "react"
import { motion } from "framer-motion"
import { ArrowUpRight, BookmarkIcon, Loader2 } from "lucide-react"
import { useRouter } from "next/navigation"
import { ResearchSession, useResearch } from "@/contexts/research/research-context"

const ITEMS_PER_PAGE = 12

export function PastSearchesGrid() {
  const router = useRouter()
  const { getSessions, sessions, loadingStates, error, totalSessions } = useResearch()
  const [offset, setOffset] = useState(0)
  const [hasMore, setHasMore] = useState(true)
  const observerTarget = useRef<HTMLDivElement>(null)
  const isInitialMount = useRef(true)

  // Combined effect for initial fetch and infinite scroll
  useEffect(() => {
    // Only fetch on initial mount
    if (isInitialMount.current) {
      getSessions({ limit: ITEMS_PER_PAGE, offset: 0, skipAuthCheck: true })
      isInitialMount.current = false
      return
    }

    // Update hasMore whenever sessions or totalSessions change
    setHasMore(sessions.length < totalSessions)

    // Set up intersection observer for infinite scroll
    const observer = new IntersectionObserver(
      (entries) => {
        // If the target is visible and we have more items to load
        if (entries[0].isIntersecting && 
            sessions.length < totalSessions && 
            !loadingStates.fetchingSessions) {
          const newOffset = sessions.length // Use sessions.length instead of offset state
          getSessions({ 
            limit: ITEMS_PER_PAGE, 
            offset: newOffset,
            append: true,
            skipAuthCheck: true
          })
        }
      },
      { threshold: 0.1 }
    )

    if (observerTarget.current) {
      observer.observe(observerTarget.current)
    }

    return () => observer.disconnect()
  }, [getSessions, sessions.length, totalSessions, loadingStates.fetchingSessions])

  const handleSearchClick = (id: string) => {
    router.push(`/research/${id}`)
  }

  // Show error state if there's an error
  if (error) {
    return (
      <div className="mt-8 w-full">
        <p className="text-sm text-red-600">
          Error loading searches: {error.message}
        </p>
      </div>
    )
  }

  // If there are no past searches and we're not loading, render nothing
  if (!sessions?.length && !loadingStates.fetchingSessions) {
    return null
  }

  return (
    <div className="mt-8 w-full">
      <h2 className="mb-4 text-sm font-medium text-gray-700">Recent Searches</h2>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
        {sessions.map((search, index) => (
          <motion.div
            key={search.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
            className="group relative cursor-pointer"
            onClick={() => handleSearchClick(search.id)}
          >
            <div className="overflow-hidden rounded-lg border border-gray-200 bg-white p-4 shadow-sm transition-all duration-300 hover:border-gray-300 hover:shadow-md h-[160px] flex flex-col justify-between">
              <div>
                <div className="mb-2 flex items-center justify-between">
                  <span className="text-xs text-gray-500">
                    {new Date(search.created_at).toLocaleDateString()}
                  </span>
                  {search.is_featured && (
                    <BookmarkIcon className="h-4 w-4 text-[#95C066]" />
                  )}
                </div>
                <p className="mb-3 line-clamp-2 text-sm text-gray-800">{search.query}</p>
              </div>
              <div className="flex items-center justify-end">
                <div className="rounded-full bg-gray-50 p-1.5 transition-colors group-hover:bg-[#9FE870] group-hover:text-white">
                  <ArrowUpRight className="h-3.5 w-3.5" />
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Loading indicator and observer target */}
      <div 
        ref={observerTarget} 
        className="mt-8 w-full flex justify-center"
      >
        {loadingStates.fetchingSessions && (
          <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
        )}
      </div>
    </div>
  )
}
// src/components/research/past-searches-grid.tsx

"use client"

import { useEffect, useRef, useState } from "react"
import { motion } from "framer-motion"
import { ArrowUpRight, BookmarkIcon, Loader2 } from "lucide-react"
import { useRouter } from "next/navigation"
import { ResearchSession, useResearch } from "@/contexts/research/research-context"

const ITEMS_PER_PAGE = 12

// Gradient patterns for cards
const gradientPatterns = [
  'before:bg-[radial-gradient(circle_at_70%_20%,#f5f9ff_0%,rgba(255,255,255,0)_50%)] before:opacity-50',
  'before:bg-[radial-gradient(circle_at_30%_80%,#f0fff4_0%,rgba(255,255,255,0)_50%)] before:opacity-50',
  'before:bg-[radial-gradient(circle_at_80%_50%,#fff5f5_0%,rgba(255,255,255,0)_50%)] before:opacity-50',
  'before:bg-[radial-gradient(circle_at_20%_60%,#f5f0ff_0%,rgba(255,255,255,0)_50%)] before:opacity-50'
]

// Abstract shape component
const AbstractShape = ({ index }: { index: number }) => {
  const patterns = [
    'M 0 0 C 50 0 50 100 100 100',
    'M 100 0 C 50 0 50 100 0 100',
    'M 0 50 C 25 0 75 100 100 50',
    'M 50 0 C 100 25 0 75 50 100'
  ]

  return (
    <div className="absolute inset-0 overflow-hidden opacity-[0.07]">
      <svg
        viewBox="0 0 100 100"
        preserveAspectRatio="none"
        className="h-full w-full"
        fill="none"
        stroke="currentColor"
        strokeWidth="1"
      >
        <path d={patterns[index % patterns.length]} />
      </svg>
    </div>
  )
}

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
      <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 md:grid-cols-3">
        {sessions.map((search, index) => (
          <motion.div
            key={search.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
            className="group relative cursor-pointer h-[200px]"
            onClick={() => handleSearchClick(search.id)}
          >
            {/* Background message cards */}
            <div className="absolute right-2 top-4 z-[1] h-[85%] w-[92%] -rotate-3 rounded-lg border border-gray-100 bg-white/90 shadow-sm transition-all duration-300 group-hover:-translate-y-1" />
            <div className="absolute right-4 top-6 z-[0] h-[85%] w-[92%] rotate-3 rounded-lg border border-gray-50 bg-white/80 shadow-sm transition-all duration-300 group-hover:-translate-y-2" />
            
            {/* Main cover card */}
            <div className={`relative z-[2] h-full w-full overflow-hidden rounded-lg border border-gray-200 bg-white p-5 shadow transition-all duration-300 hover:border-gray-300 hover:shadow-md before:absolute before:inset-0 before:content-[''] ${gradientPatterns[index % gradientPatterns.length]}`}>
              <AbstractShape index={index} />
              <div className="relative z-[1] flex h-full flex-col">
                {/* Header */}
                <div className="mb-3 flex items-center justify-between">
                  <span className="text-xs text-gray-500">
                    {new Date(search.created_at).toLocaleDateString()}
                  </span>
                  {search.is_featured && (
                    <BookmarkIcon className="h-4 w-4 text-[#95C066]" />
                  )}
                </div>
                
                {/* Content */}
                <div className="flex-grow">
                  <p className="line-clamp-3 text-sm font-medium text-gray-800">{search.query}</p>
                </div>
                
                {/* Footer */}
                <div className="mt-auto flex items-center justify-end pt-3">
                  <motion.div 
                    className="rounded-full bg-gray-50 p-2 transition-colors group-hover:bg-[#9FE870] group-hover:text-white"
                    whileHover={{ scale: 1.1 }}
                    transition={{ type: "spring", stiffness: 400, damping: 10 }}
                  >
                    <ArrowUpRight className="h-4 w-4" />
                  </motion.div>
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
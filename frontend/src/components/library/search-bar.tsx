// src/components/library/search-bar.tsx

"use client"

import { useState, useEffect, useRef } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Users, FolderDot, BookCopy, FileType, Database, Calendar } from "lucide-react"
import { useOnClickOutside } from "@/hooks/library/use-on-click-outside"
import type React from "react" // Added import for React

interface Filter {
  id: string
  label: string
  icon: React.ComponentType<{ className?: string }>
}

const filters: Filter[] = [
  { id: "clients", label: "Clients", icon: Users },
  { id: "collections", label: "Collections", icon: FolderDot },
  { id: "cases", label: "Cases/Deals", icon: BookCopy },
  { id: "types", label: "Types", icon: FileType },
  { id: "sources", label: "Sources", icon: Database },
  { id: "timeframe", label: "Timeframe", icon: Calendar },
]

export function SearchBar() {
  const [value, setValue] = useState("")
  const [isFocused, setIsFocused] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)

  // Handle click outside to close filters
  useOnClickOutside(containerRef, () => setIsFocused(false))

  // Handle escape key to close filters
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setIsFocused(false)
      }
    }

    document.addEventListener("keydown", handleEscape)
    return () => document.removeEventListener("keydown", handleEscape)
  }, [])

  return (
    <div ref={containerRef} className="w-full">
      <div className="border-b border-[#8992A9]/20">
        <div className="mx-auto max-w-[1440px] px-4">
          <div className="relative w-full">
            <input
              type="text"
              placeholder="I'm looking for..."
              value={value}
              onChange={(e) => setValue(e.target.value)}
              onFocus={() => setIsFocused(true)}
              className={`
                font-['Libre_Baskerville'] 
                w-full max-w-[467.118px] h-[44px] 
                flex flex-col justify-center flex-shrink-0
                bg-transparent 
                text-[32px] font-normal italic leading-[24px]
                ${value ? "text-[#1C1C1C]" : "text-[#8992A9]/60"}
                placeholder:text-[#8992A9]/60 
                placeholder:italic
                focus:outline-none
                transition-colors
                duration-200
              `}
            />
          </div>
        </div>
      </div>

      {/* Filters */}
      <AnimatePresence>
        {isFocused && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2, ease: "easeInOut" }}
            className="overflow-hidden border-b border-[#8992A9]/10"
          >
            <div className="mx-auto max-w-[1440px] px-4 py-4">
              <motion.div
                initial={{ y: -10 }}
                animate={{ y: 0 }}
                transition={{ duration: 0.2, ease: "easeOut" }}
                className="flex flex-wrap gap-2"
              >
                {filters.map((filter, index) => (
                  <motion.button
                    key={filter.id}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{
                      duration: 0.15,
                      delay: index * 0.05,
                      ease: "easeOut",
                    }}
                    className="flex items-center gap-2 rounded-lg border border-white/20 bg-white/10 px-4 py-2 text-sm text-[#1C1C1C] backdrop-blur-md transition-all hover:bg-white/20"
                    onClick={(e) => e.preventDefault()} // Prevent closing on filter click
                  >
                    <filter.icon className="h-4 w-4" />
                    {filter.label}
                  </motion.button>
                ))}
              </motion.div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}


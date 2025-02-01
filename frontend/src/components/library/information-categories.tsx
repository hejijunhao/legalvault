// src/components/library/information-categories.tsx

"use client"

import { useRef, useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Card } from "@/components/ui/card"
import {
  FileText,
  FileSignature,
  FileCheck,
  Scale,
  Handshake,
  Gavel,
  Building2,
  FileSpreadsheet,
  Users,
  Search,
  FileStack,
  Send,
  Expand,
  Minimize2,
} from "lucide-react"

const categories = [
  {
    name: "Contracts",
    icon: FileText,
    bgColor: "bg-blue-50",
    textColor: "text-blue-500",
    description: "Manage and track legal agreements.",
  },
  {
    name: "Agreements",
    icon: FileSignature,
    bgColor: "bg-green-50",
    textColor: "text-green-500",
    description: "Service and partnership documents.",
  },
  {
    name: "NDAs",
    icon: FileCheck,
    bgColor: "bg-amber-50",
    textColor: "text-amber-500",
    description: "Confidentiality agreements.",
  },
  {
    name: "Legal Claims",
    icon: Scale,
    bgColor: "bg-red-50",
    textColor: "text-red-500",
    description: "Track and manage legal proceedings.",
  },
  {
    name: "Settlements",
    icon: Handshake,
    bgColor: "bg-purple-50",
    textColor: "text-purple-500",
    description: "Resolution and settlement docs.",
  },
  {
    name: "Court Filings",
    icon: Gavel,
    bgColor: "bg-indigo-50",
    textColor: "text-indigo-500",
    description: "Legal documentation and records.",
  },
  {
    name: "Company Docs",
    icon: Building2,
    bgColor: "bg-pink-50",
    textColor: "text-pink-500",
    description: "Company related documents",
  },
  {
    name: "Resolutions",
    icon: FileSpreadsheet,
    bgColor: "bg-teal-50",
    textColor: "text-teal-500",
    description: "Meeting resolutions and decisions",
  },
  {
    name: "Board Minutes",
    icon: Users,
    bgColor: "bg-orange-50",
    textColor: "text-orange-500",
    description: "Records of board meetings",
  },
  {
    name: "Due Diligence",
    icon: Search,
    bgColor: "bg-cyan-50",
    textColor: "text-cyan-500",
    description: "Information gathering and verification",
  },
  {
    name: "Offers",
    icon: FileStack,
    bgColor: "bg-lime-50",
    textColor: "text-lime-500",
    description: "Proposals and offers",
  },
  {
    name: "Term Sheets",
    icon: Send,
    bgColor: "bg-violet-50",
    textColor: "text-violet-500",
    description: "Preliminary agreements",
  },
]

export function InformationCategories() {
  const [isExpanded, setIsExpanded] = useState(false)
  const [activeIndex, setActiveIndex] = useState(0)
  const toggleExpansion = () => setIsExpanded(!isExpanded)
  const containerRef = useRef<HTMLDivElement>(null)

  const handleScroll = () => {
    if (containerRef.current && isExpanded) {
      const scrollPosition = containerRef.current.scrollLeft
      const cardWidth = containerRef.current.offsetWidth / 4
      const newActiveIndex = Math.round(scrollPosition / cardWidth)
      setActiveIndex(newActiveIndex)
    }
  }

  return (
    <div className="relative mt-8">
      <AnimatePresence>
        <motion.div
          layout
          initial={false}
          animate={{
            width: isExpanded ? "100%" : "380px",
            transition: { type: "spring", stiffness: 300, damping: 30 },
          }}
          className={`relative overflow-hidden rounded-xl border border-white/20 bg-white/90 backdrop-blur-md transition-all duration-500 ${
            isExpanded ? "max-w-[calc(1440px-380px-1.5rem-2rem)]" : ""
          }`}
        >
          {/* Header */}
          <motion.div
            layout
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
            className="flex items-center justify-between border-b border-white/10 p-4"
          >
            <div>
              <motion.h2
                layout
                transition={{ type: "spring", stiffness: 300, damping: 30 }}
                className="text-lg font-medium text-[#1C1C1C]"
              >
                Information Categories
              </motion.h2>
              <motion.p
                layout
                transition={{ type: "spring", stiffness: 300, damping: 30 }}
                className="text-sm text-[#8992A9]"
              >
                {isExpanded ? "Browse all categories" : "Click to explore all categories"}
              </motion.p>
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation()
                toggleExpansion()
              }}
              className="p-2 hover:bg-gray-100 rounded-full transition-colors"
            >
              {isExpanded ? (
                <Minimize2 className="h-5 w-5 text-[#8992A9]" />
              ) : (
                <Expand className="h-5 w-5 text-[#8992A9]" />
              )}
            </button>
          </motion.div>

          {isExpanded ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3, ease: "easeInOut" }}
              className="h-full overflow-hidden"
            >
              <div
                ref={containerRef}
                className="flex h-full snap-x snap-mandatory overflow-x-auto pb-12 pt-4"
                style={{ scrollSnapType: "x mandatory", scrollbarWidth: "none", msOverflowStyle: "none" }}
                onScroll={handleScroll}
              >
                {categories.map((category, index) => (
                  <motion.div
                    key={category.name}
                    className="w-1/4 flex-shrink-0 snap-start px-2"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.05 }}
                  >
                    <Card className="group h-full cursor-pointer overflow-hidden bg-white p-4 text-[#1C1C1C] transition-all duration-500 hover:shadow-[0_8px_20px_rgba(0,0,0,0.1)] hover:translate-y-[-2px]">
                      <div className="flex h-full flex-col">
                        <div
                          className={`mb-3 flex h-10 w-10 items-center justify-center rounded-xl ${category.bgColor}`}
                        >
                          <category.icon className={`h-5 w-5 ${category.textColor}`} />
                        </div>
                        <h3 className="mb-2 text-base font-semibold">{category.name}</h3>
                        <p className="mb-4 text-sm text-gray-500">{category.description}</p>
                        <button
                          className="mt-auto rounded-full bg-gray-900 px-4 py-2 text-sm text-white transition-colors hover:bg-gray-800"
                          onClick={(e) => e.stopPropagation()}
                        >
                          View All
                        </button>
                      </div>
                    </Card>
                  </motion.div>
                ))}
              </div>

              {/* Dots navigation */}
              <div className="absolute bottom-4 left-0 flex w-full justify-center">
                {Array.from({ length: Math.ceil(categories.length / 4) }).map((_, index) => (
                  <button
                    key={index}
                    className={`mx-1 h-1.5 rounded-full transition-all ${
                      index === Math.floor(activeIndex / 4) ? "bg-black w-4" : "bg-gray-300 w-1.5"
                    }`}
                    onClick={(e) => {
                      e.stopPropagation()
                      if (containerRef.current) {
                        containerRef.current.scrollTo({
                          left: index * containerRef.current.offsetWidth,
                          behavior: "smooth",
                        })
                      }
                    }}
                  />
                ))}
              </div>
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3, ease: "easeInOut" }}
              className="grid h-full grid-cols-3 gap-2 overflow-hidden p-4"
            >
              {categories.slice(0, 9).map((category, index) => (
                <motion.div
                  key={category.name}
                  className="flex cursor-pointer flex-col items-center justify-center gap-2 rounded-lg p-2 text-center transition-colors hover:bg-black/5"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2, delay: index * 0.05 }}
                >
                  <div className={`flex h-12 w-12 items-center justify-center rounded-xl ${category.bgColor}`}>
                    <category.icon className={`h-6 w-6 ${category.textColor}`} />
                  </div>
                  <span className="text-xs font-medium text-[#1C1C1C]">{category.name}</span>
                </motion.div>
              ))}
              <motion.div
                className="col-span-3 flex items-center justify-center text-sm text-[#8992A9]"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
              >
                +{categories.length - 9} more categories
              </motion.div>
            </motion.div>
          )}
        </motion.div>
      </AnimatePresence>
    </div>
  )
}





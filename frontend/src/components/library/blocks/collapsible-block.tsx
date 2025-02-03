// src/components/library/blocks/collapsible-block.tsx

"use client"

import { useState } from "react"
import { ChevronRight, ArrowRight } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import { Card } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import Link from "next/link"
import { Button } from "@/components/ui/button"

interface BlockItem {
  id: string
  name: string
  icon: string
  secondaryText?: string
}

interface CollapsibleBlockProps {
  title: string
  items: BlockItem[]
  iconUrls: string[]
  viewAllLink?: string
}

export function CollapsibleBlock({ title, items, iconUrls, viewAllLink }: CollapsibleBlockProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  // Ensure we always have 3 icons
  const displayIcons = [...iconUrls.slice(0, 3), ...Array(3).fill("/placeholder.svg?height=24&width=24")].slice(0, 3)

  return (
    <motion.div layout className="w-[380px]">
      <Card
        className={cn(
          "cursor-pointer border-white/20 bg-white/90 backdrop-blur-md transition-all duration-500",
          "hover:border-white/30 hover:bg-white/95",
          "shadow-[0_4px_20px_-4px_rgba(0,0,0,0.1)]",
          "hover:shadow-[0_8px_30px_-4px_rgba(0,0,0,0.2)]",
          isExpanded ? "rounded-xl" : "rounded-lg",
        )}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <motion.div layout="position" className="p-4">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              {/* Standardized 3 Icons */}
              <div className="flex -space-x-2">
                {displayIcons.map((icon, index) => (
                  <motion.div
                    key={index}
                    className="flex h-7 w-7 items-center justify-center rounded-full bg-[#F3F4F6] ring-2 ring-white"
                    initial={false}
                    animate={{
                      scale: isExpanded ? 0.9 : 1,
                      translateX: isExpanded ? `-${index * 4}px` : 0,
                    }}
                    transition={{ duration: 0.5, ease: "easeInOut" }}
                  >
                    <img src={icon || "/placeholder.svg"} alt="" className="h-4 w-4" />
                  </motion.div>
                ))}
              </div>
              {/* Title and Count */}
              <div>
                <h3 className="text-sm font-medium text-[#1C1C1C]">{title}</h3>
                <p className="text-xs text-[#8992A9]">{items.length} items</p>
              </div>
            </div>
            <motion.div animate={{ rotate: isExpanded ? 90 : 0 }} transition={{ duration: 0.5, ease: "easeInOut" }}>
              <ChevronRight className="h-4 w-4 text-[#525766]" />
            </motion.div>
          </div>

          {/* Expanded Content */}
          <AnimatePresence>
            {isExpanded && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.5, ease: "easeInOut" }}
                className="overflow-hidden"
              >
                <motion.div
                  className="mt-4 space-y-1"
                  initial={{ y: -20 }}
                  animate={{ y: 0 }}
                  transition={{ duration: 0.5, ease: "easeOut" }}
                >
                  {items.map((item, index) => (
                    <motion.div
                      key={item.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1, duration: 0.5 }}
                      className="group flex items-center justify-between rounded-lg p-3 transition-all duration-300 hover:bg-white"
                    >
                      <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-[#F3F4F6] transition-all duration-300 group-hover:bg-[#E5E7EB]">
                          <img src={item.icon || "/placeholder.svg"} alt="" className="h-5 w-5" />
                        </div>
                        <div>
                          <p className="text-sm font-medium text-[#1C1C1C]">{item.name}</p>
                          {item.secondaryText && <p className="text-xs text-[#8992A9]">{item.secondaryText}</p>}
                        </div>
                      </div>
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: index * 0.1 + 0.3 }}
                      >
                        <ChevronRight className="h-4 w-4 text-[#525766] opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
                      </motion.div>
                    </motion.div>
                  ))}
                </motion.div>
                {viewAllLink && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: items.length * 0.1 + 0.3, duration: 0.3 }}
                    className="mt-4 text-center"
                  >
                    <Link href={viewAllLink} className="inline-block w-full">
                      <Button
                        variant="ghost"
                        className="w-full rounded-lg bg-[#F3F4F6] py-2 text-[#1C1C1C] transition-all duration-300 hover:bg-[#E5E7EB]"
                      >
                        View Collections
                        <ArrowRight className="ml-2 h-4 w-4 opacity-50" />
                      </Button>
                    </Link>
                  </motion.div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </Card>
    </motion.div>
  )
}



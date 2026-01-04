// src/components/ui/expandable-block.tsx
// Generic expandable block component for card-based expand/collapse UI

"use client"

import { useState, ReactNode } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ChevronRight, ChevronDown, ChevronUp, ArrowRight } from "lucide-react"
import Link from "next/link"
import { cn } from "@/lib/utils"
import { animations } from "@/lib/animations"

export interface ExpandableBlockProps {
  /** Block title */
  title: string
  /** Optional subtitle/description */
  subtitle?: string
  /** Optional icon element for the header */
  icon?: ReactNode
  /** Optional badge content (e.g., item count) */
  badge?: string | number
  /** Content shown when collapsed (preview) */
  children?: ReactNode
  /** Content shown when expanded */
  expandedContent?: ReactNode
  /** Whether to start expanded */
  defaultExpanded?: boolean
  /** Link for "View All" button */
  viewAllLink?: string
  /** Text for "View All" button */
  viewAllText?: string
  /** Visual variant */
  variant?: "default" | "compact" | "featured"
  /** Fixed width (default: auto) */
  width?: string | number
  /** Additional className */
  className?: string
  /** Callback when expand state changes */
  onExpandChange?: (expanded: boolean) => void
}

export function ExpandableBlock({
  title,
  subtitle,
  icon,
  badge,
  children,
  expandedContent,
  defaultExpanded = false,
  viewAllLink,
  viewAllText = "View All",
  variant = "default",
  width,
  className,
  onExpandChange,
}: ExpandableBlockProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded)

  const handleToggle = () => {
    const newState = !isExpanded
    setIsExpanded(newState)
    onExpandChange?.(newState)
  }

  const widthStyle = width ? (typeof width === "number" ? `${width}px` : width) : undefined

  return (
    <motion.div layout style={{ width: widthStyle }}>
      <Card
        className={cn(
          "cursor-pointer border-white/20 bg-white/90 backdrop-blur-md transition-all duration-300",
          "hover:border-white/30 hover:bg-white/95",
          "shadow-[0_4px_20px_-4px_rgba(0,0,0,0.1)]",
          "hover:shadow-[0_8px_30px_-4px_rgba(0,0,0,0.2)]",
          isExpanded ? "rounded-xl" : "rounded-lg",
          variant === "featured" && "border-primary/30",
          variant === "compact" && "p-2",
          className
        )}
        onClick={handleToggle}
      >
        <motion.div layout="position" className={cn("p-4", variant === "compact" && "p-3")}>
          {/* Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {icon && (
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-[#F3F4F6]">
                  {icon}
                </div>
              )}
              <div>
                <h3 className="text-sm font-medium text-[#1C1C1C]">{title}</h3>
                {subtitle && <p className="text-xs text-[#8992A9]">{subtitle}</p>}
              </div>
            </div>
            <div className="flex items-center gap-2">
              {badge !== undefined && (
                <span className="px-2 py-1 text-xs bg-[#F3F4F6] rounded-full text-[#525766]">
                  {badge}
                </span>
              )}
              <motion.div
                animate={{ rotate: isExpanded ? 90 : 0 }}
                transition={{ duration: 0.3 }}
              >
                <ChevronRight className="h-4 w-4 text-[#525766]" />
              </motion.div>
            </div>
          </div>

          {/* Always visible content (preview) */}
          {children && !isExpanded && (
            <div className="mt-3">{children}</div>
          )}

          {/* Expanded content */}
          <AnimatePresence>
            {isExpanded && expandedContent && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.3 }}
                className="overflow-hidden"
              >
                <motion.div
                  className="mt-4"
                  initial={{ y: -10 }}
                  animate={{ y: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  {expandedContent}
                </motion.div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* View All button */}
          {viewAllLink && isExpanded && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="mt-4"
              onClick={(e) => e.stopPropagation()}
            >
              <Link href={viewAllLink}>
                <Button
                  variant="ghost"
                  className="w-full rounded-lg bg-[#F3F4F6] py-2 text-[#1C1C1C] transition-all duration-300 hover:bg-[#E5E7EB]"
                >
                  {viewAllText}
                  <ArrowRight className="ml-2 h-4 w-4 opacity-50" />
                </Button>
              </Link>
            </motion.div>
          )}
        </motion.div>
      </Card>
    </motion.div>
  )
}

// Sub-components for common list patterns

export interface ExpandableBlockItemProps {
  /** Icon element */
  icon?: ReactNode
  /** Primary text */
  primary: string
  /** Secondary text */
  secondary?: string
  /** Click handler */
  onClick?: () => void
  /** Animation delay index for stagger effect */
  index?: number
}

export function ExpandableBlockItem({
  icon,
  primary,
  secondary,
  onClick,
  index = 0,
}: ExpandableBlockItemProps) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.1, duration: 0.3 }}
      className="group flex cursor-pointer items-center justify-between rounded-lg p-3 transition-all duration-300 hover:bg-white"
      onClick={(e) => {
        e.stopPropagation()
        onClick?.()
      }}
    >
      <div className="flex items-center gap-3">
        {icon && (
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-[#F3F4F6] transition-all duration-300 group-hover:bg-[#E5E7EB]">
            {icon}
          </div>
        )}
        <div>
          <p className="text-sm font-medium text-[#1C1C1C] line-clamp-1">{primary}</p>
          {secondary && <p className="text-xs text-[#8992A9]">{secondary}</p>}
        </div>
      </div>
      <ChevronRight className="h-4 w-4 text-[#525766] opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
    </motion.div>
  )
}

export interface ExpandableBlockListProps {
  children: ReactNode
  className?: string
}

export function ExpandableBlockList({ children, className }: ExpandableBlockListProps) {
  return <div className={cn("space-y-1", className)}>{children}</div>
}

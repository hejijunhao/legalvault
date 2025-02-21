// src/components/research/research-context.tsx

"use client"

import { motion } from "framer-motion"
import { Scale, BookOpen, Globe } from "lucide-react"

const contextItems = [
  {
    icon: Scale,
    title: "Singapore Legal Updates",
    subtitle: "Recent High Court Decision on Contract Law",
    date: "20 Feb 2024",
  },
  {
    icon: BookOpen,
    title: "Latest Amendments",
    subtitle: "Companies Act Amendments",
    date: "Effective 1 Mar 2024",
  },
  {
    icon: Globe,
    title: "International Developments",
    subtitle: "EU Data Protection Regulations",
    date: "Updated Guidelines",
  },
]

export function ResearchContext() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5, delay: 0.4 }}
      className="grid grid-cols-3 gap-4"
    >
      {contextItems.map((item, index) => {
        const Icon = item.icon
        return (
          <motion.div
            key={item.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 + index * 0.1 }}
            className="group flex cursor-pointer items-center gap-3 rounded-lg border border-gray-100 bg-white p-4 transition-all hover:border-gray-200 hover:shadow-sm"
          >
            <div className="rounded-lg bg-gray-50 p-2 transition-colors group-hover:bg-gray-100">
              <Icon className="h-5 w-5 text-gray-600" />
            </div>
            <div className="min-w-0 flex-1">
              <div className="truncate text-sm font-medium text-gray-900">{item.title}</div>
              <div className="mt-1 flex items-center gap-2">
                <span className="truncate text-xs text-gray-500">{item.subtitle}</span>
                <span className="text-xs font-medium text-gray-400">•</span>
                <span className="shrink-0 text-xs text-gray-400">{item.date}</span>
              </div>
            </div>
          </motion.div>
        )
      })}
    </motion.div>
  )
}


// src/components/library/information-categories.tsx

"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Card } from "@/components/ui/card"
import Link from "next/link"
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
} from "lucide-react"

const categories = [
  {
    name: "Contracts",
    icon: FileText,
    gradient: "from-blue-400 to-blue-600",
    description: "Manage and track legal agreements.",
  },
  {
    name: "Agreements",
    icon: FileSignature,
    gradient: "from-green-400 to-green-600",
    description: "Service and partnership documents.",
  },
  {
    name: "NDAs",
    icon: FileCheck,
    gradient: "from-yellow-400 to-yellow-600",
    description: "Confidentiality agreements.",
  },
  {
    name: "Legal Claims",
    icon: Scale,
    gradient: "from-red-400 to-red-600",
    description: "Track and manage legal proceedings.",
  },
  {
    name: "Settlements",
    icon: Handshake,
    gradient: "from-purple-400 to-purple-600",
    description: "Resolution and settlement docs.",
  },
  {
    name: "Court Filings",
    icon: Gavel,
    gradient: "from-indigo-400 to-indigo-600",
    description: "Legal documentation and records.",
  },
  {
    name: "Company Docs",
    icon: Building2,
    gradient: "from-pink-400 to-pink-600",
    description: "Company related documents",
  },
  {
    name: "Resolutions",
    icon: FileSpreadsheet,
    gradient: "from-teal-400 to-teal-600",
    description: "Meeting resolutions and decisions",
  },
  {
    name: "Board Minutes",
    icon: Users,
    gradient: "from-orange-400 to-orange-600",
    description: "Records of board meetings",
  },
  {
    name: "Due Diligence",
    icon: Search,
    gradient: "from-cyan-400 to-cyan-600",
    description: "Information gathering and verification",
  },
  {
    name: "Offers",
    icon: FileStack,
    gradient: "from-lime-400 to-lime-600",
    description: "Proposals and offers",
  },
  {
    name: "Term Sheets",
    icon: Send,
    gradient: "from-violet-400 to-violet-600",
    description: "Preliminary agreements",
  },
]

export function InformationCategories() {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null)

  return (
    <div className="relative w-full">
      <div className="flex items-center justify-between border-b border-[#dddddd] p-4">
        <h2 className="text-lg font-medium text-[#1c1c1c]">Categories</h2>
      </div>
      <div className="grid grid-cols-3 gap-4 p-4">
        {categories.map((category, index) => (
          <Link href={`/library/${category.name.toLowerCase().replace(/\s+/g, "-")}`} key={category.name}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.05 }}
              onHoverStart={() => setHoveredIndex(index)}
              onHoverEnd={() => setHoveredIndex(null)}
            >
              <Card className="group relative h-full cursor-pointer overflow-hidden rounded-lg border border-[#dddddd] bg-white/60 p-4 transition-all duration-300 hover:shadow-lg backdrop-blur-sm">
                <motion.div
                  className={`absolute inset-0 bg-gradient-to-br ${category.gradient} opacity-0 transition-opacity duration-300`}
                  animate={{ opacity: hoveredIndex === index ? 0.1 : 0 }}
                />
                <div className="relative z-10 flex h-full flex-col">
                  <div className="mb-4 flex items-center gap-3">
                    <div
                      className={`flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br ${category.gradient}`}
                    >
                      <category.icon className="h-5 w-5 text-white" />
                    </div>
                    <span className="text-sm font-medium text-[#1c1c1c]">{category.name}</span>
                  </div>
                  <p className="text-xs text-[#525766] flex-grow">{category.description}</p>
                </div>
              </Card>
            </motion.div>
          </Link>
        ))}
      </div>
    </div>
  )
}




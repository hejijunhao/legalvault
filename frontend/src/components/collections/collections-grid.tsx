// src/components/collections/collections-grid.tsx

"use client"

import { motion } from "framer-motion"
import { CollectionCard } from "./collection-card"

const collections = [
  {
    id: "1",
    name: "Precedents",
    description: "Standard legal documents and agreements used as references",
    documentCount: 89,
    lastUpdated: "2 days ago",
    coverImage: "/placeholder.svg?height=400&width=400",
    gradient: "from-blue-500/20 to-cyan-500/20",
  },
  {
    id: "2",
    name: "Clausebank",
    description: "Repository of standardized legal clauses and provisions",
    documentCount: 234,
    lastUpdated: "1 week ago",
    coverImage: "/placeholder.svg?height=400&width=400",
    gradient: "from-purple-500/20 to-pink-500/20",
  },
  {
    id: "3",
    name: "Due Diligence",
    description: "Templates and checklists for due diligence processes",
    documentCount: 56,
    lastUpdated: "3 days ago",
    coverImage: "/placeholder.svg?height=400&width=400",
    gradient: "from-amber-500/20 to-red-500/20",
  },
  {
    id: "4",
    name: "Corporate Governance",
    description: "Board resolutions, minutes, and governance documents",
    documentCount: 112,
    lastUpdated: "5 days ago",
    coverImage: "/placeholder.svg?height=400&width=400",
    gradient: "from-emerald-500/20 to-teal-500/20",
  },
  {
    id: "5",
    name: "Employment",
    description: "Employment agreements and HR-related documents",
    documentCount: 78,
    lastUpdated: "1 day ago",
    coverImage: "/placeholder.svg?height=400&width=400",
    gradient: "from-rose-500/20 to-orange-500/20",
  },
  {
    id: "6",
    name: "Intellectual Property",
    description: "IP agreements, licenses, and related documents",
    documentCount: 145,
    lastUpdated: "4 days ago",
    coverImage: "/placeholder.svg?height=400&width=400",
    gradient: "from-indigo-500/20 to-violet-500/20",
  },
]

export function CollectionsGrid() {
  return (
    <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
      {collections.map((collection, index) => (
        <motion.div
          key={collection.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: index * 0.1 }}
        >
          <CollectionCard collection={collection} />
        </motion.div>
      ))}
    </div>
  )
}


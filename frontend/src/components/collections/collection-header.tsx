// src/components/collections/collection-header.tsx

import { motion } from "framer-motion"
import { FileText, Clock } from "lucide-react"

interface CollectionHeaderProps {
  collection: {
    name: string
    description: string
    documentCount: number
    lastUpdated: string
  }
}

export function CollectionHeader({ collection }: CollectionHeaderProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="rounded-xl bg-white p-6 shadow-lg"
    >
      <h1 className="mb-2 text-3xl font-bold text-gray-900">{collection.name}</h1>
      <p className="mb-4 text-lg text-gray-600">{collection.description}</p>
      <div className="flex items-center space-x-4 text-sm text-gray-500">
        <div className="flex items-center">
          <FileText className="mr-2 h-4 w-4" />
          <span>{collection.documentCount} documents</span>
        </div>
        <div className="flex items-center">
          <Clock className="mr-2 h-4 w-4" />
          <span>Last updated {collection.lastUpdated}</span>
        </div>
      </div>
    </motion.div>
  )
}


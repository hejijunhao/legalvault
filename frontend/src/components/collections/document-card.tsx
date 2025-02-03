// src/components/collections/document-card.tsx

import { motion } from "framer-motion"
import { Card } from "@/components/ui/card"
import { FileText, Calendar } from "lucide-react"

interface DocumentCardProps {
  document: {
    id: string
    name: string
    type: string
    lastModified: string
  }
}

export function DocumentCard({ document }: DocumentCardProps) {
  return (
    <motion.div whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.98 }} transition={{ duration: 0.2 }}>
      <Card className="group cursor-pointer overflow-hidden bg-white transition-all duration-300 hover:shadow-md">
        <div className="p-4">
          <div className="mb-2 flex items-center justify-between">
            <FileText className="h-6 w-6 text-blue-500" />
            <span className="rounded-full bg-blue-100 px-2 py-1 text-xs font-medium text-blue-800">
              {document.type}
            </span>
          </div>
          <h3 className="mb-2 text-lg font-semibold text-gray-900 group-hover:text-blue-600">{document.name}</h3>
          <div className="flex items-center text-sm text-gray-500">
            <Calendar className="mr-2 h-4 w-4" />
            <span>Modified {document.lastModified}</span>
          </div>
        </div>
      </Card>
    </motion.div>
  )
}


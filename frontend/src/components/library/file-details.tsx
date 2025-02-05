// src/components/library/file-details.tsx

"use client"
import { motion } from "framer-motion"
import { formatDistanceToNow } from "date-fns"
import { FileText, Calendar, Users, Tag, ArrowUpRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import type { File } from "./file-list"

interface FileDetailsProps {
  file: File | null
  onHoverStart: () => void
  onHoverEnd: () => void
  isSticky: boolean
}

export function FileDetails({ file, onHoverStart, onHoverEnd, isSticky }: FileDetailsProps) {
  if (!file) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="absolute left-8 right-8 top-4 flex flex-col items-center justify-center rounded-2xl border border-white/20 bg-white/60 p-12 text-center backdrop-blur-md"
      >
        <FileText className="mb-4 h-12 w-12 text-neutral-300" />
        <p className="text-lg text-neutral-400">Select a file to view details</p>
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`rounded-2xl border border-white/20 bg-white/60 p-6 backdrop-blur-md ${isSticky ? "shadow-lg" : ""}`}
      onMouseEnter={onHoverStart}
      onMouseLeave={onHoverEnd}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500/10 to-purple-500/10">
            <FileText className="h-6 w-6 text-blue-600" />
          </div>
          <div>
            <h3 className="text-lg font-medium text-neutral-900">{file.name}</h3>
            <div className="mt-1 flex items-center gap-2 text-sm text-neutral-500">
              <span>{file.type.toUpperCase()}</span>
              <span>•</span>
              <span>{file.size || "Unknown size"}</span>
            </div>
          </div>
        </div>
        <Button variant="outline" size="sm" className="gap-2">
          <span>View Details</span>
          <ArrowUpRight className="h-4 w-4" />
        </Button>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
        <div className="flex items-center gap-2 text-neutral-600">
          <Calendar className="h-4 w-4" />
          <span>Modified {formatDistanceToNow(new Date(file.lastModified))} ago</span>
        </div>
        {file.collaborators && (
          <div className="flex items-center gap-2 text-neutral-600">
            <Users className="h-4 w-4" />
            <span>{file.collaborators.length} Collaborators</span>
          </div>
        )}
      </div>

      {file.tags && (
        <div className="mt-4">
          <div className="mb-2 flex items-center gap-2 text-sm text-neutral-600">
            <Tag className="h-4 w-4" />
            <span>Tags</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {file.tags.slice(0, 3).map((tag) => (
              <span
                key={tag}
                className="rounded-full bg-gradient-to-br from-blue-50 to-purple-50 px-2 py-1 text-xs font-medium text-blue-800"
              >
                {tag}
              </span>
            ))}
            {file.tags.length > 3 && (
              <span className="rounded-full bg-neutral-100 px-2 py-1 text-xs font-medium text-neutral-600">
                +{file.tags.length - 3} more
              </span>
            )}
          </div>
        </div>
      )}
    </motion.div>
  )
}






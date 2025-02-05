// src/components/library/file-list.tsx

// src/components/library/file-list.tsx

"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { FileIcon, FileTextIcon, FileTypeIcon, FileSpreadsheetIcon, FileImageIcon } from "lucide-react"
import { formatDistanceToNow } from "date-fns"
import { FilePreview } from "./file-preview"

interface File {
  id: string
  name: string
  type: string
  lastModified: string
  size?: string
  creator?: string
  collaborators?: string[]
  tags?: string[]
  linkedFiles?: string[]
  version?: string
  accessLevel?: string
  comments?: number
  aiInsights?: string
}

interface FileListProps {
  files: File[]
}

export function FileList({ files }: FileListProps) {
  const [hoveredFile, setHoveredFile] = useState<File | null>(null)

  const getFileIcon = (type: string) => {
    const baseClass = "h-4 w-4 transition-colors duration-300"
    switch (type) {
      case "pdf":
        return <FileTextIcon className={`${baseClass} text-neutral-400 group-hover:text-neutral-900`} />
      case "docx":
        return <FileIcon className={`${baseClass} text-neutral-400 group-hover:text-neutral-900`} />
      case "xlsx":
        return <FileSpreadsheetIcon className={`${baseClass} text-neutral-400 group-hover:text-neutral-900`} />
      case "pptx":
        return <FileImageIcon className={`${baseClass} text-neutral-400 group-hover:text-neutral-900`} />
      default:
        return <FileTypeIcon className={`${baseClass} text-neutral-400 group-hover:text-neutral-900`} />
    }
  }

  // Enhanced mock data for the preview
  const getEnhancedFileData = (file: File): File => ({
    ...file,
    size: "2.4 MB",
    creator: "Sarah Chen",
    collaborators: ["Michael Wong", "David Kim"],
    tags: ["Contract", "TechCorp", "2023"],
    linkedFiles: ["Meeting Notes - TechCorp", "Previous Version"],
    version: "1.2",
    accessLevel: "Full",
    comments: 5,
    aiInsights:
      "This document contains standard service agreement terms with custom modifications in sections 3.4 and 5.2. Recent changes focus on liability caps and service level definitions.",
  })

  return (
    <div className="relative">
      {files.map((file, index) => (
        <motion.div
          key={file.id}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: index * 0.05 }}
          onMouseEnter={() => setHoveredFile(file)}
          onMouseLeave={() => setHoveredFile(null)}
        >
          <div className="group relative cursor-pointer overflow-hidden transition-all duration-300">
            {/* Hover highlight effect */}
            <div className="absolute inset-y-0 left-0 w-0.5 bg-gradient-to-b from-neutral-400/0 via-neutral-400/50 to-neutral-400/0 opacity-0 transition-opacity duration-300 group-hover:opacity-100" />

            <div className="flex items-center px-6 py-4">
              <div className="flex items-center space-x-4">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-white/80 transition-colors duration-300 group-hover:bg-white">
                  {getFileIcon(file.type)}
                </div>
                <div className="flex flex-col">
                  <span className="font-medium text-neutral-900 transition-colors duration-300 group-hover:text-blue-600">
                    {file.name}
                  </span>
                  <span className="text-xs text-neutral-400">
                    {file.type.toUpperCase()} • {formatDistanceToNow(new Date(file.lastModified), { addSuffix: true })}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      ))}

      <FilePreview file={hoveredFile ? getEnhancedFileData(hoveredFile) : null} isVisible={Boolean(hoveredFile)} />
    </div>
  )
}



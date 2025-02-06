// src/components/library/file-list.tsx

"use client"

import { motion } from "framer-motion"
import { FileIcon, FileTextIcon, FileTypeIcon, FileSpreadsheetIcon, FileImageIcon } from "lucide-react"
import { formatDistanceToNow } from "date-fns"
import Link from "next/link" // Add Link import

export interface File {
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
  category: string
  collection?: string
}

interface FileListProps {
  groupedFiles: Record<string, File[]>
  onFileHover: (file: File | null) => void
  onFileSelect: (file: File) => void
  selectedFileId: string | null
}

export function FileList({ groupedFiles, onFileHover, onFileSelect, selectedFileId }: FileListProps) {
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

  return (
    <div className="space-y-12 pt-6">
      {Object.entries(groupedFiles).map(([category, files]) => (
        <motion.div
          key={category}
          id={category.toLowerCase()}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="space-y-6"
        >
          <h3 className="mb-4 text-xl font-normal italic text-neutral-900 font-['Libre_Baskerville']">{category}</h3>
          <div className="space-y-1">
            {files.map((file, index) => (
              <Link
                key={file.id}
                href={`/library/files/${file.id}`}
                className="block"
                onClick={(e) => {
                  // Allow the hover and select events to still work
                  e.preventDefault()
                  onFileSelect(file)
                  // Navigate after a small delay to allow the selection animation
                  setTimeout(() => {
                    window.location.href = `/library/files/${file.id}`
                  }, 150)
                }}
              >
                <motion.div
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{
                    duration: 0.3,
                    ease: [0.4, 0, 0.2, 1],
                    delay: index * 0.05,
                  }}
                  onMouseEnter={() => onFileHover(file)}
                  onMouseLeave={() => onFileHover(null)}
                >
                  <div
                    className={`group relative cursor-pointer overflow-hidden rounded-lg transition-all duration-300 ease-in-out ${
                      selectedFileId === file.id ? "bg-blue-50" : "hover:bg-neutral-50"
                    }`}
                  >
                    <div className="flex items-center px-4 py-2">
                      <div className="flex items-center space-x-3">
                        <div className="flex h-8 w-8 items-center justify-center rounded-full">
                          {getFileIcon(file.type)}
                        </div>
                        <div className="flex flex-col">
                          <span className="font-medium text-neutral-900 transition-colors duration-300 group-hover:text-blue-600">
                            {file.name}
                          </span>
                          <span className="text-xs text-neutral-400">
                            {file.type.toUpperCase()} •{" "}
                            {formatDistanceToNow(new Date(file.lastModified), { addSuffix: true })}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              </Link>
            ))}
          </div>
        </motion.div>
      ))}
    </div>
  )
}




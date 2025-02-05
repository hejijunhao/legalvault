// src/components/library/file-preview.tsx

"use client"

import { motion } from "framer-motion"
import { format } from "date-fns"
import { Card } from "@/components/ui/card"
import { Calendar, FileText, Users, Tags, LinkIcon, History, Lock, MessageSquare, Bot } from "lucide-react"

interface FileMetadata {
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

interface FilePreviewProps {
  file: FileMetadata | null
  isVisible: boolean
}

export function FilePreview({ file, isVisible }: FilePreviewProps) {
  if (!file) return null

  return (
    <motion.div
      initial={{ opacity: 0, y: -20, scale: 0.95 }}
      animate={isVisible ? { opacity: 1, y: 0, scale: 1 } : { opacity: 0, y: -20, scale: 0.95 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className="pointer-events-none absolute left-1/2 top-[0px] z-50 w-[500px] -translate-x-1/2 transform"
    >
      <Card className="overflow-hidden border-white/10 bg-white/40 shadow-lg backdrop-blur-md transition-all duration-300">
        <div className="absolute inset-0 bg-gradient-to-br from-white/50 via-white/30 to-white/20 opacity-80" />
        <div className="relative z-10">
          <div className="p-6">
            {/* File Header */}
            <div className="mb-6 flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-white/80">
                <FileText className="h-6 w-6 text-neutral-600" />
              </div>
              <div>
                <h3 className="text-lg font-medium text-neutral-900">{file.name}</h3>
                <p className="text-sm text-neutral-500">
                  {file.type.toUpperCase()} {file.size && `• ${file.size}`}
                </p>
              </div>
            </div>

            {/* Metadata Grid */}
            <div className="grid gap-4">
              <div className="flex items-center gap-3 text-sm text-neutral-600">
                <Calendar className="h-4 w-4" />
                <span>Last modified {format(new Date(file.lastModified), "PPP")}</span>
              </div>

              {file.creator && (
                <div className="flex items-center gap-3 text-sm text-neutral-600">
                  <Users className="h-4 w-4" />
                  <span>Created by {file.creator}</span>
                </div>
              )}

              {file.collaborators && file.collaborators.length > 0 && (
                <div className="flex items-center gap-3 text-sm text-neutral-600">
                  <Users className="h-4 w-4" />
                  <span>{file.collaborators.length} collaborators</span>
                </div>
              )}

              {file.tags && file.tags.length > 0 && (
                <div className="flex items-center gap-3 text-sm text-neutral-600">
                  <Tags className="h-4 w-4" />
                  <div className="flex flex-wrap gap-1">
                    {file.tags.map((tag) => (
                      <span key={tag} className="rounded-full bg-neutral-100 px-2 py-0.5 text-xs text-neutral-600">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {file.linkedFiles && file.linkedFiles.length > 0 && (
                <div className="flex items-center gap-3 text-sm text-neutral-600">
                  <LinkIcon className="h-4 w-4" />
                  <span>{file.linkedFiles.length} linked files</span>
                </div>
              )}

              {file.version && (
                <div className="flex items-center gap-3 text-sm text-neutral-600">
                  <History className="h-4 w-4" />
                  <span>Version {file.version}</span>
                </div>
              )}

              {file.accessLevel && (
                <div className="flex items-center gap-3 text-sm text-neutral-600">
                  <Lock className="h-4 w-4" />
                  <span>{file.accessLevel} access</span>
                </div>
              )}

              {file.comments !== undefined && (
                <div className="flex items-center gap-3 text-sm text-neutral-600">
                  <MessageSquare className="h-4 w-4" />
                  <span>{file.comments} comments</span>
                </div>
              )}

              {file.aiInsights && (
                <div className="mt-4 rounded-lg bg-blue-50/50 p-4">
                  <div className="mb-2 flex items-center gap-2 text-sm font-medium text-blue-700">
                    <Bot className="h-4 w-4" />
                    AI Insights
                  </div>
                  <p className="text-sm text-blue-600">{file.aiInsights}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </Card>
    </motion.div>
  )
}


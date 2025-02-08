// src/components/library/search/source-block.tsx

"use client"

import { motion, AnimatePresence } from "framer-motion"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { ChevronDown, ExternalLink, FileText, Clock, User } from "lucide-react"

interface SourceBlockProps {
  id: string
  title: string
  type: string
  date: string
  url?: string
  fileSize?: string
  lastModified?: string
  creator?: string
  isExpanded: boolean
  onToggle: () => void
}

export function SourceBlock({
                              id,
                              title,
                              type,
                              date,
                              url,
                              fileSize,
                              lastModified,
                              creator,
                              isExpanded,
                              onToggle,
                            }: SourceBlockProps) {
  return (
    <Card className="w-full bg-white/60 backdrop-blur-sm transition-all duration-300 hover:bg-white/70">
      <CardHeader className="p-4" onClick={onToggle}>
        <CardTitle className="flex items-center justify-between">
          <span className="text-[10px] font-light tracking-[1px] text-[#1C1C1C]">SOURCE {id}</span>
          <span className="text-xs text-[#525766]">{date}</span>
        </CardTitle>
        <div className="mt-2 space-y-1">
          <h3 className="text-sm font-medium text-[#1C1C1C]">{title}</h3>
          <p className="text-xs text-[#8992a9]">{type}</p>
        </div>
        <ChevronDown
          className={`h-4 w-4 text-[#8992a9] transition-transform duration-300 ${isExpanded ? "rotate-180" : ""}`}
        />
      </CardHeader>
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            <CardContent className="px-4 pb-4">
              <div className="space-y-2 text-sm text-[#525766]">
                {url && (
                  <div className="flex items-center gap-2">
                    <ExternalLink className="h-4 w-4" />
                    <a href={url} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">
                      View Source
                    </a>
                  </div>
                )}
                {fileSize && (
                  <div className="flex items-center gap-2">
                    <FileText className="h-4 w-4" />
                    <span>File Size: {fileSize}</span>
                  </div>
                )}
                {lastModified && (
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4" />
                    <span>Last Modified: {lastModified}</span>
                  </div>
                )}
                {creator && (
                  <div className="flex items-center gap-2">
                    <User className="h-4 w-4" />
                    <span>Creator: {creator}</span>
                  </div>
                )}
              </div>
            </CardContent>
          </motion.div>
        )}
      </AnimatePresence>
    </Card>
  )
}


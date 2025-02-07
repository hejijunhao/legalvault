// src/components/library/file-viewer/information-panel.tsx

"use client"

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Info, FileText, Users, Calendar, Tag, Link } from "lucide-react"

interface InformationPanelProps {
  metadata: {
    created: string
    modified: string
    size: string
    creator: string
    collaborators: string[]
    tags: string[]
    source: string
  }
}

export function InformationPanel({ metadata }: InformationPanelProps) {
  return (
    <Card className="flex h-full flex-col rounded-[5px] bg-[rgba(191,219,254,0.20)] p-[11px_14px] backdrop-blur-sm">
      <CardHeader className="p-0 pb-2">
        <CardTitle className="flex items-center gap-2 text-[10px] font-light tracking-[1px] text-[#1C1C1C]">
          <Info className="h-4 w-4" />
          INFORMATION
        </CardTitle>
      </CardHeader>
      <CardContent className="flex flex-1 flex-col justify-between p-0">
        <div className="space-y-4">
          <div className="flex items-center gap-2 text-sm text-[#525766]">
            <FileText className="h-4 w-4" />
            <span>Size: {metadata.size}</span>
          </div>
          <div className="flex items-start gap-2 text-sm text-[#525766]">
            <Calendar className="h-4 w-4 mt-0.5" />
            <div className="space-y-1">
              <div>Created: {metadata.created}</div>
              <div>Modified: {metadata.modified}</div>
            </div>
          </div>
          <div className="flex items-start gap-2 text-sm text-[#525766]">
            <Users className="h-4 w-4 mt-0.5" />
            <div>
              <div>Created by: {metadata.creator}</div>
              <div className="mt-1 text-xs">Collaborators: {metadata.collaborators.join(", ")}</div>
            </div>
          </div>
          <div className="flex items-start gap-2">
            <Tag className="h-4 w-4 mt-1 text-[#525766]" />
            <div className="flex flex-wrap gap-1">
              {metadata.tags.map((tag) => (
                <span key={tag} className="rounded-full bg-[#9fe870]/20 px-2 py-0.5 text-xs text-[#09332b]">
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2 pt-4 text-sm text-[#525766]">
          <Link className="h-4 w-4" />
          <span>Source: {metadata.source}</span>
        </div>
      </CardContent>
    </Card>
  )
}


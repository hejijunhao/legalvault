// src/components/library/file-viewer/versions-panel.tsx

"use client"

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { GitBranch, Clock, Check } from "lucide-react"
import { Button } from "@/components/ui/button"

const versions = [
  {
    id: "v3",
    version: "3.0",
    date: "24 Feb 2024",
    author: "Sarah Chen",
    changes: "Updated payment terms and conditions",
    current: true,
  },
  {
    id: "v2",
    version: "2.0",
    date: "22 Feb 2024",
    author: "Michael Wong",
    changes: "Revised liability clauses",
  },
  {
    id: "v1",
    version: "1.0",
    date: "20 Feb 2024",
    author: "David Kim",
    changes: "Initial draft",
  },
]

export function VersionsPanel() {
  return (
    <Card className="flex h-full flex-col rounded-[5px] bg-[rgba(191,219,254,0.20)] p-[11px_14px] backdrop-blur-sm">
      <CardHeader className="p-0 pb-2">
        <CardTitle className="flex items-center gap-2 text-[10px] font-light tracking-[1px] text-[#1C1C1C]">
          <GitBranch className="h-4 w-4" />
          VERSIONS
        </CardTitle>
      </CardHeader>
      <CardContent className="flex flex-1 flex-col p-0">
        <div className="flex items-center gap-4 overflow-x-auto py-2">
          {versions.map((version) => (
            <Button
              key={version.id}
              variant="ghost"
              className={`group relative flex h-16 w-16 flex-col items-center justify-center gap-1 rounded-lg p-0 ${
                version.current ? "bg-white/50" : "hover:bg-white/30"
              }`}
            >
              {version.current && (
                <div className="absolute -right-1 -top-1 rounded-full bg-[#9fe870] p-0.5">
                  <Check className="h-3 w-3 text-[#09332b]" />
                </div>
              )}
              <Clock className="h-4 w-4 text-[#525766]" />
              <span className="text-xs font-medium text-[#1C1C1C]">{version.version}</span>
            </Button>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}


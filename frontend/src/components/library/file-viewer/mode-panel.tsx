// src/components/library/file-viewer/mode-panel.tsx

"use client"

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Eye, PenLine, GitCompare } from "lucide-react"
import { Button } from "@/components/ui/button"

const modes = [
  { id: "view", label: "View", icon: Eye },
  { id: "annotate", label: "Annotate", icon: PenLine },
  { id: "compare", label: "Compare", icon: GitCompare },
]

export function ModePanel() {
  return (
    <Card className="flex h-full flex-col rounded-[5px] bg-[rgba(191,219,254,0.20)] p-[11px_14px] backdrop-blur-sm">
      <CardHeader className="p-0 pb-2">
        <CardTitle className="flex items-center gap-2 text-[10px] font-light tracking-[1px] text-[#1C1C1C]">
          MODE
        </CardTitle>
      </CardHeader>
      <CardContent className="flex flex-1 items-center p-0">
        <div className="flex w-full items-center justify-between gap-2">
          {modes.map((mode) => (
            <Button
              key={mode.id}
              variant="ghost"
              className="flex h-16 w-full flex-col items-center justify-center gap-2 rounded-lg bg-white/50 p-0 hover:bg-white/70"
            >
              <mode.icon className="h-5 w-5 text-[#525766]" />
              <span className="text-xs font-medium text-[#1C1C1C]">{mode.label}</span>
            </Button>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}


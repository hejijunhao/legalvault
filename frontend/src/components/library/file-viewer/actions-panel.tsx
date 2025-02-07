// src/components/library/file-viewer/actions-panel.tsx

"use client"

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Share2, Download, ExternalLink, Printer, Mail, Copy, MoreHorizontal, Settings } from "lucide-react"

const quickActions = [
  { icon: Share2, label: "Share" },
  { icon: Download, label: "Download" },
  { icon: ExternalLink, label: "Open" },
  { icon: Printer, label: "Print" },
  { icon: Mail, label: "Email" },
  { icon: Copy, label: "Copy" },
  { icon: Settings, label: "Settings" },
  { icon: MoreHorizontal, label: "More" },
]

export function ActionsPanel() {
  return (
    <Card className="flex h-full flex-col rounded-[5px] bg-[rgba(191,219,254,0.20)] p-[11px_14px] backdrop-blur-sm">
      <CardHeader className="p-0 pb-2">
        <CardTitle className="flex items-center gap-2 text-[10px] font-light tracking-[1px] text-[#1C1C1C]">
          ACTIONS
        </CardTitle>
      </CardHeader>
      <CardContent className="grid flex-1 grid-cols-4 gap-2 p-0">
        {quickActions.map((action) => (
          <Button
            key={action.label}
            variant="ghost"
            className="flex h-16 flex-col items-center justify-center gap-1 rounded-lg bg-white/50 p-0 hover:bg-white/70"
          >
            <action.icon className="h-4 w-4 text-[#525766]" />
            <span className="text-xs text-[#1C1C1C]">{action.label}</span>
          </Button>
        ))}
      </CardContent>
    </Card>
  )
}


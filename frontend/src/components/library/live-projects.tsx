// src/components/library/live-projects.tsx

"use client"

import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area"
import { Card } from "@/components/ui/card"

const projects = [
  {
    id: 1,
    name: "GreenBridge",
    type: "LIVE M&A DEAL",
    gradient: "from-[#9FE870]/20 to-[#BFE999]/20"
  },
  {
    id: 2,
    name: "Adams v. Sculley",
    type: "LIVE LITIGATION",
    gradient: "from-[#AF52DE]/20 to-[#E5A4FF]/20"
  },
  {
    id: 3,
    name: "Project Sparta",
    type: "LIVE M&A DEAL",
    gradient: "from-[#FF9B9B]/20 to-[#FFC4C4]/20"
  },
  {
    id: 4,
    name: "JCLim v. PHenley",
    type: "LIVE LITIGATION",
    gradient: "from-[#00C7BE]/20 to-[#7DEAE5]/20"
  },
  {
    id: 5,
    name: "Project Norse",
    type: "LIVE S&P DEAL",
    gradient: "from-[#93C5FD]/20 to-[#BFDBFE]/20"
  }
]

export function LiveProjects() {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-[10px] font-light tracking-[1px] text-[#1C1C1C]">
          CURRENTLY LIVE
        </h2>
        <button className="text-xs text-[#8992A9] hover:text-[#525766]">
          VIEW ALL
        </button>
      </div>
      <ScrollArea className="w-full whitespace-nowrap">
        <div className="flex w-max space-x-4 p-1">
          {projects.map((project) => (
            <Card
              key={project.id}
              className={`w-[200px] cursor-pointer bg-gradient-to-br p-6 transition-all hover:scale-[1.02] ${project.gradient}`}
            >
              <h3 className="font-medium text-[#1C1C1C]">{project.name}</h3>
              <p className="text-xs text-[#525766]">{project.type}</p>
            </Card>
          ))}
        </div>
        <ScrollBar orientation="horizontal" />
      </ScrollArea>
    </div>
  )
}


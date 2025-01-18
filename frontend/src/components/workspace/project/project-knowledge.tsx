// src/components/workspace/project/project-knowledge.tsx

"use client"

import { ProjectTabs } from "./project-tabs"
import { Card } from "@/components/ui/card"

export function Knowledge() {
  const tabs = [
    {
      id: "knowledge",
      label: "Knowledge",
      content: (
        <div className="text-[13px] font-normal tracking-[-0.39px] text-[#111827] font-inter">
          The merger of TerraLink Construction and EcoBuild Innovations to form TerraEco Holdings Pte Ltd is a strategic response to the growing emphasis on sustainable construction in Singapore and Southeast Asia. TerraLink&apos;s extensive industry experience and EcoBuild&apos;s innovative green technologies are united to create a company positioned as a leader in sustainable building practices.
        </div>
      )
    },
    {
      id: "summary",
      label: "Summary",
      content: (
        <div className="space-y-4 text-[13px] font-normal tracking-[-0.39px] text-[#111827] font-inter">
          <h3 className="font-semibold">Deal Overview</h3>
          <p>Merger between TerraLink Construction and EcoBuild Innovations to form TerraEco Holdings Pte Ltd.</p>
          <h3 className="font-semibold">Key Objectives</h3>
          <ul className="list-inside list-disc space-y-2">
            <li>Combine industry experience with innovative green technologies</li>
            <li>Establish market leadership in sustainable construction</li>
            <li>Expand presence in Southeast Asian markets</li>
          </ul>
        </div>
      )
    },
    {
      id: "files",
      label: "Files",
      content: (
        <div className="text-[13px] font-normal tracking-[-0.39px] text-[#111827] font-inter">
          File management interface coming soon
        </div>
      )
    },
    {
      id: "calendar",
      label: "Calendar",
      content: (
        <div className="text-[13px] font-normal tracking-[-0.39px] text-[#111827] font-inter">
          Calendar interface coming soon
        </div>
      )
    },
    {
      id: "communications",
      label: "Communications",
      content: (
        <div className="text-[13px] font-normal tracking-[-0.39px] text-[#111827] font-inter">
          Communications interface coming soon
        </div>
      )
    },
    {
      id: "contacts",
      label: "Contacts",
      content: (
        <div className="text-[13px] font-normal tracking-[-0.39px] text-[#111827] font-inter">
          Contacts interface coming soon
        </div>
      )
    },
    {
      id: "activity",
      label: "Activity",
      content: (
        <div className="text-[13px] font-normal tracking-[-0.39px] text-[#111827] font-inter">
          Activity feed coming soon
        </div>
      )
    }
  ]

  return (
    <Card className="flex h-[725px] flex-1 flex-col rounded-[5px] border-[#E5E7EB] bg-white/10 backdrop-blur-sm">
      <ProjectTabs tabs={tabs} />
    </Card>
  )
}
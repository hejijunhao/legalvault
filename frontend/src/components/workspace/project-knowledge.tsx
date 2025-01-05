// src/components/workspace/project-knowledge.tsx

import { Card, CardTitle } from "@/components/ui/card"

export function ProjectKnowledge() {
  return (
    <Card className="flex h-[725px] flex-1 flex-col items-start gap-2.5 self-stretch rounded-[5px] border-[#E5E7EB] bg-[rgba(159,232,112,0.20)] p-[11px_14px] backdrop-blur-sm">
      <CardTitle className="h-[18.493px] self-stretch text-[10px] font-light tracking-[1px] text-[#1C1C1C]">
        PROJECT GREENBRIDGE
      </CardTitle>
      <p className="flex-1 text-[13px] font-normal tracking-[-0.39px] text-[#111827]">
        The merger of TerraLink Construction and EcoBuild Innovations to form TerraEco Holdings Pte Ltd is a strategic response to the growing emphasis on sustainable construction in Singapore and Southeast Asia. TerraLink&apos;s extensive industry experience and EcoBuild&apos;s innovative green technologies are united to create a company positioned as a leader in sustainable building practices.
      </p>
    </Card>
  )
}
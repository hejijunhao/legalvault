// src/components/workspace/notebook.tsx

import { Card, CardTitle } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"

export function Notebook() {
  return (
    <Card className="flex flex-1 flex-col items-start gap-2.5 self-stretch rounded-[5px] border-[#E5E7EB] bg-[rgba(191,219,254,0.20)] p-[11px_14px] backdrop-blur-sm">
      <div className="flex flex-1 flex-col items-start gap-[6px] self-stretch">
        <CardTitle className="h-[18.493px] self-stretch text-[10px] font-light tracking-[1px] text-[#1C1C1C]">
          NOTEBOOK
        </CardTitle>
        <Textarea
          placeholder="Start typing a new note..."
          className="min-h-[180px] w-full resize-none border-0 bg-transparent p-0 text-[14px] font-normal tracking-[-0.42px] text-[#525766] placeholder:text-[#525766] focus:ring-0 focus-visible:ring-0"
        />
      </div>
    </Card>
  )
}
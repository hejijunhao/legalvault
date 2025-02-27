// src/components/research/search/research-header.tsx

import { cn } from "@/lib/utils"

interface ResearchHeaderProps {
  query: string
}

export function ResearchHeader({ query }: ResearchHeaderProps) {
  return (
    <div className="mb-4 -mt-8 text-center">
      <h1 className={cn("text-[32px] font-normal italic leading-normal text-[#1c1c1c]", "font-['Libre_Baskerville']")}>
        {query}
      </h1>
    </div>
  )
}




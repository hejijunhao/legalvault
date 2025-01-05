// src/components/library/launchpad.tsx

import { Card } from "@/components/ui/card"
import Image from "next/image"

const tools = [
  { id: 1, name: "Westlaw", logo: "/placeholder.svg" },
  { id: 2, name: "LexisNexis", logo: "/placeholder.svg" },
  { id: 3, name: "Bloomberg Law", logo: "/placeholder.svg" },
  { id: 4, name: "HeinOnline", logo: "/placeholder.svg" },
  { id: 5, name: "PACER", logo: "/placeholder.svg" },
  { id: 6, name: "iManage", logo: "/placeholder.svg" },
  { id: 7, name: "SharePoint", logo: "/placeholder.svg" },
  { id: 8, name: "Dropbox", logo: "/placeholder.svg" },
]

export function Launchpad() {
  return (
    <div className="space-y-4">
      <h2 className="text-[10px] font-light tracking-[1px] text-[#1C1C1C]">
        LAUNCHPAD
      </h2>
      <div className="grid grid-cols-2 gap-4">
        {tools.map((tool) => (
          <Card
            key={tool.id}
            className="flex aspect-[2/1] cursor-pointer items-center justify-center p-4 transition-all hover:scale-[1.02]"
          >
            <Image
              src={tool.logo}
              alt={tool.name}
              width={80}
              height={40}
              className="object-contain"
            />
          </Card>
        ))}
      </div>
    </div>
  )
}
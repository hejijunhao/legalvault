// src/components/library/collections.tsx

import { Card } from "@/components/ui/card"
import Image from "next/image"

const collections = [
  { id: 1, name: "Templates", type: "COLLECTION" },
  { id: 2, name: "Clausebank", type: "COLLECTION" },
  { id: 3, name: "Precedents", type: "COLLECTION" },
  { id: 4, name: "AI Companies", type: "COLLECTION" },
]

export function Collections() {
  return (
    <div className="space-y-4">
      <h2 className="text-[10px] font-light tracking-[1px] text-[#1C1C1C]">
        COLLECTIONS
      </h2>
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        {collections.map((collection) => (
          <Card
            key={collection.id}
            className="flex cursor-pointer flex-col items-center gap-3 p-6 transition-all hover:scale-[1.02]"
          >
            <div className="relative h-24 w-24 overflow-hidden rounded-full">
              <Image
                src={`/placeholder.svg?height=96&width=96`}
                alt={collection.name}
                width={96}
                height={96}
                className="object-cover"
              />
            </div>
            <div className="text-center">
              <h3 className="text-sm font-medium text-[#1C1C1C]">{collection.name}</h3>
              <p className="text-xs text-[#525766]">{collection.type}</p>
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}
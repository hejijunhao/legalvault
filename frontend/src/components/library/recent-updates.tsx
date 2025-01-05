// src/components/library/recent-updates.tsx

import { Card } from "@/components/ui/card"

const updates = [
  {
    id: 1,
    time: "Now",
    content: "Extended the submission deadline for Carter Holdings' audit report from October 31 to November 15."
  },
  {
    id: 2,
    time: "3h ago",
    content: "Crescent Data requested addition of enhanced data privacy clauses to service agreement."
  },
  {
    id: 3,
    time: "4h ago",
    content: "Final terms for acquisition of Clearview Technologies revised to include adj. to payment schedules, non-compete clauses."
  }
]

export function RecentUpdates() {
  return (
    <div className="space-y-4">
      <h2 className="text-[10px] font-light tracking-[1px] text-[#1C1C1C]">
        RECENT UPDATES
      </h2>
      <div className="space-y-2">
        {updates.map((update) => (
          <Card
            key={update.id}
            className="overflow-hidden bg-[rgba(191,219,254,0.20)] p-4"
          >
            <p className="text-xs font-medium text-[#525766]">{update.time}</p>
            <p className="text-sm text-[#1C1C1C] line-clamp-2">{update.content}</p>
          </Card>
        ))}
      </div>
    </div>
  )
}


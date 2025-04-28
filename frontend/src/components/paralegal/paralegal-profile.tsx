// src/components/paralegal/paralegal-profile.tsx

import { VPIdentityCard } from "./vp-identity-card"
import { KnowledgeMemoryCard } from "./knowledge-memory-card"
import { VirtualParalegalResponse } from "@/services/paralegal/paralegal-api-types"

interface ParalegalProfileProps {
  paralegal: VirtualParalegalResponse
}

export function ParalegalProfile({ paralegal }: ParalegalProfileProps) {
  return (
    <div className="space-y-6">
      <VPIdentityCard paralegal={paralegal} />
      <KnowledgeMemoryCard disabled />
    </div>
  )
}
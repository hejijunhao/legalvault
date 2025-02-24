// src/components/paralegal/paralegal-profile.tsx

import { VPIdentityCard } from "./vp-identity-card"
import { KnowledgeMemoryCard } from "./knowledge-memory-card"

export function ParalegalProfile() {
  return (
    <div className="space-y-6">
      <VPIdentityCard />
      <KnowledgeMemoryCard />
    </div>
  )
}




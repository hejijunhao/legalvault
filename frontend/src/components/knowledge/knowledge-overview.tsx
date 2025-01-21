// src/components/knowledge/knowledge-overview.tsx

"use client"

import { SelfConsciousness } from "./self-consciousness"
import { GeneralKnowledge } from "./general-knowledge"
import { Education } from "./education"
import { PastConversations } from "./past-conversations"
import { PastTasks } from "./past-tasks"
import { ProjectKnowledge } from "./project-knowledge"

export function KnowledgeOverview() {
  return (
    <div className="grid gap-6">
      {/* Top Row - Larger sections */}
      <div className="grid gap-6 lg:grid-cols-2">
        <SelfConsciousness />
        <GeneralKnowledge />
      </div>

      {/* Middle Row */}
      <div className="grid gap-6 lg:grid-cols-2">
        <Education />
        <PastConversations />
      </div>

      {/* Bottom Row */}
      <div className="grid gap-6 lg:grid-cols-2">
        <PastTasks />
        <ProjectKnowledge />
      </div>
    </div>
  )
}


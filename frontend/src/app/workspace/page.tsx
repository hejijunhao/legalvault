// src/app/workspace/page.tsx

import { Notebook } from "@/components/workspace/notebook"
import { Tasks } from "@/components/workspace/tasks"
import { Reminders } from "@/components/workspace/reminders"
import { ProjectKnowledge } from "@/components/workspace/project-knowledge"

export default function WorkspacePage() {
  return (
    <div className="mx-auto w-full max-w-[1280px] space-y-6 py-6">
      <div className="grid gap-6 md:grid-cols-3">
        <Notebook />
        <Tasks />
        <Reminders />
      </div>
      <ProjectKnowledge />
    </div>
  )
}
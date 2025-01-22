// src/app/(app)/workspace/projects/[projectId]/page.tsx

import { Notebook } from "@/components/workspace/project/notebook"
import { Tasks } from "@/components/workspace/project/tasks"
import { Reminders } from "@/components/workspace/project/reminders"
import { Knowledge } from "@/components/workspace/project/project-knowledge"
import { ArrowLeft } from 'lucide-react'
import Link from 'next/link'

// This will be replaced with real data fetching once backend is connected
const getDummyProject = (projectId: string) => {
  return {
    id: projectId,
    name: projectId === "project-greenbridge" ? "Project Greenbridge" : `Project ${projectId}`,
    // Add other project fields as needed
  }
}

export default function ProjectPage({ params }: { params: { projectId: string } }) {
  const project = getDummyProject(params.projectId)

  return (
    <div className="mx-auto w-full max-w-[1280px] space-y-6 py-6">
      {/* Back Navigation and Title */}
      <div className="flex flex-col gap-4">
        <div className="flex justify-between items-center self-stretch">
          <Link
            href="/workspace"
            className="flex items-center gap-1.5 rounded-[5px] px-2 py-1 hover:bg-black/5"
          >
            <ArrowLeft className="h-3 w-3 text-[#1C1C1C]" />
            <span className="text-xs text-[#1C1C1C]">All Workspaces</span>
          </Link>
        </div>
        <h1 className="flex h-11 flex-1 flex-col justify-center text-[32px] font-normal italic leading-6 text-[#111827] font-['Libre_Baskerville']">
          {project.name}
        </h1>
      </div>

      {/* Content Grid */}
      <div className="grid gap-6 md:grid-cols-3">
        <Notebook />
        <Tasks />
        <Reminders />
      </div>
      <Knowledge />
    </div>
  )
}



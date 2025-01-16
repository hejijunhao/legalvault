// src/app/workspaces/page.tsx

import { ProjectList } from "@/components/workspaces/project-list"
import { ClientGrid } from "@/components/workspaces/client-grid"

export default function WorkspacesPage() {
  return (
    <div className="mx-auto w-full max-w-[1440px] px-4 py-6">
      <div className="flex flex-col items-start gap-[15px] self-stretch">
        <h1 className="text-[32px] font-normal italic leading-6 text-[#111827] font-['Libre_Baskerville']">
          Workspaces
        </h1>
        <ProjectList />
      </div>
      <div className="mt-6">
        <ClientGrid />
      </div>
    </div>
  )
}
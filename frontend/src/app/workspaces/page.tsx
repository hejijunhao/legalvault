// src/app/workspaces/page.tsx

import { ProjectList } from "@/components/workspaces/project-list"
import { ClientGrid } from "@/components/workspaces/client-grid"
import { Plus, MonitorSmartphone } from 'lucide-react'

export default function WorkspacesPage() {
  return (
    <div className="mx-auto w-full max-w-[1440px] px-4 py-6">
      <div className="flex flex-col items-start gap-[15px] self-stretch">
        <div className="flex w-full items-center justify-between">
          <h1 className="text-[32px] font-normal italic leading-6 text-[#111827] font-['Libre_Baskerville']">
            Workspaces
          </h1>
          <div className="flex items-center gap-2">
            <button className="flex h-8 w-8 items-center justify-center rounded-full bg-[#9FE870] p-1 transition-colors hover:bg-[#9FE870]/90">
              <Plus className="h-5 w-5 text-[#09332B]" />
            </button>
            <button className="flex items-center gap-1.5 rounded-xl bg-[#BFDBFE] px-2 py-1 transition-colors hover:bg-[#BFDBFE]/90">
              <MonitorSmartphone className="h-4 w-4 text-[#111827]" />
              <span className="text-sm text-[#111827]">Tasks & Reminders</span>
            </button>
          </div>
        </div>
        <ProjectList />
      </div>
      <div className="mt-6">
        <ClientGrid />
      </div>
    </div>
  )
}


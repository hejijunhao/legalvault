// src/app/(app)/workspace/page.tsx

"use client"

import { useState } from "react"
import { ProjectList } from "@/components/workspace/project-list"
import { ClientGrid } from "@/components/workspace/client-grid"
import { NewItemDialog } from "@/components/workspace/new-item-dialog"
import { Plus } from 'lucide-react'

export default function WorkspacePage() {
  const [isDialogOpen, setIsDialogOpen] = useState(false)

  return (
    <div className="mx-auto w-full max-w-[1440px] px-4 py-6">
      <div className="flex flex-col items-start gap-[15px] self-stretch">
        <div className="group flex items-center gap-4">
          <h1 className="text-[32px] font-normal italic leading-6 text-[#111827] font-['Libre_Baskerville']">
            Workspaces
          </h1>
          <button
            aria-label="Add new workspace item"
            onClick={() => setIsDialogOpen(true)}
            className="flex h-8 w-8 items-center justify-center rounded-full border border-[#8992A9]/20 bg-white/50 text-[#8992A9] opacity-0 transition-all hover:border-[#8992A9]/40 hover:bg-white/80 hover:text-[#525766] group-hover:opacity-100"
          >
            <Plus className="h-4 w-4" />
          </button>
        </div>
        <ProjectList />
      </div>
      <div className="mt-6">
        <ClientGrid />
      </div>
      <NewItemDialog isOpen={isDialogOpen} onClose={() => setIsDialogOpen(false)} />
    </div>
  )
}

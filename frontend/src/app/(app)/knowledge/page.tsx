// src/app/knowledge/page.tsx

"use client"

import { KnowledgeOverview } from "@/components/knowledge/knowledge-overview"
import { Button } from "@/components/ui/button"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"

export default function KnowledgePage() {
  return (
    <div className="mx-auto max-w-[1440px] px-4 py-6">
      <div className="mb-6 flex items-center justify-between">
        <Link href="/paralegal">
          <Button variant="ghost" size="sm" className="gap-2">
            <ArrowLeft className="h-4 w-4" />
            Back to Paralegal
          </Button>
        </Link>
        <h1 className="text-2xl font-bold">Knowledge Base</h1>
      </div>
      <KnowledgeOverview />
    </div>
  )
}
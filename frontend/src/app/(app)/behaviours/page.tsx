// src/app/(app)/behaviours/page.tsx

import { BehavioursOverview } from "@/components/behaviours/behaviours-overview"
import { Button } from "@/components/ui/button"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"

export default function BehavioursPage() {
  return (
    <div className="mx-auto max-w-[1440px] px-4 py-6">
      <div className="mb-6 flex items-center justify-between">
        <Link href="/paralegal">
          <Button variant="ghost" size="sm" className="gap-2">
            <ArrowLeft className="h-4 w-4" />
            Back to Paralegal
          </Button>
        </Link>
        <h1 className="text-2xl font-bold">VP Behaviours</h1>
      </div>
      <BehavioursOverview />
    </div>
  )
}


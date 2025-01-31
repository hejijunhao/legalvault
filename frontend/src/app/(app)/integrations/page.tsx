// app/(app)/integrations/page.tsx

import { IntegrationsOverview } from "@/components/integrations/integrations-overview"
import { Button } from "@/components/ui/button"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"

export default function IntegrationsPage() {
  return (
    <div className="min-h-screen">
      <div className="mx-auto max-w-[1440px] px-4 py-6">
        <div className="mb-6 flex items-center justify-between">
          <Link href="/paralegal">
            <Button variant="ghost" size="sm" className="gap-2 hover:bg-black/5">
              <ArrowLeft className="h-4 w-4" />
              <span className="text-[#1C1C1C]">Back to Paralegal</span>
            </Button>
          </Link>
        </div>
        <IntegrationsOverview />
      </div>
    </div>
  )
}
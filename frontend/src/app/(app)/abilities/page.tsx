// src/app/abilities/page.tsx

"use client"

import { AbilityBoxes } from "@/components/abilities/ability-boxes"
import { Button } from "@/components/ui/button"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"

export default function AbilitiesPage() {
  return (
    <div className="relative min-h-screen">
      <div className="mx-auto max-w-[1440px] px-4">
        <div className="mb-6 pt-6">
          <Button
            variant="outline"
            size="sm"
            asChild
            className="gap-2 border-[#8992A9] bg-transparent text-[#1C1C1C] hover:bg-[#8992A9]/10"
          >
            <Link href="/paralegal">
              <ArrowLeft className="h-4 w-4" />
              Back to VP Profile
            </Link>
          </Button>
        </div>
        <div className="mb-8">
          <h1 className="mb-2 text-center text-2xl font-bold text-[#1C1C1C]">VP Abilities Overview</h1>
          <p className="text-center text-sm text-[#525766]">Explore and unlock your Virtual Paralegal's capabilities</p>
        </div>
      </div>
      <div className="w-full px-4">
        <AbilityBoxes />
      </div>
    </div>
  )
}

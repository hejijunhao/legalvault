// src/app/abilities.page.tsx

"use client"

import { AbilityTree } from "@/components/abilities/ability-tree"
import { Button } from "@/components/ui/button"
import { ArrowLeft } from 'lucide-react'
import Link from "next/link"

export default function AbilitiesPage() {
  return (
    <div className="relative min-h-screen p-6">
      <div className="mx-auto max-w-[1440px] px-4">
        <div className="mb-6">
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
        <div className="mx-auto max-w-5xl">
          <h1 className="mb-2 text-center text-2xl font-bold text-[#1C1C1C]">VP Abilities Overview</h1>
          <p className="mb-8 text-center text-sm text-[#525766]">
            Unlock and customise your Virtual Paralegal's capabilities through our evolving skill tree.
          </p>
          <div className="aspect-square w-full">
            <AbilityTree
              onNodeClick={(nodeId) => {
                // Handle node click
                console.log("Clicked node:", nodeId);
              }}
            />
          </div>
        </div>
      </div>
    </div>
  )
}


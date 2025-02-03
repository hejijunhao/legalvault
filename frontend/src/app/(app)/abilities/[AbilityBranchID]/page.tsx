// src/app/(app)/abilities/[AbilityBranchID]/page.tsx

"use client"

import { useParams } from "next/navigation"
import { Button } from "@/components/ui/button"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"
import { AbilityTreeFlow } from "@/components/abilities/ability-tree-flow"
import { abilityTrees } from "@/lib/ability-data"

export default function AbilityBranchPage() {
  const params = useParams()
  const branch = params.AbilityBranchID as string
  const tree = abilityTrees[branch as keyof typeof abilityTrees]

  if (!tree) {
    return <div>Ability branch not found</div>
  }

  return (
    <div className="min-h-screen">
      <div className="mx-auto max-w-[1440px] px-4">
        <div className="mb-6 pt-6">
          <Button
            variant="outline"
            size="sm"
            asChild
            className="gap-2 border-[#8992A9] bg-white/50 text-[#1C1C1C] hover:bg-[#8992A9]/10"
          >
            <Link href="/abilities">
              <ArrowLeft className="h-4 w-4" />
              Back to Abilities
            </Link>
          </Button>
        </div>
        <div className="mb-8 text-center">
          <h1 className="mb-2 text-2xl font-bold text-[#1C1C1C]">{tree.name} Abilities</h1>
          <p className="text-sm text-[#525766]">{tree.description}</p>
        </div>
      </div>
      <div className="h-[calc(100vh-200px)]">
        <AbilityTreeFlow tree={tree} />
      </div>
    </div>
  )
}



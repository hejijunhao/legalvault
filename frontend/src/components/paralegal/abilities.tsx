// components/paralegal/abilities.tsx

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import Link from "next/link"
import { ArrowRight } from 'lucide-react'

export function Abilities() {
  return (
    <Card className="h-full bg-[rgba(191,219,254,0.20)] transition-all hover:bg-[rgba(191,219,254,0.30)]">
      <Link href="/abilities" className="flex h-full flex-col">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center justify-between text-[10px] font-light tracking-[1px] text-[#1C1C1C]">
            ABILITIES
            <ArrowRight className="h-4 w-4" />
          </CardTitle>
        </CardHeader>
        <CardContent className="flex flex-1 items-center justify-center">
          <p className="text-center text-sm text-[#525766]">Click to view VP Abilities Overview</p>
        </CardContent>
      </Link>
    </Card>
  )
}
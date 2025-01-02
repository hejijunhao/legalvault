// components/paralegal/behaviors-card.tsx
"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ChevronRight, Timer } from 'lucide-react'
import type { VPBehavior } from "@/types/paralegal"

interface BehaviorsCardProps {
  behaviors: VPBehavior[];
}

export default function BehaviorsCard({ behaviors }: BehaviorsCardProps) {
  return (
    <Card className="border-gray-200 bg-white/50 backdrop-blur-sm shadow-sm">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-primary">Behaviors</CardTitle>
        <ChevronRight className="h-5 w-5 text-gray-500" />
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-5 gap-4">
          {behaviors.map((behavior) => (
            <div key={behavior.id} className="flex flex-col items-center space-y-2">
              <div className={`rounded-full border-2 border-${behavior.color} bg-gray-800 p-3`}>
                <Timer className={`h-6 w-6 text-${behavior.color}`} />
              </div>
              <span className="text-xs text-gray-400">{behavior.name}</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
// components/paralegal/abilities-card.tsx
"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import { ChevronRight, Search, FileText } from 'lucide-react'
import type { VPAbility } from "@/types/paralegal"

interface AbilitiesCardProps {
  abilities: VPAbility[];
}

export default function AbilitiesCard({ abilities }: AbilitiesCardProps) {
  return (
    <Card className="border-gray-200 bg-white/50 backdrop-blur-sm shadow-sm">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-primary">Abilities</CardTitle>
        <ChevronRight className="h-5 w-5 text-gray-500" />
      </CardHeader>
      <CardContent>
        <TooltipProvider>
          <div className="flex justify-between">
            {abilities.map((ability) => (
              <Tooltip key={ability.id}>
                <TooltipTrigger>
                  <div className="flex flex-col items-center space-y-2">
                    <div className="rounded-full border-2 border-primary bg-white p-3">
                      {/* This is temporary - we'll handle icons dynamically later */}
                      {ability.name === 'Research' ? (
                        <Search className="h-6 w-6 text-primary" />
                      ) : (
                        <FileText className="h-6 w-6 text-primary" />
                      )}
                    </div>
                    <span className="text-xs text-gray-400">{ability.name}</span>
                  </div>
                </TooltipTrigger>
                <TooltipContent>
                  <p>{ability.description}</p>
                </TooltipContent>
              </Tooltip>
            ))}
          </div>
        </TooltipProvider>
      </CardContent>
    </Card>
  )
}
// components/paralegal/access-card.tsx
"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ChevronRight, Gavel } from 'lucide-react'
import type { VPAccess } from "@/types/paralegal"

interface AccessCardProps {
  access: VPAccess[];
}

export default function AccessCard({ access }: AccessCardProps) {
  return (
    <Card className="border-gray-200 bg-white/50 backdrop-blur-sm shadow-sm">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-primary">Access</CardTitle>
        <ChevronRight className="h-5 w-5 text-gray-500" />
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-3 gap-4 md:grid-cols-6">
          {access.map((item) => (
            <div key={item.id} className="flex flex-col items-center space-y-2">
              <div className="rounded-lg border-2 border-gray-200 bg-white p-3">
                <Gavel className="h-6 w-6 text-gray-400" />
              </div>
              <span className="text-xs text-gray-400">{item.name}</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
// src/components/behaviours/behaviours-overview.tsx

"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Switch } from "@/components/ui/switch"
import { Slider } from "@/components/ui/slider"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

const behaviours = [
  { id: "formality", name: "Communication Formality", type: "slider" },
  { id: "proactivity", name: "Proactivity", type: "switch" },
  { id: "detailLevel", name: "Detail Level", type: "select" },
  { id: "riskTolerance", name: "Risk Tolerance", type: "slider" },
  { id: "creativity", name: "Creativity", type: "switch" },
  { id: "responsiveness", name: "Responsiveness", type: "select" },
]

export function BehavioursOverview() {
  const [values, setValues] = useState({
    formality: 50,
    proactivity: false,
    detailLevel: "medium",
    riskTolerance: 30,
    creativity: true,
    responsiveness: "high",
  })

  const handleChange = (id: string, value: any) => {
    setValues((prev) => ({ ...prev, [id]: value }))
  }

  return (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {behaviours.map((behaviour) => (
        <Card key={behaviour.id} className="overflow-hidden backdrop-blur-sm">
          <CardHeader className="border-b bg-white/5 p-4">
            <CardTitle className="text-lg">{behaviour.name}</CardTitle>
          </CardHeader>
          <CardContent className="p-4">
            {behaviour.type === "slider" && (
              <Slider
                value={[values[behaviour.id as keyof typeof values] as number]}
                onValueChange={(value) => handleChange(behaviour.id, value[0])}
                max={100}
                step={1}
                className="mt-2"
              />
            )}
            {behaviour.type === "switch" && (
              <Switch
                checked={values[behaviour.id as keyof typeof values] as boolean}
                onCheckedChange={(value) => handleChange(behaviour.id, value)}
              />
            )}
            {behaviour.type === "select" && (
              <Select
                value={values[behaviour.id as keyof typeof values] as string}
                onValueChange={(value) => handleChange(behaviour.id, value)}
              >
                <SelectTrigger className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Low</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                </SelectContent>
              </Select>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  )
}


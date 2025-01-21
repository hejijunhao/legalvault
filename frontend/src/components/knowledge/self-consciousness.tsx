// src/components/knowledge/self-consciousness.tsx

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Brain, Languages, Sparkles } from "lucide-react"

export function SelfConsciousness() {
  return (
    <Card className="overflow-hidden backdrop-blur-sm">
      <CardHeader className="border-b bg-white/5 p-6">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Brain className="h-5 w-5" />
          Self-Consciousness
        </CardTitle>
      </CardHeader>
      <CardContent className="grid gap-6 p-6">
        <div className="space-y-4">
          <h3 className="text-sm font-medium">Core Attributes</h3>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-[#8992A9]" />
                <span className="text-sm text-[#525766]">Analytical Thinking</span>
              </div>
              <div className="flex items-center gap-2">
                <Languages className="h-4 w-4 text-[#8992A9]" />
                <span className="text-sm text-[#525766]">Multilingual Support</span>
              </div>
            </div>
            <div className="space-y-2">
              <div className="text-sm text-[#525766]">
                Specializations:
                <ul className="mt-1 list-inside list-disc">
                  <li>Corporate Law</li>
                  <li>Contract Analysis</li>
                  <li>Due Diligence</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}


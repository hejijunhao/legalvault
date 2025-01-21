// src/components/workspace/general-knowledge.tsx

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Globe, Users, Building } from "lucide-react"

export function GeneralKnowledge() {
  return (
    <Card className="overflow-hidden backdrop-blur-sm">
      <CardHeader className="border-b bg-white/5 p-6">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Globe className="h-5 w-5" />
          General Knowledge
        </CardTitle>
      </CardHeader>
      <CardContent className="grid gap-6 p-6">
        <div className="grid gap-4 sm:grid-cols-3">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Building className="h-4 w-4 text-[#8992A9]" />
              <span className="text-sm font-medium">Projects</span>
            </div>
            <p className="text-2xl font-bold text-[#525766]">24</p>
            <p className="text-xs text-[#8992A9]">Active Projects</p>
          </div>
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Users className="h-4 w-4 text-[#8992A9]" />
              <span className="text-sm font-medium">Team</span>
            </div>
            <p className="text-2xl font-bold text-[#525766]">12</p>
            <p className="text-xs text-[#8992A9]">Legal Professionals</p>
          </div>
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Globe className="h-4 w-4 text-[#8992A9]" />
              <span className="text-sm font-medium">Jurisdictions</span>
            </div>
            <p className="text-2xl font-bold text-[#525766]">5</p>
            <p className="text-xs text-[#8992A9]">Active Regions</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}


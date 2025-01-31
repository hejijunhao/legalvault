// src/components/profile/billing/billing-usage.tsx

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"

export function BillingUsage() {
  return (
    <Card className="overflow-hidden bg-[rgba(191,219,254,0.20)] backdrop-blur-sm transition-all hover:bg-[rgba(191,219,254,0.30)]">
      <CardHeader>
        <CardTitle className="text-lg font-medium text-[#1C1C1C]">Usage This Month</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-[#1C1C1C]">API Calls</span>
            <span className="font-medium text-[#1C1C1C]">8,542 / 10,000</span>
          </div>
          <Progress value={85} className="h-2" />
        </div>

        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-[#1C1C1C]">Storage</span>
            <span className="font-medium text-[#1C1C1C]">2.1 GB / 5 GB</span>
          </div>
          <Progress value={42} className="h-2" />
        </div>

        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-[#1C1C1C]">Team Members</span>
            <span className="font-medium text-[#1C1C1C]">8 / 10</span>
          </div>
          <Progress value={80} className="h-2" />
        </div>
      </CardContent>
    </Card>
  )
}






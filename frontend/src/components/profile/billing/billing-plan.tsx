// src/components/profile/billing/billing-plan.tsx

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Check } from "lucide-react"

export function BillingPlan() {
  return (
    <Card className="overflow-hidden bg-[rgba(191,219,254,0.20)] backdrop-blur-sm transition-all hover:bg-[rgba(191,219,254,0.30)]">
      <CardHeader>
        <CardTitle className="text-lg font-medium text-[#1C1C1C]">Current Plan</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div>
          <div className="mb-2 text-2xl font-bold text-[#1C1C1C]">Professional</div>
          <div className="text-sm text-[#1C1C1C]">$99/month</div>
        </div>

        <div className="space-y-2">
          <div className="flex items-center gap-2 text-sm">
            <Check className="h-4 w-4 text-[#9FE870]" />
            <span className="text-[#1C1C1C]">10,000 API calls/month</span>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <Check className="h-4 w-4 text-[#9FE870]" />
            <span className="text-[#1C1C1C]">5 GB storage</span>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <Check className="h-4 w-4 text-[#9FE870]" />
            <span className="text-[#1C1C1C]">Up to 10 team members</span>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <Check className="h-4 w-4 text-[#9FE870]" />
            <span className="text-[#1C1C1C]">Priority support</span>
          </div>
        </div>

        <Button variant="outline" className="w-full border-[#1C1C1C] bg-white/50 text-[#1C1C1C] hover:bg-white/80">
          Upgrade Plan
        </Button>
      </CardContent>
    </Card>
  )
}




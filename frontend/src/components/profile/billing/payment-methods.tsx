// src/components/profile/billing/payment-methods.tsx

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { CreditCard, Plus } from "lucide-react"

const paymentMethods = [
  {
    id: 1,
    type: "Visa",
    last4: "4242",
    expiry: "12/24",
    isDefault: true,
  },
  {
    id: 2,
    type: "Mastercard",
    last4: "8888",
    expiry: "06/25",
    isDefault: false,
  },
]

export function PaymentMethods() {
  return (
    <Card className="overflow-hidden bg-[rgba(191,219,254,0.20)] backdrop-blur-sm transition-all hover:bg-[rgba(191,219,254,0.30)]">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-lg font-medium text-[#1C1C1C]">Payment Methods</CardTitle>
        <Button
          variant="outline"
          size="sm"
          className="gap-2 border-[#1C1C1C] bg-white/50 text-[#1C1C1C] hover:bg-white/80"
        >
          <Plus className="h-4 w-4" />
          Add New
        </Button>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {paymentMethods.map((method) => (
            <div
              key={method.id}
              className="flex items-center justify-between rounded-lg border border-white/20 bg-white/30 p-4 backdrop-blur-sm transition-all hover:bg-white/40"
            >
              <div className="flex items-center gap-4">
                <CreditCard className="h-6 w-6 text-[#1C1C1C]" />
                <div>
                  <div className="font-medium text-[#1C1C1C]">
                    {method.type} ending in {method.last4}
                  </div>
                  <div className="text-sm text-[#1C1C1C]">Expires {method.expiry}</div>
                </div>
              </div>
              {method.isDefault && (
                <span className="rounded-full bg-[#9FE870]/20 px-2.5 py-0.5 text-xs text-[#09332B]">Default</span>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}



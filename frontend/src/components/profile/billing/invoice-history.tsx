// src/components/profile/billing/invoice-history.tsx

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Download } from "lucide-react"

const invoices = [
  {
    id: "INV-2024-001",
    date: "Jan 1, 2024",
    amount: "$99.00",
    status: "Paid",
  },
  {
    id: "INV-2023-012",
    date: "Dec 1, 2023",
    amount: "$99.00",
    status: "Paid",
  },
  {
    id: "INV-2023-011",
    date: "Nov 1, 2023",
    amount: "$99.00",
    status: "Paid",
  },
]

export function InvoiceHistory() {
  return (
    <Card className="overflow-hidden bg-[rgba(191,219,254,0.20)] backdrop-blur-sm transition-all hover:bg-[rgba(191,219,254,0.30)]">
      <CardHeader>
        <CardTitle className="text-lg font-medium text-[#1C1C1C]">Invoice History</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {invoices.map((invoice) => (
            <div
              key={invoice.id}
              className="flex items-center justify-between rounded-lg border border-white/20 bg-white/30 p-4 backdrop-blur-sm transition-all hover:bg-white/40"
            >
              <div>
                <div className="font-medium text-[#1C1C1C]">{invoice.id}</div>
                <div className="text-sm text-[#1C1C1C]">{invoice.date}</div>
              </div>
              <div className="flex items-center gap-4">
                <div className="text-right">
                  <div className="font-medium text-[#1C1C1C]">{invoice.amount}</div>
                  <div className="text-sm text-[#1C1C1C]">{invoice.status}</div>
                </div>
                <Button variant="ghost" size="icon" className="h-8 w-8 hover:bg-white/50">
                  <Download className="h-4 w-4 text-[#1C1C1C]" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}





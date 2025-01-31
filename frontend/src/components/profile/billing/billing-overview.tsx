// src/components/profile/billing/billing-overview.tsx

import { BillingUsage } from "./billing-usage"
import { PaymentMethods } from "./payment-methods"
import { InvoiceHistory } from "./invoice-history"
import { BillingPlan } from "./billing-plan"

export function BillingOverview() {
  return (
    <div className="grid gap-6">
      <div className="grid gap-6 md:grid-cols-[2fr,1fr]">
        <BillingUsage />
        <BillingPlan />
      </div>
      <PaymentMethods />
      <InvoiceHistory />
    </div>
  )
}


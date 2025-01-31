// src/app/(app)/profile/billing/pages.tsx

import { BillingOverview } from "@/components/profile/billing/billing-overview"

export default function BillingPage() {
  return (
    <div className="mx-auto max-w-[1440px] px-4 py-6">
      <h1 className="mb-6 text-[32px] font-normal italic leading-6 text-[#111827] font-['Libre_Baskerville']">
        Billing Overview
      </h1>
      <BillingOverview />
    </div>
  )
}


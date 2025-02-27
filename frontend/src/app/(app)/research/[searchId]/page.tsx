// src/app/(app)/research/[searchId]/page.tsx

"use client"

import { useParams } from "next/navigation"
import { ResearchHeader } from "@/components/research/search/research-header"
import { SearchActions } from "@/components/research/search/search-actions"
import { ResearchInput } from "@/components/research/search/research-input"
import { BackButton } from "@/components/ui/back-button"
import { UserMessages } from "@/components/research/search/user-messages"

// Mock data - replace with actual data fetching in production
const mockSearchData = {
  query: "partial offers of publicly listed companies made in Singapore in the past 5 years",
  content: `In the past 5 years, there have been notable partial offers for publicly listed companies in Singapore. One significant example is the voluntary pre-conditional cash partial offer made by Kyanite Investment Holdings Pte. Ltd., a subsidiary of Temasek Holdings, for 30.55% of Keppel Corporation Limited's shares in October 2019.

Key details of this partial offer include:

1. Offer price: S$7.35 per share, representing a premium of approximately 26% over the last traded price and 21% over the three-month volume weighted average price.

2. Objective: To increase Temasek's ownership in Keppel from 20.45% to 51% without delisting the company.

3. Conditions: The offer was subject to pre-conditions, including obtaining domestic and foreign regulatory approvals.

Partial offers in Singapore are governed by the Takeover Code and require approval from the Securities Industry Council (SIC). The SIC generally grants consent for partial offers that do not result in the bidder and its concert parties holding more than 30% of the target company's voting rights.

It's important to note that partial offers are less common than full takeover offers or schemes of arrangement in Singapore's M&A landscape. The Keppel-Temasek partial offer stands out as a significant example in recent years, but comprehensive data on all partial offers in the past 5 years is not readily available in the provided search results.`,
}

// Mock conversation data
const mockMessages = [
  {
    id: "1",
    content: "Can you tell me about partial offers of publicly listed companies made in Singapore in the past 5 years?",
    sender: "user",
    timestamp: new Date(Date.now() - 120000), // 2 minutes ago
  },
  {
    id: "2",
    content: mockSearchData.content,
    sender: "assistant",
    timestamp: new Date(Date.now() - 60000), // 1 minute ago
  },
]

export default function ResearchPage() {
  const params = useParams()
  const searchId = params.searchId as string

  return (
    <div className="min-h-screen pb-20">
      <div className="mx-auto max-w-[1440px] px-4">
        <div className="flex items-center pt-6">
          <BackButton customText="Back to Research" />
        </div>

        <div className="mx-auto max-w-3xl">
          <ResearchHeader query={mockSearchData.query} />
          <SearchActions />
          <UserMessages messages={mockMessages} />
        </div>
      </div>
      <ResearchInput />
    </div>
  )
}




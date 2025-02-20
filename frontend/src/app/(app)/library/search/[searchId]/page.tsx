// src/app/(app)/library/search/[searchId]/page.tsx

"use client"

// import { useParams } from "next/navigation"
import { BackButton } from "@/components/ui/back-button"
import { SearchTags } from "@/components/library/search/search-tags"
import { SearchResultsBlock } from "@/components/library/search/search-results-block"
import { SourcesBlock } from "@/components/library/search/sources-block"
import { FollowUpSearch } from "@/components/library/search/follow-up-search"
import { cn } from "@/lib/utils"

// Mock search data - this would come from your backend in production
const mockSearchData = {
  query: "Employment and labour laws in Singapore",
  metadata: [
    { id: "client", label: "ClientName", value: "Acme Corp" },
    { id: "collection", label: "Collection", value: "Employment Law" },
    { id: "workspace", label: "Workspace", value: "Legal Research" },
    { id: "type", label: "DocumentType", value: "Research Note" },
    { id: "source", label: "Source", value: "LexisNexis" },
    { id: "date", label: "Date", value: "01.01.2022 - present" },
  ],
  summary: {
    introduction:
      "Singapore's employment and labour laws are primarily governed by the Employment Act (EA), which provides basic protections and sets minimum standards for working conditions. As of February 2025, the following key aspects of Singapore's employment laws are in effect:",
    sections: [
      {
        title: "Coverage and Scope",
        content:
          "The Employment Act covers most employees in Singapore, with a few exceptions such as seafarers, domestic workers, and civil servants. It applies to:",
      },
      {
        title: "",
        content: [
          "Employees working under a contract of service (written or verbal)",
          "Workers employed entirely or partially in Singapore",
          "Manual labourers earning a basic monthly salary of up to S$4,500",
          "Non-manual workers earning a basic monthly salary of up to S$2,600",
        ],
      },
      {
        title: "Key Provisions",
        content: "Working Hours and Leave",
      },
      {
        title: "",
        content: [
          "Standard working hours: 9 hours per day or 44 hours per week",
          "Minimum annual leave: 7 days after 3 months of service, increasing by 1 day per year of service up to 14 days",
        ],
      },
    ],
  },
  sources: [
    {
      id: "1",
      title: "Employment Act (Chapter 91)",
      type: "Legislative Document",
      date: "Last amended Feb 2024",
      url: "https://sso.agc.gov.sg/Act/EmA1968",
      fileSize: "2.3 MB",
      lastModified: "15 Feb 2024",
      creator: "Singapore Government",
    },
    {
      id: "2",
      title: "Ministry of Manpower Guidelines",
      type: "Government Publication",
      date: "Updated Jan 2024",
      url: "https://www.mom.gov.sg/employment-practices",
      fileSize: "1.8 MB",
      lastModified: "31 Jan 2024",
      creator: "Ministry of Manpower",
    },
    {
      id: "3",
      title: "Employment Claims Tribunals Practice Directions",
      type: "Legal Reference",
      date: "2023 Edition",
      url: "https://www.statecourts.gov.sg/cws/ECT/Pages/Legislation-and-Directions.aspx",
      fileSize: "3.5 MB",
      lastModified: "01 Dec 2023",
      creator: "State Courts of Singapore",
    },
    {
      id: "4",
      title: "Workplace Safety and Health Act",
      type: "Legislative Document",
      date: "Last amended Dec 2023",
      url: "https://sso.agc.gov.sg/Act/WSHA2006",
      fileSize: "1.9 MB",
      lastModified: "30 Dec 2023",
      creator: "Singapore Government",
    },
  ], // Will be populated in the next iteration
}

export default function SearchPage() {
  // const params = useParams()
  // const searchId = params.searchId as string

  return (
    <div className="min-h-screen pb-20">
      <div className="mx-auto max-w-[1440px] px-4 py-6">
        {/* Header row with back button and title */}
        <div className="mb-8 flex items-center justify-between">
          {/* Back Navigation */}
          <BackButton />

          {/* Title and Metadata Container */}
          <div className="flex flex-1 flex-col items-center">
            <h1
              className={cn(
                "text-[32px] font-normal italic leading-normal text-[#111827]",
                "font-['Libre_Baskerville']",
              )}
            >
              {mockSearchData.query}
            </h1>

            {/* Metadata Tags */}
            <div className="mt-4 flex flex-wrap justify-center gap-2">
              <SearchTags metadata={mockSearchData.metadata} />
            </div>
          </div>

          {/* Empty div to balance the layout */}
          <div className="w-[100px]" />
        </div>

        {/* Search Results Grid */}
        <div className="grid grid-cols-[2fr,1fr] gap-6">
          <SearchResultsBlock content={mockSearchData.summary} />
          <SourcesBlock sources={mockSearchData.sources} />
        </div>
      </div>

      {/* Follow-up Search Bar */}
      <FollowUpSearch />
    </div>
  )
}


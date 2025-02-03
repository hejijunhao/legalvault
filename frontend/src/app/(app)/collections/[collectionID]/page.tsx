// src/app/(app)/collections/[collectionID]/page.tsx

"use client"

import { useRef, createRef } from "react"
import Link from "next/link"
import { ChevronRight, FileText, Clock } from "lucide-react"
import { SectionIndexer } from "@/components/collections/section-indexer"
import { useSectionObserver } from "@/hooks/collections/use-section-observer"
import type { RefObject } from "react"

// Mock data for the collection
const collectionData = {
  id: "1",
  name: "M&A Templates",
  description:
    "A comprehensive collection of merger and acquisition templates, including term sheets, due diligence checklists, and closing documents.",
  documentCount: 156,
  lastUpdated: "2 days ago",
}

// Define section types
interface BaseSection {
  id: string
  title: string
}

interface SectionWithRef extends BaseSection {
  ref: RefObject<HTMLDivElement | null>
}

// Define the sections array
const SECTIONS: BaseSection[] = [
  { id: "confidentiality", title: "Confidentiality Clauses" },
  { id: "representations", title: "Representations & Warranties" },
  { id: "conditions", title: "Conditions Precedent" },
  { id: "covenants", title: "Covenants" },
  { id: "indemnification", title: "Indemnification" },
  { id: "termination", title: "Termination Rights" },
  { id: "miscellaneous", title: "Miscellaneous Provisions" },
]

export default function CollectionPage() {
  // Create a ref for each section at the component level
  const sectionRefs = useRef<{ [key: string]: RefObject<HTMLDivElement | null> }>(
    Object.fromEntries(
      SECTIONS.map((section) => [
        section.id,
        createRef<HTMLDivElement>()
      ])
    )
  )

  // Create sections with refs
  const sectionsWithRefs: SectionWithRef[] = SECTIONS.map((section) => ({
    ...section,
    ref: sectionRefs.current[section.id],
  }))

  // Calculate the offset based on the header height plus some padding
  const HEADER_OFFSET = 100 // Adjust this value based on your header height

  // Use the section observer hook with the calculated offset
  const { currentSectionId, scrollToSection } = useSectionObserver(sectionsWithRefs, HEADER_OFFSET)

  return (
    <div className="min-h-screen">
      {/* Header content aligned with main header */}
      <div className="mx-auto max-w-[1440px] px-4">
        {/* Breadcrumb */}
        <nav className="mb-4 flex items-center space-x-2 text-sm text-gray-500">
          <Link href="/collections" className="hover:text-gray-700">
            Collections
          </Link>
          <ChevronRight className="h-4 w-4" />
          <span className="text-gray-700">{collectionData.name}</span>
        </nav>

        {/* Collection Header */}
        <div className="mb-12">
          <h1 className="mb-2 text-3xl font-bold text-gray-900">{collectionData.name}</h1>
          <p className="mb-4 text-lg text-gray-600">{collectionData.description}</p>
          <div className="flex items-center space-x-4 text-sm text-gray-500">
            <div className="flex items-center">
              <FileText className="mr-2 h-4 w-4" />
              <span>{collectionData.documentCount} documents</span>
            </div>
            <div className="flex items-center">
              <Clock className="mr-2 h-4 w-4" />
              <span>Last updated {collectionData.lastUpdated}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Two-column layout for section indexer and content */}
      <div className="relative mx-auto max-w-[1440px] px-4">
        <div className="grid grid-cols-[200px_1fr] gap-8">
          {/* Section Indexer */}
          <div className="relative">
            <div className="sticky top-[100px] max-h-[calc(100vh-100px)] overflow-y-auto">
              <SectionIndexer
                sections={sectionsWithRefs}
                currentSectionId={currentSectionId}
                onSectionClick={scrollToSection}
              />
            </div>
          </div>

          {/* Section Content */}
          <div className="space-y-24 pb-24">
            {sectionsWithRefs.map((section) => (
              <div
                key={section.id}
                id={section.id}
                ref={section.ref}
                className="min-h-[400px] rounded-xl border border-white/20 bg-white/60 p-6 backdrop-blur-sm"
              >
                <h2 className="text-2xl font-semibold text-gray-900">{section.title}</h2>
                <p className="mt-4 text-gray-600">Content for {section.title} will be displayed here.</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}












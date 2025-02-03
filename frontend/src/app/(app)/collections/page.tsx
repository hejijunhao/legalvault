// src/app/(app)/collections/page.tsx

import { CollectionsGrid } from "@/components/collections/collections-grid"
import { FeaturedCollection } from "@/components/collections/featured-collection"
import { CollectionsNav } from "@/components/collections/collections-nav"
import Link from "next/link"
import { ChevronLeft } from "lucide-react"

export default function CollectionsPage() {
  return (
    <div className="min-h-screen">
      <div className="mx-auto max-w-[1440px] px-4 py-6">
        <div className="mb-6">
          <Link
            href="/library"
            className="mb-4 inline-flex items-center text-sm text-[#525766] hover:text-[#1C1C1C] transition-colors"
          >
            <ChevronLeft className="mr-1 h-4 w-4" />
            Back to Library
          </Link>
          <h1 className="text-[32px] font-normal italic leading-6 text-[#111827] font-['Libre_Baskerville']">
            Collections
          </h1>
          <p className="mt-2 text-[#525766]">Browse and access your document collections</p>
        </div>

        <CollectionsNav />
        <FeaturedCollection />
        <CollectionsGrid />
      </div>
    </div>
  )
}


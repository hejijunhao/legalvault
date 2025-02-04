// src/app/(app)/library/page.tsx

import { SearchBar } from "@/components/library/search-bar"
import { CollapsibleBlock } from "@/components/library/blocks/collapsible-block"
import { LibrarianBlock } from "@/components/library/blocks/librarian-block"
import { HighlightsBlock } from "@/components/library/blocks/highlights-block"
import { TypeCategories } from "@/components/library/type-categories"
import { InformationCategories } from "@/components/library/information-categories"
import { collectionsData, bookmarksData, subscriptionsData, sourcesData } from "@/components/library/blocks/block-data"

export default function LibraryPage() {
  return (
    <div className="py-6">
      <SearchBar />
      <div className="mx-auto mt-6 max-w-[1440px] px-4">
        <div className="flex gap-6">
          {/* Left column - Collapsible blocks */}
          <div className="w-[380px] flex-shrink-0 space-y-3">
            <CollapsibleBlock {...collectionsData} viewAllLink="/collections" />
            <CollapsibleBlock {...bookmarksData} />
            <CollapsibleBlock {...subscriptionsData} />
            <CollapsibleBlock {...sourcesData} />
            <LibrarianBlock />
          </div>

          {/* Right column - Highlights, Types, and Categories */}
          <div className="flex-1 space-y-6">
            <HighlightsBlock />
            <TypeCategories />
            <InformationCategories />
          </div>
        </div>
      </div>
    </div>
  )
}















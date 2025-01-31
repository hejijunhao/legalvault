// src/app/(app)/library/page.tsx

import { SearchBar } from "@/components/library/search-bar"
import { CollapsibleBlock } from "@/components/library/blocks/collapsible-block"
import { LibrarianBlock } from "@/components/library/blocks/librarian-block"
import { collectionsData, bookmarksData, subscriptionsData, sourcesData } from "@/components/library/blocks/block-data"

export default function LibraryPage() {
  return (
    <div className="py-6">
      <SearchBar />
      <div className="mx-auto mt-6 max-w-[1440px] px-4">
        <div className="space-y-3">
          <CollapsibleBlock {...collectionsData} />
          <CollapsibleBlock {...bookmarksData} />
          <CollapsibleBlock {...subscriptionsData} />
          <CollapsibleBlock {...sourcesData} />
          <LibrarianBlock />
        </div>
      </div>
    </div>
  )
}


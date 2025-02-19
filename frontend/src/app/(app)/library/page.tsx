// src/app/(app)/library/page.tsx

import { SearchBar } from "@/components/library/search-bar"
import { TypeCategories } from "@/components/library/type-categories"
import { InformationCategories } from "@/components/library/information-categories"

export default function LibraryPage() {
  return (
    <div className="py-6">
      <SearchBar />
      <div className="mx-auto mt-6 max-w-[1440px] px-4">
        <div className="space-y-6">
          <TypeCategories />
          <InformationCategories />
        </div>
      </div>
    </div>
  )
}















// src/app/(app)/library/page.tsx

import { SearchBar } from "@/components/library/search-bar"
import { LiveProjects } from "@/components/library/live-projects"
import { Collections } from "@/components/library/collections"
import { RecentUpdates } from "@/components/library/recent-updates"
import { Launchpad } from "@/components/library/launchpad"

export default function LibraryPage() {
  return (
    <div className="space-y-8 py-6">
      <SearchBar />
      <div className="grid gap-8 lg:grid-cols-[1fr,320px]">
        <div className="space-y-8">
          <LiveProjects />
          <Collections />
        </div>
        <div className="space-y-8">
          <RecentUpdates />
          <Launchpad />
        </div>
      </div>
    </div>
  )
}
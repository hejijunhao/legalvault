// src/components/research/search/search-actions.tsx

import { Bookmark, Share2, FolderPlus } from "lucide-react"

export function SearchActions() {
  return (
    <div className="mb-6 flex justify-center gap-2">
      <button className="flex items-center gap-[6px] rounded-[12px] bg-[rgba(137,146,169,0.30)] px-2 py-1">
        <Bookmark className="h-4 w-4" />
        <span className="text-sm text-[#1C1C1C]">Bookmark</span>
      </button>
      <button className="flex items-center gap-[6px] rounded-[12px] bg-[rgba(137,146,169,0.30)] px-2 py-1">
        <FolderPlus className="h-4 w-4" />
        <span className="text-sm text-[#1C1C1C]">Add to Workspace</span>
      </button>
      <button className="flex items-center gap-[6px] rounded-[12px] bg-[rgba(137,146,169,0.30)] px-2 py-1">
        <Share2 className="h-4 w-4" />
        <span className="text-sm text-[#1C1C1C]">Share</span>
      </button>
    </div>
  )
}


// src/components/research/search/search-actions.tsx

"use client"

import { useState } from "react"
import { Bookmark, Share2, FolderPlus, FileText } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"

// Mock citation data - in a real app, this would come from props or context
const mockCitations = [
  {
    id: "1",
    title: "Singapore Code on Take-overs and Mergers",
    url: "https://www.mas.gov.sg/regulation/codes/code-on-take-overs-and-mergers",
    publisher: "Monetary Authority of Singapore",
    date: "2019",
  },
  {
    id: "2",
    title: "Temasek's Partial Offer for Keppel Corporation",
    url: "https://links.sgx.com/FileOpen/Keppel-Offer%20Announcement.ashx?App=Announcement&FileID=583999",
    publisher: "Singapore Exchange",
    date: "2019",
  },
  {
    id: "3",
    title: "Securities and Futures Act (Chapter 289)",
    url: "https://sso.agc.gov.sg/Act/SFA2001",
    publisher: "Singapore Statutes Online",
    date: "2020",
  },
]

export function SearchActions() {
  const [showCitations, setShowCitations] = useState(false)

  return (
    <div className="mb-6">
      <div className="flex justify-center gap-2">
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
        <button
          className="flex items-center gap-[6px] rounded-[12px] bg-[rgba(159,232,112,0.20)] px-2 py-1 hover:bg-[rgba(159,232,112,0.30)]"
          onClick={() => setShowCitations(!showCitations)}
        >
          <FileText className="h-4 w-4" />
          <span className="text-sm text-[#1C1C1C]">Citations</span>
        </button>
      </div>

      <AnimatePresence>
        {showCitations && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="mt-4 overflow-hidden"
          >
            <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
              <h3 className="mb-3 text-sm font-medium text-gray-700">Sources & Citations</h3>
              <div className="space-y-3">
                {mockCitations.map((citation) => (
                  <div key={citation.id} className="text-sm">
                    <a
                      href={citation.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="font-medium text-blue-600 hover:underline"
                    >
                      {citation.title}
                    </a>
                    <p className="text-xs text-gray-500">
                      {citation.publisher}, {citation.date}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}



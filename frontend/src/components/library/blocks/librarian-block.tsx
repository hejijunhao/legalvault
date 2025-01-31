// src/components/library/blocks/librarian-block.tsx

"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ArrowRight, File, Folder, Clock, Calendar, Users, Bot, ChevronLeft } from "lucide-react"
import Link from "next/link"

interface RecentItem {
  id: string
  type: "file" | "folder"
  name: string
  path: string
  accessedAt: string
  metadata: {
    created: string
    modified: string
    size?: string
    fileCount?: number
    collaborators: string[]
    aiInsights: string
  }
}

const recentItems: RecentItem[] = [
  {
    id: "1",
    type: "file",
    name: "Project Greenbridge - Term Sheet.pdf",
    path: "/documents/term-sheets",
    accessedAt: "2 hours ago",
    metadata: {
      created: "Jan 15, 2024",
      modified: "Jan 30, 2024",
      size: "2.4 MB",
      collaborators: ["Sarah Chen", "Michael Wong"],
      aiInsights:
        "This term sheet outlines key deal terms for Project Greenbridge, including valuation at $50M, 15% equity stake, and standard investor rights. Recent modifications focus on governance structure and vesting schedules.",
    },
  },
  {
    id: "2",
    type: "folder",
    name: "Due Diligence Reports",
    path: "/documents/dd-reports",
    accessedAt: "Yesterday",
    metadata: {
      created: "Dec 1, 2023",
      modified: "Jan 31, 2024",
      fileCount: 24,
      collaborators: ["David Kim", "Emma Thompson"],
      aiInsights:
        "This folder contains comprehensive due diligence reports for ongoing M&A deals. Recent activity shows focus on financial and legal documentation. Most accessed documents relate to regulatory compliance.",
    },
  },
  {
    id: "3",
    type: "file",
    name: "Merger Agreement - Draft v2.docx",
    path: "/documents/agreements",
    accessedAt: "2 days ago",
    metadata: {
      created: "Jan 20, 2024",
      modified: "Jan 29, 2024",
      size: "1.8 MB",
      collaborators: ["Sarah Chen", "Robert McNamara"],
      aiInsights:
        "Second draft of the merger agreement with significant changes to sections 3.4 (Representations) and 5.2 (Covenants). Key updates include revised termination clauses and adjusted consideration structure.",
    },
  },
  {
    id: "4",
    type: "folder",
    name: "Client Correspondence",
    path: "/documents/correspondence",
    accessedAt: "3 days ago",
    metadata: {
      created: "Nov 15, 2023",
      modified: "Jan 31, 2024",
      fileCount: 156,
      collaborators: ["All Team Members"],
      aiInsights:
        "High activity folder with recent focus on Project Greenbridge communications. Notable increase in regulatory inquiry responses and client status update requests.",
    },
  },
  {
    id: "5",
    type: "file",
    name: "Regulatory Compliance Report.pdf",
    path: "/documents/compliance",
    accessedAt: "4 days ago",
    metadata: {
      created: "Jan 10, 2024",
      modified: "Jan 28, 2024",
      size: "5.2 MB",
      collaborators: ["Emma Thompson", "Michael Wong"],
      aiInsights:
        "Comprehensive analysis of regulatory requirements with focus on new ESG compliance standards. Highlights potential areas requiring immediate attention in Q1 2024.",
    },
  },
]

export function LibrarianBlock() {
  const [selectedItem, setSelectedItem] = useState<RecentItem | null>(null)

  return (
    <Card className="w-[380px] overflow-hidden border-white/20 bg-white/90 backdrop-blur-md transition-all duration-500 hover:border-white/30 hover:bg-white/95 hover:shadow-[0_8px_30px_-4px_rgba(0,0,0,0.2)]">
      <AnimatePresence mode="wait">
        {selectedItem ? (
          <motion.div
            key="details"
            initial={{ opacity: 0, x: 300 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -300 }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="p-4"
          >
            {/* Header */}
            <div className="mb-4">
              <Button
                variant="ghost"
                size="sm"
                className="mb-2 -ml-2 gap-2 text-[#525766] hover:text-[#1c1c1c]"
                onClick={() => setSelectedItem(null)}
              >
                <ChevronLeft className="h-4 w-4" />
                Back
              </Button>
              <div className="flex items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-[#F3F4F6]">
                  {selectedItem.type === "file" ? (
                    <File className="h-6 w-6 text-[#525766]" />
                  ) : (
                    <Folder className="h-6 w-6 text-[#525766]" />
                  )}
                </div>
                <div>
                  <h3 className="text-sm font-medium text-[#1c1c1c] line-clamp-1">{selectedItem.name}</h3>
                  <p className="text-xs text-[#8992a9]">{selectedItem.path}</p>
                </div>
              </div>
            </div>

            {/* Metadata */}
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-lg bg-[#F3F4F6] p-3">
                  <div className="flex items-center gap-2 text-xs text-[#525766]">
                    <Calendar className="h-4 w-4" />
                    Created
                  </div>
                  <p className="mt-1 text-sm font-medium text-[#1c1c1c]">{selectedItem.metadata.created}</p>
                </div>
                <div className="rounded-lg bg-[#F3F4F6] p-3">
                  <div className="flex items-center gap-2 text-xs text-[#525766]">
                    <Clock className="h-4 w-4" />
                    Modified
                  </div>
                  <p className="mt-1 text-sm font-medium text-[#1c1c1c]">{selectedItem.metadata.modified}</p>
                </div>
              </div>

              {selectedItem.type === "file" ? (
                <div className="rounded-lg bg-[#F3F4F6] p-3">
                  <div className="flex items-center gap-2 text-xs text-[#525766]">Size</div>
                  <p className="mt-1 text-sm font-medium text-[#1c1c1c]">{selectedItem.metadata.size}</p>
                </div>
              ) : (
                <div className="rounded-lg bg-[#F3F4F6] p-3">
                  <div className="flex items-center gap-2 text-xs text-[#525766]">Files</div>
                  <p className="mt-1 text-sm font-medium text-[#1c1c1c]">{selectedItem.metadata.fileCount} items</p>
                </div>
              )}

              <div className="rounded-lg bg-[#F3F4F6] p-3">
                <div className="flex items-center gap-2 text-xs text-[#525766]">
                  <Users className="h-4 w-4" />
                  Collaborators
                </div>
                <p className="mt-1 text-sm font-medium text-[#1c1c1c]">
                  {selectedItem.metadata.collaborators.join(", ")}
                </p>
              </div>

              <div className="rounded-lg bg-[#bfdbfe]/20 p-3">
                <div className="mb-2 flex items-center gap-2 text-xs text-[#525766]">
                  <Bot className="h-4 w-4" />
                  AI Insights
                </div>
                <p className="text-sm text-[#1c1c1c]">{selectedItem.metadata.aiInsights}</p>
              </div>
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="list"
            initial={{ opacity: 0, x: -300 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 300 }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="p-4"
          >
            {/* Header */}
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h3 className="text-sm font-medium text-[#1C1C1C]">Recently Accessed</h3>
                <p className="text-xs text-[#8992A9]">Your most frequently used items</p>
              </div>
            </div>

            {/* Items List */}
            <div className="space-y-1">
              {recentItems.map((item, index) => (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1, duration: 0.5 }}
                  className="group flex cursor-pointer items-center justify-between rounded-lg p-3 transition-all duration-300 hover:bg-white"
                  onClick={() => setSelectedItem(item)}
                >
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-[#F3F4F6] transition-all duration-300 group-hover:bg-[#E5E7EB]">
                      {item.type === "file" ? (
                        <File className="h-5 w-5 text-[#525766]" />
                      ) : (
                        <Folder className="h-5 w-5 text-[#525766]" />
                      )}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-[#1C1C1C] line-clamp-1">{item.name}</p>
                      <p className="text-xs text-[#8992A9]">{item.accessedAt}</p>
                    </div>
                  </div>
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: index * 0.1 + 0.3 }}
                  >
                    <ArrowRight className="h-4 w-4 text-[#525766] opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
                  </motion.div>
                </motion.div>
              ))}
            </div>

            {/* View Archives Button */}
            <Link href="/library/archives" className="mt-4 block">
              <Button
                variant="ghost"
                className="relative w-full rounded-lg bg-[#F3F4F6] py-6 text-[#1C1C1C] transition-all duration-300 hover:bg-[#E5E7EB]"
              >
                <span className="absolute inset-0 flex items-center justify-center">View Archives</span>
                <ArrowRight className="absolute right-4 h-4 w-4 opacity-50" />
              </Button>
            </Link>
          </motion.div>
        )}
      </AnimatePresence>
    </Card>
  )
}




// src/app/(app)/library/[fileType]/page.tsx

"use client"

import { useState } from "react"
import { useParams } from "next/navigation"
import Link from "next/link"
import { motion } from "framer-motion"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { FileList } from "@/components/library/file-list"
import { Search, ChevronLeft } from "lucide-react"

// Mock data for demonstration
const fileTypes = {
  documents: {
    title: "Documents",
    description: "Browse and manage document files",
    categories: [
      {
        name: "Contracts",
        files: [
          { id: "1", name: "Service Agreement - TechCorp", type: "pdf", lastModified: "2023-05-15" },
          { id: "2", name: "NDA - Project Alpha", type: "docx", lastModified: "2023-06-02" },
          { id: "3", name: "Employment Contract - John Doe", type: "pdf", lastModified: "2023-06-10" },
          { id: "4", name: "Vendor Agreement - SupplyCo", type: "pdf", lastModified: "2023-06-20" },
          { id: "5", name: "Lease Agreement - Office Space", type: "docx", lastModified: "2023-07-01" },
          { id: "6", name: "Consulting Agreement - Jane Smith", type: "pdf", lastModified: "2023-07-05" },
          { id: "7", name: "Partnership Agreement - NewVenture", type: "pdf", lastModified: "2023-07-10" },
          { id: "8", name: "Sales Contract - BigClient", type: "docx", lastModified: "2023-07-15" },
        ],
      },
      {
        name: "Agreements",
        files: [
          { id: "9", name: "Partnership Agreement - XYZ Inc", type: "pdf", lastModified: "2023-05-20" },
          { id: "10", name: "Licensing Agreement - Software A", type: "docx", lastModified: "2023-06-05" },
          { id: "11", name: "Joint Venture Agreement - Project Beta", type: "pdf", lastModified: "2023-06-25" },
          { id: "12", name: "Distribution Agreement - ProductX", type: "docx", lastModified: "2023-07-03" },
          { id: "13", name: "Franchise Agreement - BrandY", type: "pdf", lastModified: "2023-07-08" },
          { id: "14", name: "Subscription Agreement - ServiceZ", type: "pdf", lastModified: "2023-07-12" },
          { id: "15", name: "Confidentiality Agreement - Project Gamma", type: "docx", lastModified: "2023-07-18" },
        ],
      },
      {
        name: "Research",
        files: [
          { id: "16", name: "Market Analysis Q2 2023", type: "pdf", lastModified: "2023-06-15" },
          { id: "17", name: "Competitor Research", type: "docx", lastModified: "2023-06-18" },
          { id: "18", name: "Industry Trends Report", type: "pdf", lastModified: "2023-06-30" },
          { id: "19", name: "Customer Survey Results", type: "xlsx", lastModified: "2023-07-05" },
          { id: "20", name: "Product Development Roadmap", type: "pptx", lastModified: "2023-07-10" },
          { id: "21", name: "Financial Projections 2023-2025", type: "xlsx", lastModified: "2023-07-15" },
          { id: "22", name: "SWOT Analysis - Company X", type: "pdf", lastModified: "2023-07-20" },
        ],
      },
      {
        name: "Legal Memos",
        files: [
          { id: "23", name: "Intellectual Property Rights", type: "pdf", lastModified: "2023-06-01" },
          { id: "24", name: "Merger Compliance Guidelines", type: "docx", lastModified: "2023-06-10" },
          { id: "25", name: "Data Privacy Regulations", type: "pdf", lastModified: "2023-06-20" },
          { id: "26", name: "Employment Law Update", type: "pdf", lastModified: "2023-07-01" },
          { id: "27", name: "Corporate Governance Best Practices", type: "docx", lastModified: "2023-07-10" },
          { id: "28", name: "Antitrust Compliance Memo", type: "pdf", lastModified: "2023-07-15" },
          { id: "29", name: "International Trade Regulations", type: "pdf", lastModified: "2023-07-20" },
        ],
      },
      {
        name: "Reports",
        files: [
          { id: "30", name: "Annual Report 2022", type: "pdf", lastModified: "2023-03-15" },
          { id: "31", name: "Q1 2023 Financial Report", type: "xlsx", lastModified: "2023-04-20" },
          { id: "32", name: "Environmental Impact Assessment", type: "pdf", lastModified: "2023-05-10" },
          { id: "33", name: "HR Diversity Report", type: "pptx", lastModified: "2023-06-01" },
          { id: "34", name: "IT Security Audit Report", type: "pdf", lastModified: "2023-06-15" },
          { id: "35", name: "Customer Satisfaction Survey Results", type: "xlsx", lastModified: "2023-07-01" },
          { id: "36", name: "Project Alpha Progress Report", type: "pdf", lastModified: "2023-07-10" },
          { id: "37", name: "Supply Chain Optimization Study", type: "pdf", lastModified: "2023-07-20" },
        ],
      },
    ],
  },
  // Add more file types here as needed
}

export default function FileTypePage() {
  const { fileType } = useParams()
  const [searchQuery, setSearchQuery] = useState("")

  const typeData = fileTypes[fileType as keyof typeof fileTypes]

  if (!typeData) {
    return <div>File type not found</div>
  }

  const filteredCategories = typeData.categories
    .map((category) => ({
      ...category,
      files: category.files.filter((file) => file.name.toLowerCase().includes(searchQuery.toLowerCase())),
    }))
    .filter((category) => category.files.length > 0)

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="min-h-screen" // Removed background gradient
    >
      <div className="mx-auto max-w-[1440px] px-4 py-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-6"
        >
          <Link
            href="/library"
            className="mb-4 inline-flex items-center text-sm text-neutral-400 transition-colors hover:text-neutral-900"
          >
            <ChevronLeft className="mr-1 h-4 w-4" />
            Back to Library
          </Link>
          <h1 className="text-[32px] font-normal italic leading-6 text-neutral-900 font-['Libre_Baskerville']">
            {typeData.title}
          </h1>
          <p className="mt-2 text-neutral-500">{typeData.description}</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="relative mb-8"
        >
          <div className="relative">
            <Search className="absolute left-6 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-400" />
            <Input
              type="text"
              placeholder="Search files..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="h-12 border-transparent bg-white/50 pl-12 text-base text-neutral-900 ring-offset-transparent transition-all duration-300 placeholder:text-neutral-400 focus:border-neutral-200 focus:bg-white focus:ring-neutral-200 focus:ring-offset-2"
            />
          </div>
        </motion.div>

        <ScrollArea className="h-[calc(100vh-250px)]">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="space-y-12"
          >
            {filteredCategories.map((category, index) => (
              <motion.div
                key={category.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.1 * index }}
              >
                <h2 className="mb-4 text-sm font-medium uppercase tracking-wide text-neutral-400">{category.name}</h2>
                <FileList files={category.files} />
              </motion.div>
            ))}
          </motion.div>
        </ScrollArea>
      </div>
    </motion.div>
  )
}


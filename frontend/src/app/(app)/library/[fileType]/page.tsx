// src/app/(app)/library/[fileType]/page.tsx

"use client"

import { useState } from "react"
import { useParams } from "next/navigation"
import Link from "next/link"
import { motion } from "framer-motion"
import { Input } from "@/components/ui/input"
import { Search, ChevronLeft } from "lucide-react"
import { FileFinder } from "@/components/library/file-finder"

// Mock data for demonstration
const fileTypes = {
  documents: {
    title: "Documents",
    description: "Browse and manage document files",
    files: [
      {
        id: "1",
        name: "Service Agreement - TechCorp",
        type: "pdf",
        lastModified: "2023-05-15",
        size: "2.4 MB",
        creator: "John Smith",
        collaborators: ["Sarah Chen", "Michael Wong"],
        tags: ["Agreement", "TechCorp", "Service"],
        linkedFiles: ["Meeting Notes - TechCorp", "Previous Version"],
        version: "1.2",
        accessLevel: "Full",
        comments: 5,
        aiInsights:
          "This document contains standard service agreement terms with custom modifications in sections 3.4 and 5.2. Recent changes focus on liability caps and service level definitions.",
        category: "Agreements",
        collection: "Service Contracts",
      },
      {
        id: "2",
        name: "NDA - Project Alpha",
        type: "docx",
        lastModified: "2023-06-02",
        size: "1.1 MB",
        creator: "Jane Doe",
        collaborators: ["David Lee"],
        tags: ["NDA", "Project Alpha", "Confidential"],
        linkedFiles: [],
        version: "1.0",
        accessLevel: "Full",
        comments: 0,
        aiInsights: "This is a standard non-disclosure agreement.",
        category: "Legal",
        collection: "Project Documents",
      },
      {
        id: "3",
        name: "Employment Contract - John Doe",
        type: "pdf",
        lastModified: "2023-06-10",
        size: "3.5 MB",
        creator: "HR Department",
        collaborators: ["John Doe"],
        tags: ["Employment", "Contract", "John Doe"],
        linkedFiles: [],
        version: "1.0",
        accessLevel: "Full",
        comments: 2,
        aiInsights: "This document outlines the terms of employment for John Doe.",
        category: "HR",
        collection: "Employee Contracts",
      },
      {
        id: "4",
        name: "Vendor Agreement - SupplyCo",
        type: "pdf",
        lastModified: "2023-06-20",
        size: "1.8 MB",
        creator: "Procurement Department",
        collaborators: ["SupplyCo"],
        tags: ["Vendor", "Agreement", "SupplyCo"],
        linkedFiles: [],
        version: "1.1",
        accessLevel: "Full",
        comments: 1,
        aiInsights: "This agreement outlines the terms of service with SupplyCo.",
        category: "Agreements",
        collection: "Vendor Contracts",
      },
      {
        id: "5",
        name: "Lease Agreement - Office Space",
        type: "docx",
        lastModified: "2023-07-01",
        size: "2.1 MB",
        creator: "Real Estate",
        collaborators: ["Landlord"],
        tags: ["Lease", "Agreement", "Office Space"],
        linkedFiles: [],
        version: "2.0",
        accessLevel: "Full",
        comments: 0,
        aiInsights: "This document outlines the terms of the office space lease.",
        category: "Legal",
        collection: "Real Estate",
      },
      {
        id: "6",
        name: "Consulting Agreement - Jane Smith",
        type: "pdf",
        lastModified: "2023-07-05",
        size: "1.5 MB",
        creator: "Jane Smith",
        collaborators: ["Project Manager"],
        tags: ["Consulting", "Agreement", "Jane Smith"],
        linkedFiles: [],
        version: "1.0",
        accessLevel: "Full",
        comments: 3,
        aiInsights: "This agreement outlines the terms of the consulting engagement with Jane Smith.",
        category: "Agreements",
        collection: "Consulting Contracts",
      },
      {
        id: "7",
        name: "Partnership Agreement - NewVenture",
        type: "pdf",
        lastModified: "2023-07-10",
        size: "2.9 MB",
        creator: "Legal Department",
        collaborators: ["NewVenture"],
        tags: ["Partnership", "Agreement", "NewVenture"],
        linkedFiles: [],
        version: "1.0",
        accessLevel: "Full",
        comments: 0,
        aiInsights: "This document outlines the terms of the partnership with NewVenture.",
        category: "Legal",
        collection: "Partnership Agreements",
      },
      {
        id: "8",
        name: "Sales Contract - BigClient",
        type: "docx",
        lastModified: "2023-07-15",
        size: "3.2 MB",
        creator: "Sales Department",
        collaborators: ["BigClient"],
        tags: ["Sales", "Contract", "BigClient"],
        linkedFiles: [],
        version: "1.0",
        accessLevel: "Full",
        comments: 4,
        aiInsights: "This document outlines the terms of the sales contract with BigClient.",
        category: "Sales",
        collection: "Sales Contracts",
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

  const filteredFiles = typeData.files.filter((file) => file.name.toLowerCase().includes(searchQuery.toLowerCase()))

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="min-h-screen">
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

        <FileFinder files={filteredFiles} />
      </div>
    </motion.div>
  )
}




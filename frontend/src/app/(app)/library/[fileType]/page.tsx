// src/app/(app)/library/[fileType]/page.tsx

"use client"

import { useState } from "react"
import { useParams } from "next/navigation"
import Link from "next/link"
import { motion } from "framer-motion"
import { Input } from "@/components/ui/input"
import { Search, ChevronLeft } from "lucide-react"
import { FileFinder } from "@/components/library/file-finder"

const fileTypes = {
  documents: {
    title: "Documents",
    description: "Browse and manage document files",
    files: [
      // Agreements Section
      {
        id: "1",
        name: "Service Agreement - TechCorp",
        type: "pdf",
        lastModified: "2024-01-15",
        size: "2.4 MB",
        creator: "Sarah Chen",
        collaborators: ["Michael Wong", "David Kim"],
        tags: ["Agreement", "TechCorp", "Service", "Active"],
        linkedFiles: ["Meeting Notes - TechCorp", "Previous Version"],
        version: "1.2",
        accessLevel: "Full",
        comments: 5,
        aiInsights:
          "This service agreement contains custom SLA terms and modified liability caps. Recent amendments focus on service level definitions and response time commitments.",
        category: "Agreements",
        collection: "Service Contracts",
      },
      {
        id: "2",
        name: "Vendor Agreement - SupplyCo",
        type: "pdf",
        lastModified: "2024-01-20",
        size: "1.8 MB",
        creator: "David Kim",
        collaborators: ["Sarah Chen"],
        tags: ["Agreement", "SupplyCo", "Vendor", "Pending"],
        linkedFiles: ["Vendor Evaluation", "Terms Sheet"],
        version: "1.0",
        accessLevel: "Full",
        comments: 3,
        aiInsights:
          "Standard vendor agreement with modified payment terms. Includes special provisions for rush delivery and quality assurance protocols.",
        category: "Agreements",
        collection: "Vendor Contracts",
      },
      {
        id: "3",
        name: "Partnership Agreement - GlobalTech",
        type: "docx",
        lastModified: "2024-01-25",
        size: "3.1 MB",
        creator: "Michael Wong",
        collaborators: ["Sarah Chen", "Emma Thompson"],
        tags: ["Agreement", "GlobalTech", "Partnership", "Draft"],
        linkedFiles: ["Term Sheet", "Due Diligence Report"],
        version: "2.1",
        accessLevel: "Restricted",
        comments: 8,
        aiInsights:
          "Strategic partnership agreement with revenue sharing model. Notable sections on intellectual property rights and joint venture operations.",
        category: "Agreements",
        collection: "Partnership Contracts",
      },

      // Legal Section
      {
        id: "4",
        name: "NDA - Project Alpha",
        type: "docx",
        lastModified: "2024-02-01",
        size: "1.1 MB",
        creator: "Emma Thompson",
        collaborators: ["David Lee"],
        tags: ["NDA", "Project Alpha", "Confidential"],
        linkedFiles: [],
        version: "1.0",
        accessLevel: "Confidential",
        comments: 2,
        aiInsights:
          "Standard NDA with enhanced IP protection clauses. Includes specific provisions for data handling and trade secrets.",
        category: "Legal",
        collection: "Project Documents",
      },
      {
        id: "5",
        name: "Lease Agreement - Office Space",
        type: "pdf",
        lastModified: "2024-01-28",
        size: "4.2 MB",
        creator: "Sarah Chen",
        collaborators: ["Michael Wong", "David Kim"],
        tags: ["Lease", "Real Estate", "Active"],
        linkedFiles: ["Floor Plans", "Building Specs"],
        version: "1.3",
        accessLevel: "Full",
        comments: 6,
        aiInsights:
          "Commercial lease agreement with renovation allowance and expansion options. Includes detailed maintenance responsibilities and utility arrangements.",
        category: "Legal",
        collection: "Real Estate",
      },
      {
        id: "6",
        name: "Trademark Registration - TechFlow",
        type: "pdf",
        lastModified: "2024-01-30",
        size: "2.8 MB",
        creator: "David Lee",
        collaborators: ["Emma Thompson"],
        tags: ["Trademark", "IP", "Pending"],
        linkedFiles: ["Logo Files", "Brand Guidelines"],
        version: "1.1",
        accessLevel: "Restricted",
        comments: 4,
        aiInsights:
          "Trademark application for TechFlow brand and associated marks. Includes comprehensive brand usage guidelines and protection strategy.",
        category: "Legal",
        collection: "Intellectual Property",
      },

      // HR Section
      {
        id: "7",
        name: "Employment Contract - John Doe",
        type: "docx",
        lastModified: "2024-02-02",
        size: "1.5 MB",
        creator: "HR Department",
        collaborators: ["Sarah Chen", "Legal Team"],
        tags: ["Employment", "Contract", "Active"],
        linkedFiles: ["Offer Letter", "Benefits Package"],
        version: "1.0",
        accessLevel: "Confidential",
        comments: 3,
        aiInsights:
          "Senior developer employment agreement with specialized IP assignment clauses and remote work provisions.",
        category: "HR",
        collection: "Employment Contracts",
      },
      {
        id: "8",
        name: "Employee Handbook - 2024",
        type: "pdf",
        lastModified: "2024-01-15",
        size: "5.6 MB",
        creator: "HR Department",
        collaborators: ["Legal Team", "Management"],
        tags: ["Policy", "Handbook", "Active"],
        linkedFiles: ["Previous Version", "Policy Updates"],
        version: "2.0",
        accessLevel: "Public",
        comments: 12,
        aiInsights:
          "Updated employee handbook with new remote work policies and mental health benefits. Significant changes to leave policies and professional development programs.",
        category: "HR",
        collection: "Company Policies",
      },
      {
        id: "9",
        name: "Benefits Summary - 2024",
        type: "pdf",
        lastModified: "2024-01-10",
        size: "2.2 MB",
        creator: "HR Department",
        collaborators: ["Finance Team"],
        tags: ["Benefits", "HR", "Active"],
        linkedFiles: ["Insurance Policy", "401k Plan"],
        version: "1.0",
        accessLevel: "Internal",
        comments: 5,
        aiInsights:
          "Comprehensive benefits package documentation including new mental health coverage and expanded parental leave policies.",
        category: "HR",
        collection: "Benefits",
      },

      // Sales Section
      {
        id: "10",
        name: "Sales Contract - BigClient",
        type: "docx",
        lastModified: "2024-02-03",
        size: "2.3 MB",
        creator: "Sales Team",
        collaborators: ["Legal Team", "Account Managers"],
        tags: ["Sales", "Contract", "High Priority"],
        linkedFiles: ["Proposal", "Price Quote"],
        version: "1.2",
        accessLevel: "Restricted",
        comments: 7,
        aiInsights: "Enterprise-level sales contract with custom SLA terms and volume-based pricing structure.",
        category: "Sales",
        collection: "Client Contracts",
      },
      {
        id: "11",
        name: "Master Service Agreement - TechGiant",
        type: "pdf",
        lastModified: "2024-01-29",
        size: "4.7 MB",
        creator: "Legal Team",
        collaborators: ["Sales Team", "Executive Team"],
        tags: ["MSA", "Enterprise", "Active"],
        linkedFiles: ["Service Schedule", "Pricing Appendix"],
        version: "2.1",
        accessLevel: "Confidential",
        comments: 15,
        aiInsights:
          "Comprehensive MSA for enterprise client with complex service integration requirements and custom compliance terms.",
        category: "Sales",
        collection: "Enterprise Agreements",
      },
      {
        id: "12",
        name: "Channel Partner Agreement - ResellCo",
        type: "pdf",
        lastModified: "2024-01-22",
        size: "3.3 MB",
        creator: "Sales Team",
        collaborators: ["Legal Team", "Partner Manager"],
        tags: ["Partner", "Agreement", "Active"],
        linkedFiles: ["Partner Profile", "Commission Structure"],
        version: "1.1",
        accessLevel: "Restricted",
        comments: 6,
        aiInsights:
          "Channel partner agreement with territory exclusivity and performance-based incentives. Includes detailed partner enablement program.",
        category: "Sales",
        collection: "Partner Agreements",
      },

      // Project Documentation
      {
        id: "13",
        name: "Technical Specification - Project Luna",
        type: "docx",
        lastModified: "2024-02-04",
        size: "6.2 MB",
        creator: "Engineering Team",
        collaborators: ["Product Team", "QA Team"],
        tags: ["Technical", "Specification", "Active"],
        linkedFiles: ["Requirements Doc", "Architecture Diagram"],
        version: "3.0",
        accessLevel: "Internal",
        comments: 23,
        aiInsights:
          "Detailed technical specification for Project Luna, including API documentation and system architecture details.",
        category: "Project Documentation",
        collection: "Technical Specs",
      },
      {
        id: "14",
        name: "Project Charter - Digital Transformation",
        type: "pdf",
        lastModified: "2024-01-18",
        size: "2.8 MB",
        creator: "Project Management",
        collaborators: ["Executive Team", "Department Heads"],
        tags: ["Project", "Charter", "Strategic"],
        linkedFiles: ["Budget Forecast", "Timeline"],
        version: "1.4",
        accessLevel: "Restricted",
        comments: 18,
        aiInsights:
          "Strategic project charter outlining digital transformation initiatives with detailed resource allocation and success metrics.",
        category: "Project Documentation",
        collection: "Project Management",
      },
      {
        id: "15",
        name: "Implementation Guide - Cloud Migration",
        type: "pdf",
        lastModified: "2024-01-26",
        size: "8.1 MB",
        creator: "IT Department",
        collaborators: ["Engineering Team", "Operations"],
        tags: ["Implementation", "Technical", "Active"],
        linkedFiles: ["Migration Schedule", "Risk Assessment"],
        version: "2.2",
        accessLevel: "Internal",
        comments: 31,
        aiInsights:
          "Comprehensive guide for cloud migration project, including detailed procedures and contingency plans.",
        category: "Project Documentation",
        collection: "Implementation Guides",
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






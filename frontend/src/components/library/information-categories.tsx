// src/components/library/information-categories.tsx

"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Card } from "@/components/ui/card"
import Link from "next/link"

const categories = [
  {
    id: "contracts",
    name: "Contracts",
    type: "LEGAL DOCUMENTS",
    gradient: "from-[#93C5FD]/10 via-[#BFDBFE]/20 to-[#93C5FD]/10",
    angle: "bg-gradient-to-br",
  },
  {
    id: "ndas",
    name: "NDAs",
    type: "NON-DISCLOSURE AGREEMENTS",
    gradient: "from-[#93C5FD]/15 via-[#BFDBFE]/25 to-[#93C5FD]/15",
    angle: "bg-gradient-to-tr",
  },
  {
    id: "legal-claims",
    name: "Legal Claims",
    type: "LITIGATION DOCUMENTS",
    gradient: "from-[#93C5FD]/20 via-[#BFDBFE]/30 to-[#93C5FD]/20",
    angle: "bg-gradient-to-r",
  },
  {
    id: "court-filings",
    name: "Court Filings",
    type: "JUDICIAL DOCUMENTS",
    gradient: "from-[#93C5FD]/25 via-[#BFDBFE]/35 to-[#93C5FD]/25",
    angle: "bg-gradient-to-bl",
  },
  {
    id: "settlements",
    name: "Settlements",
    type: "RESOLUTION DOCUMENTS",
    gradient: "from-[#93C5FD]/15 via-[#BFDBFE]/25 to-[#93C5FD]/15",
    angle: "bg-gradient-to-tl",
  },
  {
    id: "corporate-governance",
    name: "Corporate Governance",
    type: "INTERNAL DOCUMENTS",
    gradient: "from-[#93C5FD]/20 via-[#BFDBFE]/30 to-[#93C5FD]/20",
    angle: "bg-gradient-to-l",
  },
  {
    id: "transaction-documents",
    name: "Transaction Documents",
    type: "FINANCIAL RECORDS",
    gradient: "from-[#93C5FD]/25 via-[#BFDBFE]/35 to-[#93C5FD]/25",
    angle: "bg-gradient-to-tr",
  },
  {
    id: "client-proposals",
    name: "Client Proposals",
    type: "BUSINESS DEVELOPMENT",
    gradient: "from-[#93C5FD]/30 via-[#BFDBFE]/40 to-[#93C5FD]/30",
    angle: "bg-gradient-to-br",
  },
]

export function InformationCategories() {
  const [hoveredId, setHoveredId] = useState<string | null>(null)

  return (
    <div className="w-full">
      <div className="mb-4">
        <h2 className="text-[10px] font-light tracking-[1px] text-[#1C1C1C]">CATEGORIES</h2>
      </div>
      <div className="grid grid-cols-4 gap-4">
        {categories.map((category) => (
          <Link key={category.id} href={`/library/categories/${category.id}`}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              onHoverStart={() => setHoveredId(category.id)}
              onHoverEnd={() => setHoveredId(null)}
            >
              <Card
                className={`group relative aspect-[4/3] cursor-pointer overflow-hidden border-white/20 ${category.angle} ${category.gradient} p-6 transition-all duration-500 hover:shadow-lg hover:border-white/40`}
              >
                <motion.div
                  className="flex h-full flex-col justify-end"
                  animate={{
                    y: hoveredId === category.id ? -4 : 0,
                  }}
                  transition={{ duration: 0.2 }}
                >
                  <h3 className="text-lg font-medium text-[#1C1C1C]">{category.name}</h3>
                  <p className="mt-1 text-xs tracking-wide text-[#525766]">{category.type}</p>
                </motion.div>
              </Card>
            </motion.div>
          </Link>
        ))}
      </div>
    </div>
  )
}


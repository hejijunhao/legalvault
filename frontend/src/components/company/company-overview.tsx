// src/components/company/company-overview.tsx

"use client"

import { motion } from "framer-motion"
import Image from "next/image"
import { Card } from "@/components/ui/card"
import { MapPin, Users, Crown } from "lucide-react"

interface CompanyOverviewProps {
  data: {
    logo: string
    name: string
    industry: string
    practiceAreas: string[]
    officeLocations: string[]
    companySize: string
    subscriptionTier: string
  }
}

export function CompanyOverview({ data }: CompanyOverviewProps) {
  return (
    <Card className="overflow-hidden bg-white/60 backdrop-blur-md">
      <div className="p-6">
        <div className="flex items-center space-x-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
          >
            <Image
              src={data.logo || "/placeholder.svg"}
              alt={data.name}
              width={80}
              height={80}
              className="rounded-lg"
            />
          </motion.div>
          <div>
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.5 }}
              className="text-2xl font-bold text-gray-900"
            >
              {data.name}
            </motion.h2>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.5 }}
              className="text-gray-600"
            >
              {data.industry}
            </motion.p>
          </div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.5 }}
          className="mt-6 grid gap-4 sm:grid-cols-2"
        >
          <div>
            <h3 className="text-sm font-medium text-gray-500">Practice Areas</h3>
            <ul className="mt-1 space-y-1">
              {data.practiceAreas.map((area, index) => (
                <li key={index} className="text-sm text-gray-700">
                  {area}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h3 className="text-sm font-medium text-gray-500">Office Locations</h3>
            <ul className="mt-1 space-y-1">
              {data.officeLocations.map((location, index) => (
                <li key={index} className="flex items-center text-sm text-gray-700">
                  <MapPin className="mr-1 h-4 w-4 text-gray-400" />
                  {location}
                </li>
              ))}
            </ul>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.5 }}
          className="mt-6 flex items-center justify-between"
        >
          <div className="flex items-center text-sm text-gray-700">
            <Users className="mr-2 h-5 w-5 text-gray-400" />
            {data.companySize}
          </div>
          <div className="flex items-center text-sm font-medium text-purple-600">
            <Crown className="mr-2 h-5 w-5" />
            {data.subscriptionTier}
          </div>
        </motion.div>
      </div>
    </Card>
  )
}


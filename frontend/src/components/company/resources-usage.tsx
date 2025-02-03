// src/components/company/resources-usage.tsx

"use client"

import { motion } from "framer-motion"
import { Card } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { HardDrive, Zap, FileText, MessageSquare, Users } from "lucide-react"

interface ResourcesUsageProps {
  data: {
    storage: {
      used: number
      total: number
      unit: string
    }
    apiCalls: {
      used: number
      total: number
      period: string
    }
    documentProcessing: {
      processed: number
      averageTime: string
    }
    vpInteractions: {
      totalInteractions: number
      averageResponseTime: string
    }
    licenseUtilization: {
      used: number
      total: number
    }
  }
}

export function ResourcesUsage({ data }: ResourcesUsageProps) {
  return (
    <Card className="overflow-hidden bg-white/60 backdrop-blur-md">
      <div className="p-6">
        <h2 className="mb-4 text-xl font-semibold text-gray-900">Resources Usage</h2>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="space-y-6"
        >
          <div>
            <div className="mb-2 flex items-center justify-between">
              <div className="flex items-center">
                <HardDrive className="mr-2 h-5 w-5 text-blue-500" />
                <span className="text-sm font-medium text-gray-700">Storage</span>
              </div>
              <span className="text-sm text-gray-500">
                {data.storage.used} / {data.storage.total} {data.storage.unit}
              </span>
            </div>
            <Progress value={(data.storage.used / data.storage.total) * 100} className="h-2" />
          </div>

          <div>
            <div className="mb-2 flex items-center justify-between">
              <div className="flex items-center">
                <Zap className="mr-2 h-5 w-5 text-yellow-500" />
                <span className="text-sm font-medium text-gray-700">API Calls</span>
              </div>
              <span className="text-sm text-gray-500">
                {data.apiCalls.used.toLocaleString()} / {data.apiCalls.total.toLocaleString()} per{" "}
                {data.apiCalls.period}
              </span>
            </div>
            <Progress value={(data.apiCalls.used / data.apiCalls.total) * 100} className="h-2" />
          </div>

          <div>
            <div className="mb-2 flex items-center justify-between">
              <div className="flex items-center">
                <FileText className="mr-2 h-5 w-5 text-green-500" />
                <span className="text-sm font-medium text-gray-700">Document Processing</span>
              </div>
              <span className="text-sm text-gray-500">
                {data.documentProcessing.processed.toLocaleString()} docs processed
              </span>
            </div>
            <p className="text-sm text-gray-500">Average processing time: {data.documentProcessing.averageTime}</p>
          </div>

          <div>
            <div className="mb-2 flex items-center justify-between">
              <div className="flex items-center">
                <MessageSquare className="mr-2 h-5 w-5 text-purple-500" />
                <span className="text-sm font-medium text-gray-700">VP Interactions</span>
              </div>
              <span className="text-sm text-gray-500">
                {data.vpInteractions.totalInteractions.toLocaleString()} total interactions
              </span>
            </div>
            <p className="text-sm text-gray-500">Average response time: {data.vpInteractions.averageResponseTime}</p>
          </div>

          <div>
            <div className="mb-2 flex items-center justify-between">
              <div className="flex items-center">
                <Users className="mr-2 h-5 w-5 text-indigo-500" />
                <span className="text-sm font-medium text-gray-700">License Utilization</span>
              </div>
              <span className="text-sm text-gray-500">
                {data.licenseUtilization.used} / {data.licenseUtilization.total} licenses
              </span>
            </div>
            <Progress value={(data.licenseUtilization.used / data.licenseUtilization.total) * 100} className="h-2" />
          </div>
        </motion.div>
      </div>
    </Card>
  )
}


// src/components/profile/user-profile/integration-connections.tsx

"use client"

import { motion } from "framer-motion"
import { Card } from "@/components/ui/card"
import { Mail, Calendar, FileText, CheckSquare, MessageSquare } from "lucide-react"

interface IntegrationConnectionsProps {
  data: {
    emailAccounts: string[]
    calendarIntegrations: string[]
    documentManagement: string[]
    taskManagement: string[]
    communicationPlatforms: string[]
  }
}

export function IntegrationConnections({ data }: IntegrationConnectionsProps) {
  const integrations = [
    { icon: Mail, title: "Email Accounts", items: data.emailAccounts },
    { icon: Calendar, title: "Calendar Integrations", items: data.calendarIntegrations },
    { icon: FileText, title: "Document Management", items: data.documentManagement },
    { icon: CheckSquare, title: "Task Management", items: data.taskManagement },
    { icon: MessageSquare, title: "Communication Platforms", items: data.communicationPlatforms },
  ]

  return (
    <Card className="overflow-hidden bg-white/60 backdrop-blur-md">
      <div className="p-6">
        <h2 className="mb-4 text-xl font-semibold text-gray-900">Integration Connections</h2>
        <div className="space-y-4">
          {integrations.map((integration, index) => (
            <motion.div
              key={integration.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <div className="flex items-center">
                <integration.icon className="mr-2 h-5 w-5 text-blue-500" />
                <h3 className="font-medium text-gray-700">{integration.title}</h3>
              </div>
              <div className="mt-2 flex flex-wrap gap-2">
                {integration.items.map((item) => (
                  <span key={item} className="rounded-full bg-blue-100 px-3 py-1 text-sm font-medium text-blue-800">
                    {item}
                  </span>
                ))}
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </Card>
  )
}


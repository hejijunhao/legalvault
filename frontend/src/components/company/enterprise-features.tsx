// src/components/company/enterprise-features.tsx

"use client"

import { motion } from "framer-motion"
import { Card } from "@/components/ui/card"
import { Settings, Shield, FileCheck, Clock, Link } from "lucide-react"

interface EnterpriseFeaturesProps {
  data: {
    customVpConfigs: number
    securitySettings: {
      twoFactor: boolean
      ssoEnabled: boolean
      dataEncryption: string
    }
    complianceRequirements: string[]
    dataRetentionPolicy: string
    customIntegrations: string[]
  }
}

export function EnterpriseFeatures({ data }: EnterpriseFeaturesProps) {
  return (
    <Card className="overflow-hidden bg-white/60 backdrop-blur-md">
      <div className="p-6">
        <h2 className="mb-4 text-xl font-semibold text-gray-900">Enterprise Features</h2>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="space-y-6"
        >
          <div>
            <div className="flex items-center">
              <Settings className="mr-2 h-5 w-5 text-blue-500" />
              <h3 className="text-sm font-medium text-gray-700">Custom VP Configurations</h3>
            </div>
            <p className="mt-1 text-sm text-gray-500">{data.customVpConfigs} custom configurations</p>
          </div>

          <div>
            <div className="flex items-center">
              <Shield className="mr-2 h-5 w-5 text-green-500" />
              <h3 className="text-sm font-medium text-gray-700">Security Settings</h3>
            </div>
            <ul className="mt-1 space-y-1 text-sm text-gray-500">
              <li>Two-Factor Authentication: {data.securitySettings.twoFactor ? "Enabled" : "Disabled"}</li>
              <li>SSO: {data.securitySettings.ssoEnabled ? "Enabled" : "Disabled"}</li>
              <li>Data Encryption: {data.securitySettings.dataEncryption}</li>
            </ul>
          </div>

          <div>
            <div className="flex items-center">
              <FileCheck className="mr-2 h-5 w-5 text-yellow-500" />
              <h3 className="text-sm font-medium text-gray-700">Compliance Requirements</h3>
            </div>
            <div className="mt-1 flex flex-wrap gap-2">
              {data.complianceRequirements.map((req, index) => (
                <span key={index} className="rounded-full bg-yellow-100 px-2 py-1 text-xs font-medium text-yellow-800">
                  {req}
                </span>
              ))}
            </div>
          </div>

          <div>
            <div className="flex items-center">
              <Clock className="mr-2 h-5 w-5 text-purple-500" />
              <h3 className="text-sm font-medium text-gray-700">Data Retention Policy</h3>
            </div>
            <p className="mt-1 text-sm text-gray-500">{data.dataRetentionPolicy}</p>
          </div>

          <div>
            <div className="flex items-center">
              <Link className="mr-2 h-5 w-5 text-indigo-500" />
              <h3 className="text-sm font-medium text-gray-700">Custom Integrations</h3>
            </div>
            <div className="mt-1 flex flex-wrap gap-2">
              {data.customIntegrations.map((integration, index) => (
                <span key={index} className="rounded-full bg-indigo-100 px-2 py-1 text-xs font-medium text-indigo-800">
                  {integration}
                </span>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </Card>
  )
}


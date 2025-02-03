// src/app/(app)/company/page.tsx

"use client"

import { motion } from "framer-motion"
import { CompanyOverview } from "@/components/company/company-overview"
import { TeamManagement } from "@/components/company/team-management"
import { ResourcesUsage } from "@/components/company/resources-usage"
import { EnterpriseFeatures } from "@/components/company/enterprise-features"

// Mock data for the company
const companyData = {
  companyOverview: {
    logo: "/placeholder.svg?height=100&width=100",
    name: "LegalTech Solutions",
    industry: "Legal Technology",
    practiceAreas: ["Corporate Law", "Intellectual Property", "Mergers & Acquisitions"],
    officeLocations: ["New York", "San Francisco", "London"],
    companySize: "250-500 employees",
    subscriptionTier: "Enterprise Plus",
  },
  teamManagement: {
    teamMembers: [
      { id: 1, name: "Sarah Chen", role: "Senior Legal Counsel", department: "Legal", accessLevel: "Admin" },
      {
        id: 2,
        name: "Michael Wong",
        role: "Legal Operations Manager",
        department: "Operations",
        accessLevel: "Manager",
      },
      { id: 3, name: "Emily Johnson", role: "Paralegal", department: "Legal", accessLevel: "Standard" },
      // Add more team members as needed
    ],
    departments: ["Legal", "Operations", "IT", "Finance"],
    activityOverview: {
      activeProjects: 15,
      completedTasks: 287,
      ongoingCollaborations: 8,
    },
  },
  resourcesUsage: {
    storage: {
      used: 1.7,
      total: 5,
      unit: "TB",
    },
    apiCalls: {
      used: 8750000,
      total: 10000000,
      period: "month",
    },
    documentProcessing: {
      processed: 15000,
      averageTime: "2.3 seconds",
    },
    vpInteractions: {
      totalInteractions: 45000,
      averageResponseTime: "0.8 seconds",
    },
    licenseUtilization: {
      used: 230,
      total: 250,
    },
  },
  enterpriseFeatures: {
    customVpConfigs: 3,
    securitySettings: {
      twoFactor: true,
      ssoEnabled: true,
      dataEncryption: "256-bit AES",
    },
    complianceRequirements: ["GDPR", "CCPA", "HIPAA"],
    dataRetentionPolicy: "7 years",
    customIntegrations: ["Salesforce", "NetDocuments", "Clio"],
  },
}

export default function CompanyPage() {
  return (
    <div className="min-h-screen py-6">
      <div className="mx-auto max-w-[1440px] px-4">
        <motion.h1
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8 text-[32px] font-normal italic leading-6 text-[#111827] font-['Libre_Baskerville']"
        >
          Company Overview
        </motion.h1>
        <div className="grid gap-8 md:grid-cols-2">
          <div className="space-y-8">
            <CompanyOverview data={companyData.companyOverview} />
            <ResourcesUsage data={companyData.resourcesUsage} />
          </div>
          <div className="space-y-8">
            <TeamManagement data={companyData.teamManagement} />
            <EnterpriseFeatures data={companyData.enterpriseFeatures} />
          </div>
        </div>
      </div>
    </div>
  )
}


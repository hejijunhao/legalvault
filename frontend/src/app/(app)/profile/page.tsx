// src/app/(app)/profile/page.tsx

"use client"

import { motion } from "framer-motion"
import { PersonalInfo } from "@/components/profile/user-profile/personal-info"
import { WorkStats } from "@/components/profile/user-profile/work-stats"
import { IntegrationConnections } from "@/components/profile/user-profile/integration-connections"

// Mock data for the profile
const profileData = {
  personalInfo: {
    profilePicture: "/placeholder.svg?height=200&width=200",
    fullName: "Sarah Chen",
    jobTitle: "Senior Legal Counsel",
    email: "sarah.chen@legalvault.com",
    phone: "+1 (555) 123-4567",
    officeLocation: "New York, NY",
    timeZone: "Eastern Time (ET)",
    languages: ["English", "Mandarin"],
    bio: "Experienced legal professional specializing in corporate law and M&A. Passionate about leveraging technology to streamline legal processes.",
  },
  workStats: {
    activeProjects: 7,
    taskCompletionRate: 92,
    recentActivities: [
      { id: 1, description: "Reviewed merger agreement for Project Greenbridge", timestamp: "2 hours ago" },
      { id: 2, description: "Completed due diligence report for Elysian Ventures", timestamp: "1 day ago" },
      { id: 3, description: "Updated compliance documentation for Q1 2024", timestamp: "3 days ago" },
    ],
    collaborationMetrics: {
      teamMembers: 12,
      documentsShared: 156,
      commentsResolved: 89,
    },
    timeSaved: "37 hours this month",
  },
  integrationConnections: {
    emailAccounts: ["sarah.chen@legalvault.com", "s.chen@personal.com"],
    calendarIntegrations: ["Google Calendar", "Outlook"],
    documentManagement: ["SharePoint", "Google Drive"],
    taskManagement: ["Asana", "Trello"],
    communicationPlatforms: ["Slack", "Microsoft Teams"],
  },
}

export default function ProfilePage() {
  return (
    <div className="min-h-screen py-6">
      <div className="mx-auto max-w-[1440px] px-4">
        <motion.h1
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8 text-[32px] font-normal italic leading-6 text-[#111827] font-['Libre_Baskerville']"
        >
          Your Profile
        </motion.h1>
        <div className="grid gap-8 md:grid-cols-2">
          <PersonalInfo data={profileData.personalInfo} />
          <div className="space-y-8">
            <WorkStats data={profileData.workStats} />
            <IntegrationConnections data={profileData.integrationConnections} />
          </div>
        </div>
      </div>
    </div>
  )
}


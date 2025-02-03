// src/components/company/team-management.tsx

"use client"

import { motion } from "framer-motion"
import { Card } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

interface TeamMember {
  id: number
  name: string
  role: string
  department: string
  accessLevel: string
}

interface TeamManagementProps {
  data: {
    teamMembers: TeamMember[]
    departments: string[]
    activityOverview: {
      activeProjects: number
      completedTasks: number
      ongoingCollaborations: number
    }
  }
}

export function TeamManagement({ data }: TeamManagementProps) {
  return (
    <Card className="overflow-hidden bg-white/60 backdrop-blur-md">
      <div className="p-6">
        <h2 className="mb-4 text-xl font-semibold text-gray-900">Team Management</h2>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-6"
        >
          <h3 className="mb-2 text-sm font-medium text-gray-500">Team Members</h3>
          <div className="space-y-3">
            {data.teamMembers.slice(0, 3).map((member) => (
              <div key={member.id} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <Avatar>
                    <AvatarImage src={`/placeholder.svg?height=40&width=40`} alt={member.name} />
                    <AvatarFallback>
                      {member.name
                        .split(" ")
                        .map((n) => n[0])
                        .join("")}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{member.name}</p>
                    <p className="text-xs text-gray-500">{member.role}</p>
                  </div>
                </div>
                <div className="text-xs text-gray-500">
                  {member.department} • {member.accessLevel}
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.5 }}
          className="mb-6"
        >
          <h3 className="mb-2 text-sm font-medium text-gray-500">Departments</h3>
          <div className="flex flex-wrap gap-2">
            {data.departments.map((dept, index) => (
              <span key={index} className="rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-600">
                {dept}
              </span>
            ))}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.5 }}
        >
          <h3 className="mb-2 text-sm font-medium text-gray-500">Activity Overview</h3>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">{data.activityOverview.activeProjects}</p>
              <p className="text-xs text-gray-500">Active Projects</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">{data.activityOverview.completedTasks}</p>
              <p className="text-xs text-gray-500">Completed Tasks</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-600">{data.activityOverview.ongoingCollaborations}</p>
              <p className="text-xs text-gray-500">Ongoing Collaborations</p>
            </div>
          </div>
        </motion.div>
      </div>
    </Card>
  )
}


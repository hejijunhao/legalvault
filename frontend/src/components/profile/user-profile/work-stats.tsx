// src/components/profile/user-profile/work-stats.tsx

"use client"

import { motion } from "framer-motion"
import { Card } from "@/components/ui/card"
import { CheckCircle, Users, Clock } from "lucide-react"
import { animations, withDelay } from "@/lib/animations"

interface WorkStatsProps {
  data: {
    activeProjects: number
    taskCompletionRate: number
    recentActivities: Array<{ id: number; description: string; timestamp: string }>
    collaborationMetrics: {
      teamMembers: number
      documentsShared: number
      commentsResolved: number
    }
    timeSaved: string
  }
}

export function WorkStats({ data }: WorkStatsProps) {
  return (
    <Card className="overflow-hidden bg-white/60 backdrop-blur-md">
      <div className="p-6">
        <h2 className="mb-4 text-xl font-semibold text-gray-900">Work Statistics</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          <motion.div
            {...animations.fadeInUp}
            className="rounded-lg bg-blue-50 p-4"
          >
            <div className="text-2xl font-bold text-blue-600">{data.activeProjects}</div>
            <div className="text-sm text-blue-600">Active Projects</div>
          </motion.div>
          <motion.div
            {...withDelay(animations.fadeInUp, 0.1)}
            className="rounded-lg bg-green-50 p-4"
          >
            <div className="text-2xl font-bold text-green-600">{data.taskCompletionRate}%</div>
            <div className="text-sm text-green-600">Task Completion Rate</div>
          </motion.div>
        </div>
        <motion.div
          {...withDelay(animations.fadeInUp, 0.2)}
          className="mt-4"
        >
          <h3 className="mb-2 font-semibold text-gray-700">Recent Activities</h3>
          <ul className="space-y-2">
            {data.recentActivities.map((activity) => (
              <li key={activity.id} className="flex items-start text-sm">
                <CheckCircle className="mr-2 h-5 w-5 text-green-500" />
                <div>
                  <div className="text-gray-600">{activity.description}</div>
                  <div className="text-xs text-gray-400">{activity.timestamp}</div>
                </div>
              </li>
            ))}
          </ul>
        </motion.div>
        <motion.div
          {...withDelay(animations.fadeInUp, 0.3)}
          className="mt-4"
        >
          <h3 className="mb-2 font-semibold text-gray-700">Collaboration Metrics</h3>
          <div className="grid gap-2 sm:grid-cols-3">
            <div className="flex items-center">
              <Users className="mr-2 h-5 w-5 text-blue-500" />
              <div>
                <div className="text-sm font-medium text-gray-600">{data.collaborationMetrics.teamMembers}</div>
                <div className="text-xs text-gray-400">Team Members</div>
              </div>
            </div>
            <div>
              <div className="text-sm font-medium text-gray-600">{data.collaborationMetrics.documentsShared}</div>
              <div className="text-xs text-gray-400">Documents Shared</div>
            </div>
            <div>
              <div className="text-sm font-medium text-gray-600">{data.collaborationMetrics.commentsResolved}</div>
              <div className="text-xs text-gray-400">Comments Resolved</div>
            </div>
          </div>
        </motion.div>
        <motion.div
          {...withDelay(animations.fadeInUp, 0.4)}
          className="mt-4 flex items-center rounded-lg bg-purple-50 p-4"
        >
          <Clock className="mr-2 h-6 w-6 text-purple-600" />
          <div>
            <div className="text-lg font-semibold text-purple-600">Time Saved</div>
            <div className="text-sm text-purple-600">{data.timeSaved}</div>
          </div>
        </motion.div>
      </div>
    </Card>
  )
}

// src/components/knowledge/past-tasks.tsx

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { CheckSquare, Clock, BarChart } from "lucide-react"

export function PastTasks() {
  const taskStats = [
    { label: "Tasks Completed", value: 1248, icon: CheckSquare },
    { label: "Avg. Response Time", value: "2.5h", icon: Clock },
    { label: "Success Rate", value: "99.2%", icon: BarChart },
  ]

  const recentTasks = [
    {
      id: 1,
      task: "Contract Review - Project Greenbridge",
      completion: "Completed in 1.5h",
    },
    {
      id: 2,
      task: "Due Diligence Report - Elysian Ventures",
      completion: "Completed in 4h",
    },
  ]

  return (
    <Card className="overflow-hidden backdrop-blur-sm">
      <CardHeader className="border-b bg-white/5 p-6">
        <CardTitle className="flex items-center gap-2 text-lg">
          <CheckSquare className="h-5 w-5" />
          Past Tasks
        </CardTitle>
      </CardHeader>
      <CardContent className="grid gap-6 p-6">
        <div className="grid grid-cols-3 gap-4">
          {taskStats.map((stat, index) => (
            <div key={index} className="space-y-2">
              <div className="flex items-center gap-2">
                <stat.icon className="h-4 w-4 text-[#8992A9]" />
                <span className="text-sm font-medium">{stat.label}</span>
              </div>
              <p className="text-2xl font-bold text-[#525766]">{stat.value}</p>
            </div>
          ))}
        </div>
        <div className="space-y-4">
          <h3 className="text-sm font-medium">Recent Completions</h3>
          {recentTasks.map((task) => (
            <div key={task.id} className="space-y-1">
              <div className="text-sm text-[#1C1C1C]">{task.task}</div>
              <div className="text-xs text-[#8992A9]">{task.completion}</div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}


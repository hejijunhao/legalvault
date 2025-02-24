// src/components/paralegal/activity-block.tsx

"use client"

import { useState } from "react"
import { format, eachDayOfInterval, subYears, startOfWeek, addDays, isSameDay, addYears } from "date-fns"
import { ChevronLeft, ChevronRight } from "lucide-react"

type ActivityLevel = 0 | 1 | 2 | 3 | 4
type DayActivity = {
  date: Date
  level: ActivityLevel
}

type ActivityBlockProps = {}

export function ActivityBlock({}: ActivityBlockProps) {
  const [currentYear, setCurrentYear] = useState(new Date())

  // Generate sample data for the current year
  const startDate = startOfWeek(subYears(currentYear, 1))
  const endDate = startOfWeek(currentYear)
  const days = eachDayOfInterval({ start: startDate, end: endDate })

  // Sample activity data - in real app, this would come from API
  const activityData: DayActivity[] = days.map((date) => ({
    date,
    level: Math.floor(Math.random() * 5) as ActivityLevel,
  }))

  const totalContributions = activityData.reduce((sum, day) => sum + day.level, 0)

  // Get array of month labels
  const months = Array.from(new Set(days.map((date) => format(date, "MMM"))))

  const navigateYear = (direction: "prev" | "next") => {
    setCurrentYear((prev) => (direction === "prev" ? subYears(prev, 1) : addYears(prev, 1)))
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="p-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-medium text-gray-900">Activity Overview</h3>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => navigateYear("prev")}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="text-sm text-gray-600">{format(currentYear, "yyyy")}</span>
            <button
              onClick={() => navigateYear("next")}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
        <p className="text-2xl font-semibold text-gray-900 mb-1">{totalContributions}</p>
        <p className="text-sm text-gray-500">contributions in the last year</p>
      </div>

      <div className="px-4 pb-4">
        <div className="grid grid-cols-[repeat(52,1fr)] gap-[2px] h-[100px]">
          {Array.from({ length: 52 }).map((_, weekIndex) => (
            <div key={weekIndex} className="grid grid-rows-7 gap-[2px]">
              {Array.from({ length: 7 }).map((_, dayIndex) => {
                const currentDate = addDays(startDate, weekIndex * 7 + dayIndex)
                const activity = activityData.find((d) => isSameDay(d.date, currentDate))
                const level = activity?.level || 0

                return (
                  <div
                    key={dayIndex}
                    className={`w-full h-full rounded-sm ${getActivityColor(level)}`}
                    title={`${format(currentDate, "MMM d, yyyy")}: ${level} contributions`}
                  />
                )
              })}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function getActivityColor(level: ActivityLevel): string {
  const colors = {
    0: "bg-gray-100",
    1: "bg-emerald-100",
    2: "bg-emerald-200",
    3: "bg-emerald-300",
    4: "bg-emerald-400",
  }
  return colors[level]
}


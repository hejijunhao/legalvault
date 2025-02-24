// src/components/paralegal/activity-block.tsx

"use client"

import { Card } from "@/components/ui/card"
import { format, eachDayOfInterval, subYears, startOfWeek, addDays, isSameDay, addYears } from "date-fns"
import { ChevronLeft, ChevronRight } from "lucide-react"
import { useState } from "react"

type ActivityLevel = 0 | 1 | 2 | 3 | 4
type DayActivity = {
  date: Date
  level: ActivityLevel
}

export function ActivityBlock() {
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

  // Get weekday labels (Sun-Sat)
  const weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

  const navigateYear = (direction: "prev" | "next") => {
    setCurrentYear((prev) => (direction === "prev" ? subYears(prev, 1) : addYears(prev, 1)))
  }

  return (
    <Card className="relative overflow-hidden rounded-3xl bg-white border-none shadow-lg hover:shadow-xl transition-all duration-300 h-[215px] w-full">
      <div className="h-full p-4 flex flex-col">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm text-gray-800">
            <span className="font-medium">{totalContributions} contributions</span>
            <span className="text-gray-500 ml-1">in the last year</span>
          </h3>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => navigateYear("prev")}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="text-gray-600 text-sm">{format(currentYear, "yyyy")}</span>
            <button
              onClick={() => navigateYear("next")}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>

        <div className="flex-1 min-h-0">
          {/* Months row */}
          <div className="grid grid-cols-[auto_repeat(12,1fr)] gap-[2px] mb-1">
            <div className="text-[10px] text-gray-400" /> {/* Empty cell for alignment */}
            {months.map((month) => (
              <div key={month} className="text-[10px] text-gray-500">
                {month}
              </div>
            ))}
          </div>

          {/* Calendar grid */}
          <div className="grid grid-cols-[auto_repeat(52,1fr)] gap-[2px] h-[calc(100%-24px)]">
            {/* Weekday labels */}
            <div className="grid grid-rows-7 gap-[2px]">
              {weekdays.map((day) => (
                <div key={day} className="text-[10px] text-gray-500 h-3 flex items-center">
                  {day}
                </div>
              ))}
            </div>

            {/* Activity squares */}
            {Array.from({ length: 52 }).map((_, weekIndex) => (
              <div key={weekIndex} className="grid grid-rows-7 gap-[2px]">
                {Array.from({ length: 7 }).map((_, dayIndex) => {
                  const currentDate = addDays(startDate, weekIndex * 7 + dayIndex)
                  const activity = activityData.find((d) => isSameDay(d.date, currentDate))
                  const level = activity?.level || 0

                  return (
                    <div
                      key={dayIndex}
                      className={`
                        h-3 w-full rounded-sm transition-all duration-200
                        ${getActivityColor(level)}
                        hover:ring-1 hover:ring-gray-300
                      `}
                      title={`${format(currentDate, "MMM d, yyyy")}: ${level} contributions`}
                    />
                  )
                })}
              </div>
            ))}
          </div>

          {/* Legend */}
          <div className="flex items-center justify-end mt-1 space-x-1 text-[10px] text-gray-500">
            <span>Less</span>
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className={`h-2 w-2 rounded-sm ${getActivityColor(i as ActivityLevel)}`} />
            ))}
            <span>More</span>
          </div>
        </div>
      </div>
    </Card>
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




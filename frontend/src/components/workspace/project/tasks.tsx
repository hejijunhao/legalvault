// src/components/workspace/project/tasks.tsx

import { Card, CardTitle } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Calendar } from 'lucide-react'

const tasks = [
  { id: 1, title: "Review Gemini pitchdeck", date: "Today", type: "today" },
  { id: 2, title: "Revert to Sheryl Koh re SHA changes", date: "Today", type: "today" },
  { id: 3, title: "Check-in on Project Blue Horseshoe", date: "Tomorrow", type: "tomorrow" },
  { id: 4, title: "Compile research for Sean Bean", date: "Next Thu 23Nov", type: "future" },
]

export function Tasks() {
  return (
    <Card className="flex flex-1 flex-col items-start gap-2.5 self-stretch rounded-[5px] border-[#E5E7EB] bg-[rgba(191,219,254,0.20)] p-[11px_14px] backdrop-blur-sm">
      <div className="flex flex-1 flex-col items-start gap-[6px]">
        <CardTitle className="h-[18.493px] self-stretch text-[10px] font-light tracking-[1px] text-[#1C1C1C]">
          TASKS
        </CardTitle>
        <div className="w-full space-y-2">
          {tasks.map((task) => (
            <div key={task.id} className="flex items-center gap-[10px]">
              <Checkbox
                className="h-4 w-4 border-[#8992A9]"
              />
              <div className="flex flex-1 items-center justify-between">
                <p className="text-[14px] font-normal tracking-[-0.42px] text-[#525766]">
                  {task.title}
                </p>
                <div className="flex items-center gap-[3px]">
                  {task.type === "today" ? (
                    <span className="flex items-center justify-center gap-[2px] rounded-[20px] bg-[#9FE870] px-[5px] py-[2px] text-xs text-[#09332B]">
                      <Calendar className="h-3.5 w-3.5" />
                      {task.date}
                    </span>
                  ) : (
                    <>
                      <Calendar className="h-3.5 w-3.5 text-[#8992A9]" />
                      <span className="text-xs text-[#8992A9]">{task.date}</span>
                    </>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </Card>
  )
}


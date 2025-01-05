// src/components/workspace/reminders.tsx

import { Card, CardTitle } from "@/components/ui/card"
import { Bell } from 'lucide-react'

const reminders = [
  { id: 1, title: "Review Gemini pitchdeck", time: "Today 6pm", urgent: true },
  { id: 2, title: "Glencore Mitsubishi Lease Renewal due", time: "14 Nov 1pm" },
  { id: 3, title: "Capitaland Merger due", time: "2 Dec 10am" },
  { id: 4, title: "Internal review for", time: "9 Jan '25 11am" },
]

export function Reminders() {
  return (
    <Card className="flex flex-1 flex-col items-start gap-2.5 self-stretch rounded-[5px] border-[#E5E7EB] bg-[rgba(191,219,254,0.20)] p-[11px_14px] backdrop-blur-sm">
      <div className="flex flex-1 flex-col items-start gap-[6px]">
        <CardTitle className="h-[18.493px] self-stretch text-[10px] font-light tracking-[1px] text-[#1C1C1C]">
          REMINDERS
        </CardTitle>
        <div className="w-full space-y-2">
          {reminders.map((reminder) => (
            <div key={reminder.id} className="flex items-center gap-[10px]">
              <div className="flex flex-1 items-center justify-between">
                <p className="text-[14px] font-normal tracking-[-0.42px] text-[#525766]">
                  {reminder.title}
                </p>
                <div className="flex items-center gap-[3px]">
                  {reminder.urgent ? (
                    <span className="flex items-center justify-center gap-[2px] rounded-[20px] bg-[#9FE870] px-[5px] py-[2px] text-xs text-[#09332B]">
                      <Bell className="h-3.5 w-3.5" />
                      {reminder.time}
                    </span>
                  ) : (
                    <>
                      <Bell className="h-3.5 w-3.5 text-[#8992A9]" />
                      <span className="text-xs text-[#8992A9]">{reminder.time}</span>
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
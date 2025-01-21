// src/components/knowledge/education.tsx

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { GraduationCap, Book, CheckCircle } from "lucide-react"

export function Education() {
  const learningModules = [
    { id: 1, name: "Corporate Law Fundamentals", progress: 100 },
    { id: 2, name: "Contract Analysis", progress: 85 },
    { id: 3, name: "Legal Research Methods", progress: 70 },
  ]

  return (
    <Card className="overflow-hidden backdrop-blur-sm">
      <CardHeader className="border-b bg-white/5 p-6">
        <CardTitle className="flex items-center gap-2 text-lg">
          <GraduationCap className="h-5 w-5" />
          Education
        </CardTitle>
      </CardHeader>
      <CardContent className="p-6">
        <div className="space-y-4">
          {learningModules.map((module) => (
            <div key={module.id} className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Book className="h-4 w-4 text-[#8992A9]" />
                  <span className="text-sm text-[#525766]">{module.name}</span>
                </div>
                {module.progress === 100 ? (
                  <CheckCircle className="h-4 w-4 text-[#9FE870]" />
                ) : (
                  <span className="text-sm text-[#8992A9]">{module.progress}%</span>
                )}
              </div>
              <div className="h-1 overflow-hidden rounded-full bg-[#8992A9]/20">
                <div className="h-full bg-[#9FE870]" style={{ width: `${module.progress}%` }} />
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}


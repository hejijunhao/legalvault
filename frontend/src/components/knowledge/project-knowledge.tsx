// src/components/workspace/project-knowledge.tsx

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Briefcase, FileText, Users } from "lucide-react"

export function ProjectKnowledge() {
  const projects = [
    {
      id: 1,
      name: "Project Greenbridge",
      type: "M&A",
      documents: 45,
      team: 8,
    },
    {
      id: 2,
      name: "Elysian Ventures",
      type: "Due Diligence",
      documents: 32,
      team: 5,
    },
  ]

  return (
    <Card className="overflow-hidden backdrop-blur-sm">
      <CardHeader className="border-b bg-white/5 p-6">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Briefcase className="h-5 w-5" />
          Project Knowledge
        </CardTitle>
      </CardHeader>
      <CardContent className="p-6">
        <div className="space-y-4">
          {projects.map((project) => (
            <div key={project.id} className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-medium text-[#1C1C1C]">{project.name}</span>
                <span className="rounded-full bg-[#9FE870]/20 px-2 py-1 text-xs text-[#09332B]">{project.type}</span>
              </div>
              <div className="flex gap-4">
                <div className="flex items-center gap-1 text-sm text-[#8992A9]">
                  <FileText className="h-4 w-4" />
                  {project.documents} docs
                </div>
                <div className="flex items-center gap-1 text-sm text-[#8992A9]">
                  <Users className="h-4 w-4" />
                  {project.team} members
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}


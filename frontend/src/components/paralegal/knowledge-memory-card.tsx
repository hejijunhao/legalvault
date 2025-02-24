// src/components/paralegal/knowledge-memory-card.tsx

import type React from "react"
import { Card } from "@/components/ui/card"
import { Brain, Globe2, GraduationCap, MessageSquare, CheckSquare } from "lucide-react"

export function KnowledgeMemoryCard() {
  return (
    <Card className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-gray-50 to-gray-100 border-none shadow-lg hover:shadow-xl transition-all duration-300">
      <div className="relative p-6 space-y-6">
        <h3 className="text-lg font-medium text-gray-800 tracking-wider">KNOWLEDGE & MEMORY</h3>

        {/* Memory Stats */}
        <div className="space-y-3">
          <MemoryBlock
            icon={Brain}
            label="Self Identity"
            stats={[
              { label: "Core", value: 95 },
              { label: "Adaptive", value: 88 },
            ]}
            color="bg-blue-500"
          />
          <MemoryBlock
            icon={Globe2}
            label="General Knowledge"
            stats={[
              { label: "Domain", value: 92 },
              { label: "Context", value: 85 },
            ]}
            color="bg-emerald-500"
          />
          <MemoryBlock
            icon={GraduationCap}
            label="Legal Education"
            stats={[
              { label: "Theory", value: 90 },
              { label: "Practice", value: 88 },
            ]}
            color="bg-violet-500"
          />
          <MemoryBlock
            icon={MessageSquare}
            label="Conversation Memories"
            stats={[
              { label: "Recall", value: 94 },
              { label: "Apply", value: 89 },
            ]}
            color="bg-amber-500"
          />
          <MemoryBlock
            icon={CheckSquare}
            label="Task Memories"
            stats={[
              { label: "Process", value: 91 },
              { label: "Execute", value: 87 },
            ]}
            color="bg-rose-500"
          />
        </div>
      </div>
    </Card>
  )
}

type MemoryBlockProps = {
  icon: React.ElementType
  label: string
  stats: Array<{ label: string; value: number }>
  color: string
}

function MemoryBlock({ icon: Icon, label, stats, color }: MemoryBlockProps) {
  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-xl p-3 hover:bg-white transition-colors duration-200 shadow-sm">
      <div className="flex items-center justify-between text-gray-800 mb-2">
        <div className="flex items-center space-x-2">
          <Icon className="w-4 h-4 text-gray-600" />
          <span className="text-xs font-medium">{label}</span>
        </div>
        <div className="flex items-center space-x-4">
          {stats.map((stat, index) => (
            <div key={stat.label} className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${color} opacity-70`} />
              <span className="text-xs text-gray-600">{stat.value}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

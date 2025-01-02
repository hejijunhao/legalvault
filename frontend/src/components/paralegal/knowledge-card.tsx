// components/paralegal/knowledge-card.tsx
"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ChevronRight, Atom } from 'lucide-react'
import type { VPKnowledge } from "@/types/paralegal"

interface KnowledgeCardProps {
  knowledge: VPKnowledge;
}

export default function KnowledgeCard({ knowledge }: KnowledgeCardProps) {
  return (
    <Card className="border-gray-200 bg-white/50 backdrop-blur-sm shadow-sm">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-primary">Knowledge</CardTitle>
        <ChevronRight className="h-5 w-5 text-gray-500" />
      </CardHeader>
      <CardContent>
        <div className="flex items-center space-x-4">
          <Atom className="h-8 w-8 text-blue-500" />
          <div className="flex-1">
            <div className="mb-2 flex justify-between">
              <span className="text-sm font-medium text-gray-700">Legal Expertise</span>
              <span className="text-sm text-gray-400">Level {knowledge.level}</span>
            </div>
            <div className="h-2 rounded-full bg-gray-100">
              <div
                className="h-2 rounded-full bg-primary"
                style={{ width: `${knowledge.progress}%` }}
              />
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
// src/components/abilities/ability-boxes.tsx

"use client"

import { Card } from "@/components/ui/card"
import Link from "next/link"

const abilities = [
  {
    id: "communication",
    name: "Communication",
    gradient: "from-[#9FE870]/20 to-[#BFE999]/20",
    description: "Email and chat capabilities",
  },
  {
    id: "project-management",
    name: "Project Management",
    gradient: "from-[#AF52DE]/20 to-[#E5A4FF]/20",
    description: "Task tracking, deadlines, and resource allocation",
  },
  {
    id: "library",
    name: "Library",
    gradient: "from-[#FF9B9B]/20 to-[#FFC4C4]/20",
    description: "Document management and organization",
  },
  {
    id: "research",
    name: "Research",
    gradient: "from-[#00C7BE]/20 to-[#7DEAE5]/20",
    description: "Legal research and analysis tools",
  },
  {
    id: "legal",
    name: "Legal",
    gradient: "from-[#93C5FD]/20 to-[#BFDBFE]/20",
    description: "Core legal processing capabilities",
  },
  {
    id: "analytical",
    name: "Analytical",
    gradient: "from-[#FCD34D]/20 to-[#FDE68A]/20",
    description: "Data analysis and pattern recognition",
  },
]

export function AbilityBoxes() {
  return (
    <div className="flex w-full space-x-4 overflow-x-auto pb-4">
      {abilities.map((ability) => (
        <Link key={ability.id} href={`/abilities/${ability.id}`} className="flex-1 min-w-[200px]">
          <Card
            className={`group h-[250px] cursor-pointer flex flex-col justify-end rounded-[10px] border border-white/10 bg-gradient-to-br p-6 backdrop-blur-[17.7px] transition-all duration-500 ease-in-out hover:h-[400px] ${ability.gradient}`}
          >
            <div className="space-y-2 transition-all duration-500">
              <h3 className="font-medium text-[#1C1C1C] italic font-['Libre_Baskerville']">{ability.name}</h3>
              <p className="text-sm text-[#525766] opacity-0 transition-opacity duration-500 group-hover:opacity-100">
                {ability.description}
              </p>
            </div>
          </Card>
        </Link>
      ))}
    </div>
  )
}


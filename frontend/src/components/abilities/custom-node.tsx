// src/components/abilities/custom-node.tsx

import { Handle, Position } from "reactflow"
import { Lock } from "lucide-react"
import type { AbilityStatus } from "@/lib/ability-data"

interface CustomNodeProps {
  data: {
    name: string
    description: string
    status: AbilityStatus
    gradient: string
  }
}

export function CustomNode({ data }: CustomNodeProps) {
  const isLocked = data.status === "locked"
  const isActive = data.status === "active"

  return (
    <div
      className={`group relative h-[150px] w-[300px] cursor-pointer overflow-hidden rounded-xl border border-white/30 bg-gradient-to-br p-6 backdrop-blur-md transition-all duration-300 ${
        data.gradient
      } ${isLocked ? "opacity-50" : ""}`}
    >
      <Handle type="target" position={Position.Top} className="!bg-transparent" style={{ opacity: 0 }} />
      <Handle type="source" position={Position.Bottom} className="!bg-transparent" style={{ opacity: 0 }} />

      {/* Subtle gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-white/10 to-transparent" />

      {/* Content */}
      <div className="relative z-10 flex h-full flex-col justify-between">
        <h3 className="font-medium text-[#1C1C1C] italic font-['Libre_Baskerville']">{data.name}</h3>
        <p className="text-sm text-[#525766]">{data.description}</p>
      </div>

      {/* Lock overlay */}
      {isLocked && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/10 backdrop-blur-[2px]">
          <div className="rounded-full bg-white/10 p-2">
            <Lock className="h-6 w-6 text-white/90" />
          </div>
        </div>
      )}
    </div>
  )
}



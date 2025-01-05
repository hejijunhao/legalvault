// src/components/abilities/ability-node.tsx

"use client"

interface AbilityNodeProps {
  ability: {
    id: string
    name: string
    x: number
    y: number
    unlocked?: boolean
    children?: string[]
  }
  onClick: () => void
}

export function AbilityNode({ ability, onClick }: AbilityNodeProps) {
  const isCore = ability.id === "core"
  const isMainBranch = ability.children && ability.children.length > 0 && !isCore
  const radius = isCore ? 50 : isMainBranch ? 40 : 30

  return (
    <g
      transform={`translate(${ability.x}, ${ability.y})`}
      className="cursor-pointer transition-all duration-300 hover:opacity-80"
      onClick={onClick}
    >
      {/* Decorative outer ring */}
      <circle
        r={radius + 2}
        className={`
          fill-none
          ${ability.unlocked ? "stroke-[#9FE870]" : "stroke-[#8992A9]"}
          stroke-[0.5px] opacity-20
        `}
      />

      {/* Main node circle */}
      <circle
        r={radius}
        className={`
          ${ability.unlocked ? "fill-[#9FE870] stroke-[#09332B]" : "fill-[#8992A9] stroke-[#525766]"}
          stroke-2
        `}
      />

      {/* Inner glow */}
      <circle
        r={radius - 2}
        className={`
          fill-none
          ${ability.unlocked ? "stroke-[#9FE870]" : "stroke-[#8992A9]"}
          stroke-[0.5px] opacity-20
        `}
      />

      {/* Text label */}
      <text
        y={radius + 15}
        textAnchor="middle"
        className={`
          fill-[#8992A9] text-center font-inter font-normal leading-4
          ${ability.unlocked ? "fill-[#525766]" : "fill-[#8992A9]"}
          ${isCore ? "text-sm" : isMainBranch ? "text-xs" : "text-[10px]"}
        `}
      >
        {ability.name.split(' ').map((word, index, array) => (
          <tspan key={index} x="0" dy={index ? "1.2em" : 0}>
            {word}
          </tspan>
        ))}
      </text>
    </g>
  )
}
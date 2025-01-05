// src/components/abilities/connection-lines.tsx

"use client"

interface Ability {
  id: string;
  name: string;
  x: number;
  y: number;
  unlocked?: boolean;
  children?: string[];
}

interface ConnectionLinesProps {
  abilities: Ability[];
}

export function ConnectionLines({ abilities }: ConnectionLinesProps) {
  const firstOrderNodes = abilities.filter(a => a.id !== "core" && a.children?.length > 0)
  const radius = 220 // Radius of the circle connecting first order nodes

  return (
    <g>
      {/* Circle connecting first order nodes */}
      <circle
        cx="0"
        cy="0"
        r={radius}
        fill="none"
        className="stroke-[#8992A9] stroke-[1px] opacity-30"
      />

      {/* Decorative circles */}
      <circle
        cx="0"
        cy="0"
        r={radius - 2}
        fill="none"
        className="stroke-[#8992A9] stroke-[0.5px] opacity-20"
      />
      <circle
        cx="0"
        cy="0"
        r={radius + 2}
        fill="none"
        className="stroke-[#8992A9] stroke-[0.5px] opacity-20"
      />

      {/* Connections to sub-abilities */}
      {abilities.map((ability) => (
        ability.children?.map(childId => {
          const child = abilities.find(a => a.id === childId)
          if (!child || ability.id === "core") return null

          // Calculate control points for the curve
          const dx = child.x - ability.x
          const dy = child.y - ability.y
          const midX = ability.x + dx * 0.5
          const midY = ability.y + dy * 0.5

          // Add some curvature based on the distance
          const curvature = 0.2
          const normalX = -dy * curvature
          const normalY = dx * curvature

          return (
            <g key={`${ability.id}-${childId}`}>
              {/* Main connection line */}
              <path
                d={`M ${ability.x} ${ability.y} Q ${midX + normalX} ${midY + normalY} ${child.x} ${child.y}`}
                fill="none"
                className={`
                  stroke-[#8992A9] stroke-[1.5px]
                  ${ability.unlocked && child.unlocked ? 'opacity-50' : 'opacity-30'}
                `}
              />

              {/* Glow effect */}
              <path
                d={`M ${ability.x} ${ability.y} Q ${midX + normalX} ${midY + normalY} ${child.x} ${child.y}`}
                fill="none"
                className={`
                  stroke-[#8992A9] stroke-[0.5px] blur-[1px]
                  ${ability.unlocked && child.unlocked ? 'opacity-30' : 'opacity-10'}
                `}
              />

              {/* Connection point decorations */}
              <circle
                cx={ability.x}
                cy={ability.y}
                r="3"
                className={`
                  fill-[#8992A9]
                  ${ability.unlocked ? 'opacity-50' : 'opacity-30'}
                `}
              />
              <circle
                cx={child.x}
                cy={child.y}
                r="3"
                className={`
                  fill-[#8992A9]
                  ${child.unlocked ? 'opacity-50' : 'opacity-30'}
                `}
              />
            </g>
          )
        })
      ))}
    </g>
  )
}
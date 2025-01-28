// src/components/abilities/ability-node.tsx

interface AbilityNodeProps {
  name: string
  description: string
  unlocked: boolean
  gradient: string
}

export function AbilityNode({ name, description, unlocked, gradient }: AbilityNodeProps) {
  return (
    <div
      className={`group relative h-[150px] w-[300px] cursor-pointer overflow-hidden rounded-xl border border-white/10 bg-gradient-to-br p-6 backdrop-blur-md transition-all duration-300 hover:scale-105 ${gradient} ${
        !unlocked && "opacity-50"
      }`}
    >
      {/* Glow effect */}
      <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-white/0" />

      {/* Content */}
      <div className="relative z-10 flex h-full flex-col justify-between">
        <h3 className="font-medium text-[#1C1C1C] italic font-['Libre_Baskerville']">{name}</h3>
        <p className="text-sm text-[#525766]">{description}</p>
      </div>

      {/* Lock overlay */}
      {!unlocked && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/20 backdrop-blur-sm">
          <div className="rounded-full bg-white/10 p-2">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="text-white"
            >
              <rect width="18" height="11" x="3" y="11" rx="2" ry="2" />
              <path d="M7 11V7a5 5 0 0 1 10 0v4" />
            </svg>
          </div>
        </div>
      )}
    </div>
  )
}


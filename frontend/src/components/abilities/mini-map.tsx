// src/components/abilities/mini-map.tsx

interface MiniMapProps {
  currentZoom: number
  currentCenter: { x: number; y: number }
}

export function MiniMap({ currentZoom, currentCenter }: MiniMapProps) {
  return (
    <div className="rounded-lg border border-white/10 bg-black/50 p-2">
      <div className="h-32 w-32">
        {/* Mini representation of the ability tree */}
        <div className="relative h-full w-full">
          <div className="absolute inset-0 rounded border border-white/20" />
          <div
            className="absolute bg-white/10"
            style={{
              left: `${50 + (currentCenter.x / currentZoom)}%`,
              top: `${50 + (currentCenter.y / currentZoom)}%`,
              width: `${100 / currentZoom}%`,
              height: `${100 / currentZoom}%`,
              transform: "translate(-50%, -50%)",
            }}
          />
        </div>
      </div>
    </div>
  )
}


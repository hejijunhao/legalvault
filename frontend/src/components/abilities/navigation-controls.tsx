// src/components/abilities/navigation-controls.tsx

import { Minus, Plus, RotateCcw } from 'lucide-react'
import { Button } from "@/components/ui/button"

interface NavigationControlsProps {
  zoom: number
  onZoomIn: () => void
  onZoomOut: () => void
  onReset: () => void
}

export function NavigationControls({
                                     zoom,
                                     onZoomIn,
                                     onZoomOut,
                                     onReset,
                                   }: NavigationControlsProps) {
  return (
    <div className="flex items-center gap-2">
      <Button
        variant="outline"
        size="icon"
        onClick={onZoomOut}
        disabled={zoom <= 0.5}
        className="border-white/10 bg-black/50 hover:bg-white/10"
      >
        <Minus className="h-4 w-4 text-white" />
      </Button>
      <Button
        variant="outline"
        size="icon"
        onClick={onZoomIn}
        disabled={zoom >= 2}
        className="border-white/10 bg-black/50 hover:bg-white/10"
      >
        <Plus className="h-4 w-4 text-white" />
      </Button>
      <Button
        variant="outline"
        size="icon"
        onClick={onReset}
        className="border-white/10 bg-black/50 hover:bg-white/10"
      >
        <RotateCcw className="h-4 w-4 text-white" />
      </Button>
    </div>
  )
}
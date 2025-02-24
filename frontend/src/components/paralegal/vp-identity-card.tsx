// src/components/paralegal/vp-identity-card.tsx

import { Card } from "@/components/ui/card"
import { Shield } from "lucide-react"

export function VPIdentityCard() {
  return (
    <Card className="relative overflow-hidden rounded-3xl border-none w-[340px] h-[215px] group">
      {/* Background gradients and effects */}
      <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/90 via-teal-500/80 to-cyan-500/90">
        {/* Animated gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent animate-shimmer" />

        {/* Neon glow effects */}
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(255,255,255,0.1),transparent_70%)]" />
          <div className="absolute inset-0 bg-[linear-gradient(45deg,transparent,rgba(255,255,255,0.1)_50%,transparent)] animate-pulse" />
        </div>
      </div>

      {/* Glassmorphism card overlay */}
      <div className="absolute inset-0 backdrop-blur-sm bg-black/10" />

      {/* Content wrapper */}
      <div className="relative h-full p-4 flex flex-col justify-between">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-6 h-6 relative">
              <LegalVaultLogo />
              <div className="absolute inset-0 blur-sm opacity-50 animate-pulse" />
            </div>
            <span className="text-xs font-medium text-white/90 tracking-[0.2em] drop-shadow-glow">
              VIRTUAL PARALEGAL
            </span>
          </div>
          <div className="h-8 w-8 rounded-full bg-white/10 backdrop-blur-md flex items-center justify-center">
            <Shield className="w-4 h-4 text-white/70" />
          </div>
        </div>

        {/* Main content */}
        <div className="space-y-3">
          {/* VP ID */}
          <p className="font-mono text-sm tracking-[0.25em] text-white/80 drop-shadow-glow">VP-2023-1002-RM</p>

          {/* Name */}
          <p className="text-xl font-medium tracking-wider text-white drop-shadow-glow">ROBERT MCNAMARA</p>

          {/* Practice date */}
          <div className="flex items-center space-x-2">
            <span className="text-xs text-white/70 tracking-wider">PRACTICING SINCE 01/2023</span>
          </div>
        </div>
      </div>

      {/* Hover effects */}
      <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-700">
        <div className="absolute inset-0 bg-gradient-to-tr from-white/5 via-white/10 to-transparent" />
      </div>
    </Card>
  )
}

function LegalVaultLogo() {
  return (
    <svg viewBox="0 0 24 24" fill="none" className="text-white/90">
      <path
        d="M12 2L2 7V17L12 22L22 17V7L12 2Z"
        stroke="currentColor"
        strokeWidth="2"
        fill="currentColor"
        fillOpacity="0.2"
      />
    </svg>
  )
}




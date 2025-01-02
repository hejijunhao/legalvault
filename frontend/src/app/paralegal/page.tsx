// app/paralegal/page.tsx
"use client"

import { Scale } from 'lucide-react'
import { Button } from "@/components/ui/button"
import ProfileCard from "@/components/paralegal/profile-card"
import AbilitiesCard from "@/components/paralegal/abilities-card"
import BehaviorsCard from "@/components/paralegal/behaviors-card"
import KnowledgeCard from "@/components/paralegal/knowledge-card"
import AccessCard from "@/components/paralegal/access-card"
import { useVPStore } from "@/store/vp-store"

export default function ParalegalProfile() {
  const { profile, abilities, behaviors, knowledge, access } = useVPStore()

  return (
    <div className="min-h-screen bg-[#EFF2F5]">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white/50 backdrop-blur-sm">
        <div className="container flex h-16 items-center justify-between px-4">
          <div className="flex items-center space-x-4">
            <Scale className="h-6 w-6 text-primary" />
            <span className="text-lg font-bold text-gray-900">LegalVault</span>
          </div>
          <nav className="flex items-center space-x-4">
            <Button variant="ghost">Workspace</Button>
            <Button variant="ghost">Library</Button>
            <Button variant="ghost">Paralegal</Button>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="container px-4 py-8">
        <div className="grid gap-8 lg:grid-cols-[300px_1fr]">
          {/* Left Column - Profile */}
          <div className="space-y-4">
            <ProfileCard profile={profile} />
          </div>

          {/* Right Column - Stats & Abilities */}
          <div className="space-y-4">
            <AbilitiesCard abilities={abilities} />
            <BehaviorsCard behaviors={behaviors} />
            <KnowledgeCard knowledge={knowledge} />
            <AccessCard access={access} />
          </div>
        </div>
      </main>
    </div>
  )
}
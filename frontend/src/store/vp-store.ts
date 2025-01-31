// src/store/vp-store.ts

import { create } from 'zustand'
import type { VPState, VPProfile, VPAbility, VPBehavior, VPKnowledge, VPAccess } from '@/types/paralegal'

interface VPStore extends VPState {
  setProfile: (profile: VPProfile) => void
  setAbilities: (abilities: VPAbility[]) => void
  setBehaviors: (behaviors: VPBehavior[]) => void
  setKnowledge: (knowledge: VPKnowledge) => void
  setAccess: (access: VPAccess[]) => void
}

export const useVPStore = create<VPStore>((set) => ({
  // Initial state - using the same mock data structure
  profile: {
    name: "Lisa Chen",
    email: "lisa.chen@gmail.com",
    level: 40,
    avatar: "/placeholder.svg"
  },
  abilities: [
    {
      id: "1",
      name: "Research",
      description: "Legal Research Proficiency",
      icon: "search",
      status: "active"
    },
    {
      id: "2",
      name: "Drafting",
      description: "Document Drafting",
      icon: "fileText",
      status: "active"
    }
  ],
  behaviors: [
    {
      id: "1",
      name: "Efficient",
      icon: "timer",
      color: "yellow-500"
    }
  ],
  knowledge: {
    level: 85,
    progress: 85,
    areas: []
  },
  access: [
    {
      id: "1",
      name: "Courts",
      icon: "gavel",
      status: "granted"
    }
  ],

  // Actions
  setProfile: (profile) => set({ profile }),
  setAbilities: (abilities) => set({ abilities }),
  setBehaviors: (behaviors) => set({ behaviors }),
  setKnowledge: (knowledge) => set({ knowledge }),
  setAccess: (access) => set({ access }),
}))
// src/components/abilities/ability-tree.tsx

"use client"

import { AbilityNode } from "./ability-node"
import { ConnectionLines } from "./connection-lines"

interface AbilityTreeProps {
  onNodeClick: (nodeId: string) => void
}

const abilities = [
  { id: "core", name: "Core", x: 0, y: 0, children: ["communication", "task", "calendar", "document", "client"], unlocked: true },

  { id: "communication", name: "Communication Management", x: 0, y: -220, children: ["email", "instant_messaging"], unlocked: true },
  { id: "email", name: "Email", x: -100, y: -320, unlocked: true },
  { id: "instant_messaging", name: "Instant Messaging", x: 100, y: -320, unlocked: false },

  { id: "task", name: "Task Management", x: 209, y: -68, children: ["create_tasks", "track_tasks", "organise_tasks"], unlocked: true },
  { id: "create_tasks", name: "Create tasks", x: 309, y: -168, unlocked: true },
  { id: "track_tasks", name: "Track tasks", x: 379, y: -68, unlocked: true },
  { id: "organise_tasks", name: "Organise tasks", x: 309, y: 32, unlocked: false },

  { id: "calendar", name: "Calendar", x: 129, y: 178, children: ["schedule_events", "manage_events", "availability_checks"], unlocked: false },
  { id: "schedule_events", name: "Schedule events", x: 229, y: 278, unlocked: false },
  { id: "manage_events", name: "Manage events", x: 299, y: 178, unlocked: false },
  { id: "availability_checks", name: "Availability checks", x: 229, y: 78, unlocked: false },

  { id: "document", name: "Document Management", x: -129, y: 178, children: ["find_documents", "file_documents"], unlocked: false },
  { id: "find_documents", name: "Find Documents", x: -229, y: 278, unlocked: false },
  { id: "file_documents", name: "File Documents", x: -29, y: 278, unlocked: false },

  { id: "client", name: "Client Management", x: -209, y: -68, children: ["client_profiles", "interaction_logging", "document_tagging"], unlocked: false },
  { id: "client_profiles", name: "Client Profiles", x: -309, y: -168, unlocked: false },
  { id: "interaction_logging", name: "Interaction Logging", x: -379, y: -68, unlocked: false },
  { id: "document_tagging", name: "Document Tagging", x: -309, y: 32, unlocked: false },
]

export function AbilityTree({ onNodeClick }: AbilityTreeProps) {
  return (
    <svg
      className="h-full w-full"
      viewBox="-450 -350 900 700"
      preserveAspectRatio="xMidYMid meet"
    >
      <ConnectionLines abilities={abilities} />
      {abilities.map((ability) => (
        <AbilityNode
          key={ability.id}
          ability={ability}
          onClick={() => onNodeClick(ability.id)}
        />
      ))}
    </svg>
  )
}
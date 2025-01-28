// placeholder for actual abilityTreeVisualiser class in lib/ability-data.ts

export type AbilityStatus = "active" | "locked" | "available"

export interface AbilityNode {
  id: string
  name: string
  description: string
  level: number
  prerequisites: string[]
  status: AbilityStatus
}

export interface AbilityTree {
  name: string
  description: string
  gradient: string
  nodes: AbilityNode[]
}

export const abilityTrees: Record<string, AbilityTree> = {
  communication: {
    name: "Communication",
    description: "Review your Virtual Paralegal's communication abilities.",
    gradient: "from-[#9FE870]/20 to-[#BFE999]/20",
    nodes: [
      {
        id: "email",
        name: "Email Processing",
        description: "Process and understand email content",
        level: 1,
        prerequisites: [],
        status: "active",
      },
      {
        id: "summarization",
        name: "Email Summarization",
        description: "Create concise email summaries",
        level: 2,
        prerequisites: ["email"],
        status: "active",
      },
      {
        id: "drafting",
        name: "Email Drafting",
        description: "Draft professional emails",
        level: 2,
        prerequisites: ["email"],
        status: "locked",
      },
      {
        id: "auto-categorize",
        name: "Auto-Categorization",
        description: "Automatically categorize emails by type",
        level: 3,
        prerequisites: ["summarization"],
        status: "locked",
      },
      {
        id: "templates",
        name: "Template Management",
        description: "Create and manage email templates",
        level: 3,
        prerequisites: ["drafting"],
        status: "locked",
      },
      {
        id: "multi-language",
        name: "Multi-Language Support",
        description: "Draft emails in multiple languages",
        level: 3,
        prerequisites: ["drafting"],
        status: "locked",
      },
      {
        id: "advanced-templates",
        name: "Advanced Templates",
        description: "Dynamic and context-aware templates",
        level: 4,
        prerequisites: ["templates"],
        status: "locked",
      },
    ],
  },
  // Add other ability trees here
}
// // src/components/workspace/project-tabs.tsx

"use client"

import * as React from "react"
import * as TabsPrimitive from "@radix-ui/react-tabs"
import { cn } from "@/lib/utils"
import { motion, AnimatePresence } from "framer-motion"

const tabBackgrounds = {
  knowledge: "bg-blue-50/20",
  summary: "bg-purple-50/20",
  files: "bg-green-50/20",
  calendar: "bg-yellow-50/20",
  communications: "bg-pink-50/20",
  contacts: "bg-indigo-50/20",
  activity: "bg-orange-50/20"
}

interface Tab {
  id: string
  label: string
  content: React.ReactNode
}

interface ProjectTabsProps {
  tabs: Tab[]
  defaultTab?: string
}

export function ProjectTabs({ tabs, defaultTab = "knowledge" }: ProjectTabsProps) {
  const [activeTab, setActiveTab] = React.useState(defaultTab)

  return (
    <TabsPrimitive.Root
      value={activeTab}
      onValueChange={setActiveTab}
      className="flex h-full flex-col"
    >
      <TabsPrimitive.List
        className="relative flex gap-1 overflow-hidden rounded-t-xl bg-white/5 p-1"
      >
        {tabs.map((tab) => (
          <TabsPrimitive.Trigger
            key={tab.id}
            value={tab.id}
            className={cn(
              "relative z-10 rounded-t-lg px-4 py-2 text-[10px] font-light tracking-[1px] font-inter",
              "data-[state=active]:text-[#1C1C1C]",
              "data-[state=inactive]:text-[#525766] data-[state=inactive]:hover:text-[#1C1C1C]/80",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2",
              "select-none uppercase"
            )}
          >
            {tab.label}
            {activeTab === tab.id && (
              <motion.div
                layoutId="activeTab"
                className={cn(
                  "absolute inset-0 -z-10 rounded-t-lg",
                  tabBackgrounds[tab.id as keyof typeof tabBackgrounds]
                )}
                transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
              />
            )}
          </TabsPrimitive.Trigger>
        ))}
      </TabsPrimitive.List>
      <TabsPrimitive.Content
        value={activeTab}
        className={cn(
          "flex-1 rounded-b-xl p-6",
          tabBackgrounds[activeTab as keyof typeof tabBackgrounds]
        )}
      >
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
          >
            {tabs.find(tab => tab.id === activeTab)?.content}
          </motion.div>
        </AnimatePresence>
      </TabsPrimitive.Content>
    </TabsPrimitive.Root>
  )
}
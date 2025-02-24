// src/app/(app)/paralegal/page.tsx

"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { cn } from "@/lib/utils"
import Image from "next/image"
import { ChatInput } from "@/components/paralegal/chat-input"
import { ActivityBlock } from "@/components/paralegal/activity-block"

type Section = "profile" | "knowledge" | "abilities" | "integrations"

export default function ParalegalPage() {
  const [selectedSection, setSelectedSection] = useState<Section>("profile")

  const sections = [
    { id: "profile", label: "Profile Overview" },
    { id: "knowledge", label: "Knowledge & Memory" },
    { id: "abilities", label: "Abilities" },
    { id: "integrations", label: "Integrations" },
  ] as const

  return (
    <div className="relative mx-auto min-h-[calc(100vh-4rem)] max-w-[1440px] overflow-hidden">
      <div className="grid grid-cols-[300px_1fr] gap-12">
        {/* Navigation Menu */}
        <nav className="relative z-10 flex flex-col space-y-6 p-12">
          {sections.map(({ id, label }) => (
            <button
              key={id}
              onClick={() => setSelectedSection(id)}
              className={cn(
                "w-fit text-left transition-all duration-300",
                selectedSection === id
                  ? "font-['Libre_Baskerville'] text-3xl italic text-gray-900"
                  : "font-inter text-base text-gray-600 hover:text-gray-900",
              )}
            >
              {label}
            </button>
          ))}
        </nav>

        {/* Content Section */}
        <div className="relative flex flex-col min-h-[calc(100vh-4rem)] pt-[220px]">
          {/* Activity Block */}
          {selectedSection === "profile" && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="absolute top-12 right-8 w-[600px]"
            >
              <ActivityBlock />
            </motion.div>
          )}

          {/* Portrait Section */}
          <div className="absolute bottom-0 left-[-200px] w-[calc(100%-300px)]">
            <div className="relative h-[calc(100vh-4rem)] w-full">
              <Image
                src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/Virtual%20Paralegals-fie2JYdrbgShF29etJsoiieb2v8SUT.svg"
                alt="Virtual Paralegal Portrait"
                layout="fill"
                objectFit="contain"
                objectPosition="bottom left"
                priority
              />
            </div>
          </div>
        </div>
      </div>

      {/* Chat Input */}
      <div className="fixed bottom-8 right-8 z-50">
        <ChatInput />
      </div>
    </div>
  )
}


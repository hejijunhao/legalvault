// src/app/(app)/paralegal/page.tsx

"use client"

import { useState } from "react"
import { cn } from "@/lib/utils"
import Image from "next/image"

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

        {/* Portrait Section */}
        <div className="relative min-h-[calc(100vh-4rem)]">
          <div className="absolute left-[-150px] top-0 h-full w-[700px]">
            <Image
              src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/Virtual%20Paralegals-fie2JYdrbgShF29etJsoiieb2v8SUT.svg"
              alt="Virtual Paralegal Portrait"
              fill
              className="object-cover object-left"
              priority
            />
          </div>
        </div>
      </div>
    </div>
  )
}


// src/app/(app)/paralegal/wip/page.tsx

"use client"

import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { cn } from "@/lib/utils"
import { Loader2 } from "lucide-react"
import { ParalegalProfile } from "@/components/paralegal/paralegal-profile"
import { paralegalService } from "@/services/paralegal/paralegal-api"
import { VirtualParalegalResponse, ParalegalNotFoundError } from "@/services/paralegal/paralegal-api-types"
import { Button } from "@/components/ui/button"

type Section = "profile" | "knowledge" | "abilities" | "integrations"

export default function ParalegalPage() {
  const [selectedSection, setSelectedSection] = useState<Section>("profile")
  const [paralegal, setParalegal] = useState<VirtualParalegalResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Sections configuration with disabled state
  const sections = [
    { id: "profile" as const, label: "Profile Overview", disabled: false },
    { id: "knowledge" as const, label: "Knowledge & Memory", disabled: true },
    { id: "abilities" as const, label: "Abilities", disabled: true },
    { id: "integrations" as const, label: "Integrations", disabled: true },
  ]

  // Fetch paralegal data
  useEffect(() => {
    const fetchParalegal = async () => {
      try {
        const data = await paralegalService.getMyParalegal()
        setParalegal(data)
        setError(null)
      } catch (err) {
        if (err instanceof ParalegalNotFoundError) {
          setError("No Virtual Paralegal assigned. Please configure one first.")
        } else {
          setError("Failed to load Virtual Paralegal data.")
        }
      } finally {
        setLoading(false)
      }
    }

    fetchParalegal()
  }, [])

  // Loading state
  if (loading) {
    return (
      <div className="flex h-[calc(100vh-4rem)] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-gray-500" />
      </div>
    )
  }

  // Error state with retry option
  if (error) {
    return (
      <div className="flex h-[calc(100vh-4rem)] flex-col items-center justify-center gap-4">
        <p className="text-gray-600">{error}</p>
        <Button
          onClick={() => {
            setLoading(true)
            setError(null)
            paralegalService.getMyParalegal()
              .then(data => {
                setParalegal(data)
                setError(null)
              })
              .catch(() => setError("Failed to load Virtual Paralegal data."))
              .finally(() => setLoading(false))
          }}
        >
          Retry
        </Button>
      </div>
    )
  }

  return (
    <div className="relative mx-auto min-h-[calc(100vh-4rem)] w-full">
      {/* Header Section */}
      <div className="sticky top-0 z-10 h-24 w-full border-b bg-white/80 backdrop-blur-sm">
        <div className="mx-auto flex h-full max-w-[1440px] items-center px-8">
          <nav className="flex space-x-12">
            {sections.map(({ id, label, disabled }) => (
              <button
                key={id}
                onClick={() => !disabled && setSelectedSection(id)}
                className={cn(
                  "relative transition-all duration-300",
                  selectedSection === id
                    ? "font-['Libre_Baskerville'] text-xl italic text-gray-900"
                    : "font-inter text-base text-gray-600 hover:text-gray-900",
                  disabled && "cursor-not-allowed opacity-50 hover:text-gray-600"
                )}
                disabled={disabled}
                title={disabled ? "Coming soon" : undefined}
              >
                {label}
                {selectedSection === id && (
                  <motion.div
                    layoutId="activeSection"
                    className="absolute -bottom-[25px] left-0 right-0 h-px bg-gray-900"
                    transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                  />
                )}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <div className="mx-auto max-w-[1440px] px-8 py-12">
        {paralegal && selectedSection === "profile" && (
          <ParalegalProfile paralegal={paralegal} />
        )}
      </div>
    </div>
  )
}
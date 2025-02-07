// src/components/ui/back-button.tsx

"use client"

import { useRouter } from "next/navigation"
import { ChevronLeft } from "lucide-react"
import { useEffect, useState } from "react"
import { getDisplayNameFromPath, formatBackLinkText } from "@/lib/navigation"

export function BackButton() {
  const router = useRouter()
  const [backText, setBackText] = useState("Back")

  useEffect(() => {
    const previousPath = document.referrer
    const displayName = getDisplayNameFromPath(previousPath || "/library")
    setBackText(formatBackLinkText(displayName))
  }, [])

  const handleBack = () => {
    if (window.history.length > 2) {
      router.back()
    } else {
      router.push("/library")
    }
  }

  return (
    <button
      onClick={handleBack}
      className="inline-flex items-center text-sm text-[#525766] transition-colors hover:text-[#1c1c1c]"
    >
      <ChevronLeft className="mr-1 h-4 w-4" />
      {backText}
    </button>
  )
}




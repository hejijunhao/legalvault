// src/components/paralegal/chat-input.tsx

"use client"

import { useState } from "react"
import { ArrowRight } from "lucide-react"
import { cn } from "@/lib/utils"

export function ChatInput() {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <div className="fixed bottom-0 w-full max-w-[1440px] left-1/2 -translate-x-1/2 px-8 pb-8">
      <div
        className="ml-auto w-[600px]"
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        <div
          className={cn(
            "flex w-full items-center gap-4 rounded-full bg-white px-8 py-5 shadow-lg transition-all duration-300",
            isHovered ? "shadow-xl" : "",
          )}
        >
          <input
            type="text"
            placeholder="Ask your Paralegal"
            className="flex-1 border-none bg-transparent text-base outline-none placeholder:text-gray-500"
          />
          <button
            className={cn(
              "flex h-6 w-6 items-center justify-center transition-all duration-300",
              isHovered ? "bg-gray-100" : "",
            )}
          >
            <ArrowRight className="h-4 w-4 text-gray-600" />
          </button>
        </div>
      </div>
    </div>
  )
}


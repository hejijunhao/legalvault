// src/components/research/search/research-input.tsx

"use client"

import { useState, useRef, useEffect, useCallback } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { ArrowRight, Loader2, Gavel, BookText, Building2 } from "lucide-react"
import { useResearch, QueryType } from "@/contexts/research/research-context"
import { useAuth } from "@/contexts/auth-context"
import { cn } from "@/lib/utils"

interface ResearchInputProps {
  onSubmit: (content: string, type: QueryType) => Promise<void>
  isLoading: boolean
  searchId?: string
  disabled?: boolean
  isInitialQuery?: boolean
}

export function ResearchInput({
  onSubmit,
  isLoading: isLoadingProp,
  searchId,
  disabled = false,
  isInitialQuery = false,
}: ResearchInputProps) {
  const [input, setInput] = useState("")
  const [selectedType, setSelectedType] = useState<QueryType>(QueryType.GENERAL)
  const [isFocused, setIsFocused] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const router = useRouter()
  const { user } = useAuth()
  const { createSession } = useResearch()
  const [isCreating, setIsCreating] = useState(false)

  const MAX_LENGTH = 500

  const isLoading = isLoadingProp || isCreating

  const adjustTextareaHeight = useCallback(() => {
    const textarea = textareaRef.current
    if (textarea) {
      textarea.style.height = "auto"
      const newHeight = Math.min(textarea.scrollHeight, 200)
      textarea.style.height = `${newHeight}px`
    }
  }, [])

  useEffect(() => {
    adjustTextareaHeight()
  }, [input, adjustTextareaHeight])

  useEffect(() => {
    window.addEventListener("resize", adjustTextareaHeight)
    return () => window.removeEventListener("resize", adjustTextareaHeight)
  }, [adjustTextareaHeight])

  const isAtLimit = input.length >= MAX_LENGTH

  const toggleQueryType = (type: QueryType) => {
    setSelectedType(selectedType === type ? QueryType.GENERAL : type)
  }

  const handleInputChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(event.target.value)
  }

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const content = input.trim()
    if (!content || isLoading || isAtLimit || disabled) return

    if (isInitialQuery) {
      setIsCreating(true)
      try {
        const newSession = await createSession(content, { type: selectedType })
        if (newSession) {
          setInput("")
          setSelectedType(QueryType.GENERAL)
          router.push(
            `/research/${newSession}?initialQuery=${encodeURIComponent(content)}&queryType=${selectedType}`
          )
        } else {
          console.error("Failed to create research session.")
        }
      } catch (error) {
        console.error("Error creating research session:", error)
      } finally {
        setIsCreating(false)
      }
    } else if (searchId) {
      try {
        await onSubmit(content, selectedType)
        setInput("")
      } catch (error) {
        console.error("Error sending message:", error)
      }
    } else {
      console.warn("handleSubmit called without searchId and not as initial query.")
    }
  }

  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
      event.preventDefault()
      const form = event.currentTarget.form
      if (form) {
        form.requestSubmit()
      }
    }

    if (event.shiftKey && event.key === "Enter") {
      return
    }
  }

  return (
    <div className={cn(
      "fixed bottom-0 left-0 right-0 py-4 z-10",
      "transition-transform duration-200",
      disabled && "translate-y-full"
    )}>
      <form onSubmit={handleSubmit} className="mx-auto max-w-3xl px-4" aria-label="Research message form">
        <div className={cn(
          "flex flex-col rounded-2xl border bg-white p-4 shadow-[0_0_10px_rgba(0,0,0,0.05)] transition-all",
          isFocused ? "border-gray-300" : "border-gray-200"
        )}>
          <div className="relative">
            <Textarea
              ref={textareaRef}
              value={input}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              placeholder="Type your legal question here..."
              className={cn(
                "mb-3 w-full resize-none border-0 bg-transparent text-lg text-gray-900",
                "placeholder:text-gray-500 focus:outline-none focus:ring-0 focus-visible:outline-none focus-visible:ring-0 focus-visible:ring-offset-0",
                isAtLimit && "text-red-500",
                (isLoading || disabled) && "text-gray-500"
              )}
              style={{ minHeight: "24px", maxHeight: "200px" }}
              disabled={isLoading || disabled}
              aria-label="Research message input"
              aria-invalid={isAtLimit}
              maxLength={MAX_LENGTH}
            />
            {/* Character count removed */}
          </div>

          <div className="flex items-center justify-between gap-2 pt-2">
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => toggleQueryType(QueryType.COURT_CASE)}
                className={`flex items-center gap-2 rounded-full px-3 py-1.5 text-sm transition-colors ${
                  selectedType === QueryType.COURT_CASE
                    ? "bg-[#9FE870] text-[#1A2E0D]"
                    : "bg-gray-50 text-gray-600 hover:bg-gray-100"
                }`}
                aria-pressed={selectedType === QueryType.COURT_CASE}
                title="Search court cases and legal precedents"
                disabled={isLoading || disabled}
              >
                <Gavel className="h-4 w-4" />
                <span>Courts</span>
              </button>
              <button
                type="button"
                onClick={() => toggleQueryType(QueryType.LEGISLATIVE)}
                className={`flex items-center gap-2 rounded-full px-3 py-1.5 text-sm transition-colors ${
                  selectedType === QueryType.LEGISLATIVE
                    ? "bg-[#9FE870] text-[#1A2E0D]"
                    : "bg-gray-50 text-gray-600 hover:bg-gray-100"
                }`}
                aria-pressed={selectedType === QueryType.LEGISLATIVE}
                title="Search legislation, statutes and regulations"
                disabled={isLoading || disabled}
              >
                <BookText className="h-4 w-4" />
                <span>Legislative</span>
              </button>
              <button
                type="button"
                onClick={() => toggleQueryType(QueryType.COMMERCIAL)}
                className={`flex items-center gap-2 rounded-full px-3 py-1.5 text-sm transition-colors ${
                  selectedType === QueryType.COMMERCIAL
                    ? "bg-[#9FE870] text-[#1A2E0D]"
                    : "bg-gray-50 text-gray-600 hover:bg-gray-100"
                }`}
                aria-pressed={selectedType === QueryType.COMMERCIAL}
                title="Search commercial law and business regulations"
                disabled={isLoading || disabled}
              >
                <Building2 className="h-4 w-4" />
                <span>Commercial</span>
              </button>
            </div>

            <Button
              type="submit"
              disabled={!input.trim() || isLoading || isAtLimit || disabled}
              className={cn(
                "rounded-full p-2 transition-colors",
                input.trim() && !isLoading && !isAtLimit && !disabled
                  ? "bg-[#9FE870] text-[#1A2E0D] hover:bg-[#8ad460] cursor-pointer"
                  : "bg-gray-100 text-gray-400 cursor-not-allowed"
              )}
              aria-label={isLoading ? "Sending message" : "Send message"}
            >
              {isLoading ? (
                <Loader2 className="h-5 w-5 animate-spin" aria-hidden="true" />
              ) : (
                <ArrowRight className="h-5 w-5" aria-hidden="true" />
              )}
            </Button>
          </div>
        </div>
      </form>

      {isLoading && (
        <div className="mx-auto mt-2 max-w-3xl px-4 text-xs text-gray-500" aria-live="polite">
          Processing your request...
        </div>
      )}
    </div>
  )
}
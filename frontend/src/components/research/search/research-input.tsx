// src/components/research/search/research-input.tsx

"use client"

import { useState, useRef, useEffect } from "react"
import { Loader2, Send, Gavel, BookText, Building2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { toast } from "sonner"
import { cn } from "@/lib/utils"
import { QueryType } from "@/contexts/research/research-context"

interface ResearchInputProps {
  onSendMessage: (content: string, queryType?: QueryType | null) => Promise<void>
  isLoading: boolean
  maxLength?: number
  placeholder?: string
  disabled?: boolean
}

export function ResearchInput({
  onSendMessage,
  isLoading,
  maxLength = 2000,
  placeholder = "Type your legal question here...",
  disabled = false
}: ResearchInputProps) {
  const [input, setInput] = useState("")
  const [isAtLimit, setIsAtLimit] = useState(false)
  const [isFocused, setIsFocused] = useState(false)
  const [selectedType, setSelectedType] = useState<QueryType | null>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Update character limit status when input changes
  useEffect(() => {
    const trimmedLength = input.trim().length
    setIsAtLimit(trimmedLength >= maxLength)

    if (isAtLimit && trimmedLength >= maxLength) {
      toast.warning("You've reached the maximum character limit")
    }
  }, [input, maxLength, isAtLimit])

  // Auto-adjust textarea height
  useEffect(() => {
    const textarea = textareaRef.current
    if (textarea) {
      textarea.style.height = "auto"
      const newHeight = Math.min(textarea.scrollHeight, 200) // Cap at 200px
      textarea.style.height = `${newHeight}px`
    }
  }, [input])

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value)
  }

  const toggleQueryType = (type: QueryType) => {
    setSelectedType(selectedType === type ? null : type)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const trimmedInput = input.trim()
    
    if (!trimmedInput || isLoading || disabled) return
    
    if (trimmedInput.length < 3) {
      toast.error("Message must be at least 3 characters long")
      return
    }
    
    try {
      await onSendMessage(trimmedInput, selectedType)
      setInput("") // Clear input after successful send
      // Reset textarea height and refocus
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto"
        textareaRef.current.focus()
      }
    } catch (error) {
      // Error is already handled by the context provider
      console.error("Error sending message:", error)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Submit on Ctrl/Cmd+Enter
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault()
      handleSubmit(e)
    }

    // New line on Shift+Enter
    if (e.shiftKey && e.key === "Enter") {
      return // Allow default behavior
    }
  }

  return (
    <div className={cn(
      "fixed bottom-0 left-0 right-0 py-4 z-10",
      "transition-transform duration-200",
      disabled && "translate-y-full"
    )}>
      <form 
        onSubmit={handleSubmit} 
        className="mx-auto max-w-3xl px-4"
        aria-label="Research message form"
      >
        <div 
          className={cn(
            "flex flex-col rounded-2xl border bg-white p-4 shadow-[0_0_10px_rgba(0,0,0,0.05)] transition-all",
            isFocused ? "border-gray-300" : "border-gray-200"
          )}
        >
          <div className="relative">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              placeholder={placeholder}
              className={cn(
                "mb-3 w-full resize-none border-0 bg-transparent text-lg text-gray-900",
                "placeholder:text-gray-500 focus:outline-none focus:ring-0",
                isAtLimit && "text-red-500",
                (isLoading || disabled) && "text-gray-500"
              )}
              style={{ minHeight: "24px", maxHeight: "200px" }}
              disabled={isLoading || disabled}
              aria-label="Research message input"
              aria-invalid={isAtLimit}
              maxLength={maxLength}
            />
          </div>

          <div className="flex items-center justify-between">
            {/* Query type toggles */}
            <div className="flex items-center gap-2 overflow-x-auto pb-1">
              {/* Courts Toggle */}
              <button
                type="button"
                onClick={() => toggleQueryType(QueryType.COURT_CASE)}
                className={`flex items-center gap-2 rounded-full px-3 py-1.5 text-sm transition-colors ${
                  selectedType === QueryType.COURT_CASE
                    ? "bg-[#95C066] text-white"
                    : "bg-gray-50 text-gray-600 hover:bg-gray-100"
                }`}
                aria-pressed={selectedType === QueryType.COURT_CASE}
                title="Search court cases and legal precedents"
                disabled={isLoading || disabled}
              >
                <Gavel className="h-4 w-4" />
                <span>Courts</span>
              </button>

              {/* Legislative Toggle */}
              <button
                type="button"
                onClick={() => toggleQueryType(QueryType.LEGISLATIVE)}
                className={`flex items-center gap-2 rounded-full px-3 py-1.5 text-sm transition-colors ${
                  selectedType === QueryType.LEGISLATIVE
                    ? "bg-[#95C066] text-white"
                    : "bg-gray-50 text-gray-600 hover:bg-gray-100"
                }`}
                aria-pressed={selectedType === QueryType.LEGISLATIVE}
                title="Search legislation, statutes and regulations"
                disabled={isLoading || disabled}
              >
                <BookText className="h-4 w-4" />
                <span>Legislative</span>
              </button>

              {/* Commercial Toggle */}
              <button
                type="button"
                onClick={() => toggleQueryType(QueryType.COMMERCIAL)}
                className={`flex items-center gap-2 rounded-full px-3 py-1.5 text-sm transition-colors ${
                  selectedType === QueryType.COMMERCIAL
                    ? "bg-[#95C066] text-white"
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

            {/* Send button */}
            <Button
              type="submit"
              disabled={!input.trim() || isLoading || isAtLimit || disabled}
              className={cn(
                "rounded-full p-2 transition-colors",
                input.trim() && !isLoading && !isAtLimit && !disabled
                  ? "bg-[#95C066] text-white hover:bg-[#85b056] cursor-pointer"
                  : "bg-gray-100 text-gray-400 cursor-not-allowed"
              )}
              aria-label={isLoading ? "Sending message" : "Send message"}
            >
              {isLoading ? (
                <Loader2 className="h-5 w-5 animate-spin" aria-hidden="true" />
              ) : (
                <Send className="h-5 w-5" aria-hidden="true" />
              )}
            </Button>
          </div>
        </div>
      </form>

      {isLoading && (
        <div 
          className="mx-auto mt-2 max-w-3xl px-4 text-xs text-gray-500"
          aria-live="polite"
        >
          Processing your request...
        </div>
      )}
    </div>
  )
}
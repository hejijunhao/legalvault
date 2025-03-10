// src/components/research/search/research-input.tsx

"use client"

import { useState, useRef, useEffect } from "react"
import { Loader2, Send } from "lucide-react"
import { Button } from "@/components/ui/button"

interface ResearchInputProps {
  onSendMessage: (content: string) => Promise<void>
  isLoading: boolean
  maxLength?: number
  placeholder?: string
}

export function ResearchInput({
  onSendMessage,
  isLoading,
  maxLength = 1000,
  placeholder = "Type your legal question here..."
}: ResearchInputProps) {
  const [input, setInput] = useState("")
  const [charCount, setCharCount] = useState(0)
  const [isAtLimit, setIsAtLimit] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Update character count and limit status when input changes
  useEffect(() => {
    const trimmedLength = input.trim().length
    setCharCount(trimmedLength)
    setIsAtLimit(trimmedLength >= maxLength)
  }, [input, maxLength])

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const trimmedInput = input.trim()
    
    if (!trimmedInput || isLoading) return
    
    try {
      await onSendMessage(trimmedInput)
      setInput("") // Clear input after successful send
      // Reset textarea height and refocus
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto"
        textareaRef.current.focus()
      }
    } catch (error) {
      console.error("Error sending message:", error)
      // Error is handled by the parent component
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Submit on Ctrl+Enter or Cmd+Enter
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white py-4 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.1)]">
      <form 
        onSubmit={handleSubmit} 
        className="mx-auto flex max-w-3xl items-end gap-2 px-4"
        aria-label="Research message form"
      >
        <div className="relative flex-1">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            className="min-h-[52px] w-full resize-none rounded-md border border-gray-300 p-3 pr-10 focus:border-[#95C066] focus:outline-none focus:ring-1 focus:ring-[#95C066]"
            disabled={isLoading}
            aria-label="Research message input"
            aria-invalid={isAtLimit}
            aria-describedby="char-count"
            maxLength={maxLength}
          />
          <div 
            id="char-count"
            className={`absolute bottom-1 right-2 text-xs ${isAtLimit ? 'text-red-500 font-bold' : 'text-gray-400'}`}
            aria-live="polite"
          >
            {charCount}/{maxLength}
          </div>
        </div>
        <Button
          type="submit"
          disabled={!input.trim() || isLoading || isAtLimit}
          className="h-10 w-10 rounded-full bg-[#95C066] p-2 text-white hover:bg-[#85b056] disabled:bg-gray-300"
          aria-label={isLoading ? "Sending message" : "Send message"}
        >
          {isLoading ? (
            <Loader2 className="h-5 w-5 animate-spin" aria-hidden="true" />
          ) : (
            <Send className="h-5 w-5" aria-hidden="true" />
          )}
        </Button>
      </form>
      {isLoading && (
        <div 
          className="mx-auto mt-2 max-w-3xl px-4 text-sm text-gray-500"
          aria-live="polite"
        >
          Processing your request...
        </div>
      )}
    </div>
  )
}
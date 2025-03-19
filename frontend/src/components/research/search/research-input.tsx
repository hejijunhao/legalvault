// src/components/research/search/research-input.tsx

"use client"

import { useState, useRef, useEffect } from "react"
import { Loader2, Send, Bold, Italic, List } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { toast } from "sonner"
import { cn } from "@/lib/utils"

interface ResearchInputProps {
  onSendMessage: (content: string) => Promise<void>
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
  const [charCount, setCharCount] = useState(0)
  const [isAtLimit, setIsAtLimit] = useState(false)
  const [isFocused, setIsFocused] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Update character count and limit status when input changes
  useEffect(() => {
    const trimmedLength = input.trim().length
    setCharCount(trimmedLength)
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const trimmedInput = input.trim()
    
    if (!trimmedInput || isLoading || disabled) return
    
    if (trimmedInput.length < 3) {
      toast.error("Message must be at least 3 characters long")
      return
    }
    
    try {
      await onSendMessage(trimmedInput)
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

  const insertMarkdown = (syntax: string) => {
    const textarea = textareaRef.current
    if (!textarea) return

    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    const text = textarea.value

    // If text is selected, wrap it with syntax
    if (start !== end) {
      const selectedText = text.substring(start, end)
      const newText = text.substring(0, start) + syntax + selectedText + syntax + text.substring(end)
      setInput(newText)
      // Set cursor position after formatting
      setTimeout(() => {
        textarea.selectionStart = start + syntax.length
        textarea.selectionEnd = end + syntax.length
      }, 0)
    } else {
      // If no text is selected, just insert syntax
      const newText = text.substring(0, start) + syntax + text.substring(end)
      setInput(newText)
      // Set cursor position between syntax
      setTimeout(() => {
        textarea.selectionStart = start + syntax.length
        textarea.selectionEnd = start + syntax.length
      }, 0)
    }
  }

  return (
    <div className={cn(
      "fixed bottom-0 left-0 right-0 bg-white py-4 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.1)]",
      "transition-transform duration-200",
      disabled && "translate-y-full"
    )}>
      <form 
        onSubmit={handleSubmit} 
        className="mx-auto flex max-w-3xl flex-col gap-2 px-4"
        aria-label="Research message form"
      >
        {/* Formatting Toolbar */}
        <div className="flex items-center gap-1 px-2">
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="h-8 w-8 p-0"
                  onClick={() => insertMarkdown("**")}
                  disabled={isLoading || disabled}
                >
                  <Bold className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Bold (Ctrl+B)</TooltipContent>
            </Tooltip>

            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="h-8 w-8 p-0"
                  onClick={() => insertMarkdown("*")}
                  disabled={isLoading || disabled}
                >
                  <Italic className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Italic (Ctrl+I)</TooltipContent>
            </Tooltip>

            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="h-8 w-8 p-0"
                  onClick={() => insertMarkdown("- ")}
                  disabled={isLoading || disabled}
                >
                  <List className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Bullet List</TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>

        <div className="flex items-end gap-2">
          <div className="relative flex-1">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              placeholder={placeholder}
              className={cn(
                "min-h-[52px] w-full resize-none rounded-md border p-3 pr-10",
                "focus:outline-none focus:ring-1",
                "transition-colors duration-200",
                isFocused
                  ? "border-[#95C066] ring-[#95C066]"
                  : "border-gray-300",
                isAtLimit && "border-red-500 ring-red-500",
                (isLoading || disabled) && "bg-gray-50 text-gray-500"
              )}
              disabled={isLoading || disabled}
              aria-label="Research message input"
              aria-invalid={isAtLimit}
              aria-describedby="char-count"
              maxLength={maxLength}
            />
            <div 
              id="char-count"
              className={cn(
                "absolute bottom-1 right-2 text-xs transition-colors",
                isAtLimit ? "text-red-500 font-bold" : "text-gray-400"
              )}
              aria-live="polite"
            >
              {charCount}/{maxLength}
            </div>
          </div>
          <Button
            type="submit"
            disabled={!input.trim() || isLoading || isAtLimit || disabled}
            className={cn(
              "h-10 w-10 rounded-full p-2",
              "bg-[#95C066] text-white",
              "hover:bg-[#85b056]",
              "disabled:bg-gray-300",
              "transition-all duration-200"
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
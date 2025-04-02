// src/components/research/search/user-messages.tsx

"use client"

import { useEffect, useRef } from "react"
import { motion } from "framer-motion"
import { Avatar, AvatarImage } from "@/components/ui/avatar"
import { ChevronDown, Copy, ThumbsUp, ThumbsDown, RefreshCw, Loader2, AlertCircle } from "lucide-react"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { cn } from "@/lib/utils"
import { Message, Citation, QueryStatus } from "@/contexts/research/research-context"
import { toast } from "sonner"

interface UserMessagesProps {
  messages: Message[]
  userAvatar?: string
  userName?: string
  onRegenerateMessage?: (messageId: string) => void
  onRateMessage?: (messageId: string, rating: 'positive' | 'negative') => void
}

export function UserMessages({ 
  messages, 
  userAvatar, 
  userName = "You",
  onRegenerateMessage,
  onRateMessage
}: UserMessagesProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" })
    }
  }, [messages.length])

  const handleCopyMessage = async (content: string) => {
    try {
      await navigator.clipboard.writeText(content)
      toast.success("Message copied to clipboard")
    } catch (error) {
      toast.error("Failed to copy message")
    }
  }

  const getStatusText = (status?: QueryStatus) => {
    switch (status) {
      case QueryStatus.PENDING:
        return "Processing..."
      case QueryStatus.COMPLETED:
        return "Delivered"
      case QueryStatus.FAILED:
        return "Failed to process"
      case QueryStatus.NEEDS_CLARIFICATION:
        return "Needs clarification"
      case QueryStatus.IRRELEVANT:
        return "Irrelevant query"
      default:
        return ""
    }
  }

  // Function to check if we should show the sender name
  // (show for first message or when sender changes)
  const shouldShowSender = (index: number) => {
    if (index === 0) return true
    if (index > 0 && messages[index].role !== messages[index - 1].role) return true
    return false
  }

  return (
    <div className="space-y-4 mb-8 px-4">
      {messages.map((message, index) => (
        <motion.div
          key={message.id || index}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
          className="space-y-1"
        >
          {/* Sender Name */}
          {shouldShowSender(index) && (
            <div className={cn(
              "flex items-center text-xs text-gray-500 mb-1",
              message.role === "assistant" ? "justify-start" : "justify-end"
            )}>
              {message.role === "assistant" && (
                <>
                  <Avatar className="h-4 w-4 mr-1">
                    <AvatarImage src="/vp-avatar.png" alt="Virtual Paralegal" />
                  </Avatar>
                  <span>Virtual Paralegal</span>
                </>
              )}
              {message.role === "user" && (
                <>
                  <span>{userName}</span>
                  <Avatar className="h-4 w-4 ml-1">
                    <AvatarImage src={userAvatar || "/user-avatar.png"} alt={userName} />
                  </Avatar>
                </>
              )}
            </div>
          )}
          
          {/* Message Container */}
          <div className={cn(
            "group relative flex gap-3",
            message.role === "assistant" ? "justify-start" : "justify-end"
          )}>
            {/* Message Content */}
            <div className={cn(
              "relative max-w-[75%] space-y-2"
            )}>
              {/* Message Bubble */}
              <div className={cn(
                "relative rounded-[20px] px-4 py-2.5 shadow-sm",
                message.role === "assistant" 
                  ? "bg-[#FAFAFA] text-[#000000] rounded-bl-md border border-[#E8E8E8]" 
                  : "bg-[#BFEF9C] text-[#1A2E0D] rounded-br-md"
              )}>
                {/* Message Text */}
                <div className="prose prose-sm max-w-none">
                  <p className="text-[15px] leading-[1.35] m-0 break-words font-system">
                    {typeof message.content === 'object' && message.content?.text ? message.content.text : 'No content available'}
                  </p>
                </div>

                {/* Message Actions Dropdown (hidden by default, shown on hover) */}
                <div className={cn(
                  "absolute top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity",
                  message.role === "assistant" ? "-right-10" : "-left-10"
                )}>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <button className="rounded-full p-1.5 hover:bg-accent">
                        <ChevronDown className="h-4 w-4 text-muted-foreground" />
                      </button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align={message.role === "assistant" ? "end" : "start"}>
                      <DropdownMenuItem onClick={() => handleCopyMessage(message.content?.text || '')}>
                        <Copy className="mr-2 h-4 w-4" />
                        Copy message
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </div>

              {/* Quick Action Buttons for Assistant Messages */}
              {message.role === "assistant" && (
                <div className="flex items-center justify-start space-x-2 pt-1">
                  <button 
                    onClick={() => handleCopyMessage(message.content?.text || '')}
                    className="rounded-full p-1.5 hover:bg-gray-100 transition-colors text-gray-500 hover:text-gray-700"
                    title="Copy message"
                  >
                    <Copy className="h-4 w-4" />
                  </button>
                  {onRegenerateMessage && (
                    <button 
                      onClick={() => onRegenerateMessage(message.id || '')}
                      className="rounded-full p-1.5 hover:bg-gray-100 transition-colors text-gray-500 hover:text-gray-700"
                      title="Regenerate response"
                    >
                      <RefreshCw className="h-4 w-4" />
                    </button>
                  )}
                  {onRateMessage && (
                    <>
                      <button 
                        onClick={() => onRateMessage(message.id || '', 'positive')}
                        className="rounded-full p-1.5 hover:bg-gray-100 transition-colors text-gray-500 hover:text-green-600"
                        title="Helpful"
                      >
                        <ThumbsUp className="h-4 w-4" />
                      </button>
                      <button 
                        onClick={() => onRateMessage(message.id || '', 'negative')}
                        className="rounded-full p-1.5 hover:bg-gray-100 transition-colors text-gray-500 hover:text-red-600"
                        title="Not helpful"
                      >
                        <ThumbsDown className="h-4 w-4" />
                      </button>
                    </>
                  )}
                </div>
              )}

              {/* Status indicator for user messages only */}
              {message.role === "user" && message.status && (
                <div className="flex justify-end">
                  <div className={cn(
                    "text-xs px-1",
                    message.status === QueryStatus.PENDING 
                      ? "text-gray-500" 
                      : message.status === QueryStatus.FAILED 
                        ? "text-red-500" 
                        : "text-gray-500"
                  )}>
                    {message.status === QueryStatus.PENDING && (
                      <span className="flex items-center gap-1">
                        <Loader2 className="h-3 w-3 animate-spin" />
                        {getStatusText(message.status)}
                      </span>
                    )}
                    {message.status === QueryStatus.FAILED && (
                      <span className="flex items-center gap-1">
                        <AlertCircle className="h-3 w-3" />
                        {getStatusText(message.status)}
                      </span>
                    )}
                    {message.status !== QueryStatus.PENDING && message.status !== QueryStatus.FAILED && (
                      <span>{getStatusText(message.status)}</span>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </motion.div>
      ))}
      <div ref={messagesEndRef} />
    </div>
  )
}

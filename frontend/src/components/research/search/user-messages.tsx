// src/components/research/search/user-messages.tsx

"use client"

import { useEffect, useRef } from "react"
import { motion } from "framer-motion"
import { Avatar, AvatarImage } from "@/components/ui/avatar"
import { ChevronDown, Reply, Copy, Forward, FolderPlus, Bell, CheckSquare, Loader2, AlertCircle } from "lucide-react"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { cn } from "@/lib/utils"
import { Message, Citation, QueryStatus } from "@/contexts/research/research-context"
import { SourceCitations } from "./source-citations"
import { toast } from "sonner"

interface UserMessagesProps {
  messages: Message[]
  userAvatar?: string
  userName?: string
}

export function UserMessages({ 
  messages, 
  userAvatar, 
  userName = "You" 
}: UserMessagesProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" })
    }
  }, [messages])

  const handleCopyMessage = async (content: string) => {
    try {
      await navigator.clipboard.writeText(content)
      toast.success("Message copied to clipboard")
    } catch (error) {
      toast.error("Failed to copy message")
    }
  }

  return (
    <div className="space-y-4 mb-8 px-4">
      {messages.map((message, index) => (
        <motion.div
          key={message.id || index}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
          className={cn(
            "group relative flex gap-3 items-end",
            message.role === "assistant" ? "flex-row" : "flex-row-reverse"
          )}
        >
          {/* Assistant Avatar */}
          {message.role === "assistant" && (
            <Avatar className="mb-1 h-8 w-8 ring-1 ring-primary/5 ring-offset-1">
              <AvatarImage src="/vp-avatar.png" alt="Virtual Paralegal" />
            </Avatar>
          )}

          {/* Message Content */}
          <div className={cn(
            "relative max-w-[75%] space-y-2",
            message.role === "assistant" ? "mr-12" : "ml-12"
          )}>
            {/* Message Status */}
            {message.status === QueryStatus.PENDING && (
              <div className="absolute -top-6 left-0 flex items-center gap-2 text-muted-foreground">
                <Loader2 className="h-3 w-3 animate-spin" />
                <span className="text-xs font-medium">Processing...</span>
              </div>
            )}
            
            {message.status === QueryStatus.FAILED && (
              <div className="absolute -top-6 left-0 flex items-center gap-2 text-destructive">
                <AlertCircle className="h-3 w-3" />
                <span className="text-xs font-medium">Failed to process message</span>
              </div>
            )}
            
            {/* Message Bubble */}
            <div className={cn(
              "relative rounded-[20px] px-4 py-2.5 shadow-sm",
              message.role === "assistant" 
                ? "bg-[#e9e9eb] text-[#000000] rounded-bl-md" 
                : "bg-[#007AFF] text-white rounded-br-md"
            )}>
              {/* Message Text */}
              <div className="prose prose-sm max-w-none">
                <p className="text-[15px] leading-[1.35] m-0 break-words font-system">
                  {message.content?.text || 'No content available'}
                </p>
              </div>

              {/* Citations */}
              {message.content?.citations && message.content.citations.length > 0 && (
                <div className={cn(
                  "mt-2 pt-2 border-t",
                  message.role === "assistant" 
                    ? "border-black/10" 
                    : "border-white/10"
                )}>
                  <SourceCitations sources={message.content.citations} />
                </div>
              )}

              {/* Message Actions */}
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
          </div>

          {/* User Avatar */}
          {message.role === "user" && (
            <Avatar className="mb-1 h-8 w-8">
              <AvatarImage src={userAvatar || "/user-avatar.png"} alt={userName} />
            </Avatar>
          )}
        </motion.div>
      ))}
      <div ref={messagesEndRef} />
    </div>
  )
}

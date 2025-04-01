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

  // Scroll to bottom when new messages arrive
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
    <div className="space-y-6 mb-8">
      {messages.map((message, index) => (
        <motion.div
          key={message.id || index}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className={cn(
            "group relative flex gap-3 px-4 py-3 rounded-lg",
            message.role === "assistant" ? "bg-secondary" : "bg-background"
          )}
        >
          {/* Assistant Avatar */}
          {message.role === "assistant" && (
            <Avatar className="mt-1 h-8 w-8 border border-white/20">
              <AvatarImage src="/vp-avatar.png" alt="Virtual Paralegal" />
            </Avatar>
          )}

          {/* Message Content */}
          <div className="flex-1 space-y-2">
            {/* Message Status */}
            {message.status === QueryStatus.PENDING && (
              <div className="mb-2 flex items-center gap-2 text-muted-foreground">
                <Loader2 className="h-3 w-3 animate-spin" />
                <span className="text-xs">Processing...</span>
              </div>
            )}
            
            {message.status === QueryStatus.FAILED && (
              <div className="mb-2 flex items-center gap-2 text-destructive">
                <AlertCircle className="h-3 w-3" />
                <span className="text-xs">Failed to process message</span>
              </div>
            )}
            
            {/* Message Text */}
            <div className="prose prose-sm max-w-none">
              <p className="text-sm leading-relaxed whitespace-pre-wrap">
                {message.content?.text || 'No content available'}
              </p>
            </div>

            {/* Citations */}
            {message.content?.citations && message.content.citations.length > 0 && (
              <div className="mt-2">
                <SourceCitations sources={message.content.citations} />
              </div>
            )}

            {/* Message Actions Dropdown - Only show for assistant messages */}
            {message.role === "assistant" && (
              <div className="absolute -top-2 -right-2 opacity-0 transition-opacity group-hover:opacity-100">
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <button className="rounded-full bg-white p-1 shadow-md hover:bg-gray-100">
                      <ChevronDown className="h-4 w-4 text-gray-600" />
                    </button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="w-72">
                    <DropdownMenuItem onSelect={() => handleCopyMessage(message.content?.text || '')}>
                      <Copy className="mr-2 h-4 w-4" />
                      <span>Copy</span>
                    </DropdownMenuItem>
                    <DropdownMenuItem disabled>
                      <Reply className="mr-2 h-4 w-4" />
                      <span>Reply</span>
                    </DropdownMenuItem>
                    <DropdownMenuItem disabled>
                      <Forward className="mr-2 h-4 w-4" />
                      <span>Forward</span>
                    </DropdownMenuItem>
                    <DropdownMenuItem disabled>
                      <FolderPlus className="mr-2 h-4 w-4 flex-shrink-0" />
                      <span className="flex-grow">Add to Workspace</span>
                      <span className="ml-2 flex-shrink-0 text-xs text-muted-foreground">Coming Soon</span>
                    </DropdownMenuItem>
                    <DropdownMenuItem disabled>
                      <Bell className="mr-2 h-4 w-4 flex-shrink-0" />
                      <span className="flex-grow">Create Reminder</span>
                      <span className="ml-2 flex-shrink-0 text-xs text-muted-foreground">Coming Soon</span>
                    </DropdownMenuItem>
                    <DropdownMenuItem disabled>
                      <CheckSquare className="mr-2 h-4 w-4 flex-shrink-0" />
                      <span className="flex-grow">Create Task</span>
                      <span className="ml-2 flex-shrink-0 text-xs text-muted-foreground">Coming Soon</span>
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            )}
          </div>

          {/* User Avatar */}
          {message.role === "user" && (
            <Avatar className="mt-1 h-8 w-8">
              <AvatarImage src={userAvatar || "/user-avatar.png"} alt={userName} />
            </Avatar>
          )}
        </motion.div>
      ))}

      {/* Auto-scroll anchor */}
      <div ref={messagesEndRef} />
    </div>
  )
}

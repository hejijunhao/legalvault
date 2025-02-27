// src/components/research/search/user-messages.tsx

"use client"

import { motion } from "framer-motion"
import { Avatar, AvatarImage } from "@/components/ui/avatar"
import { ChevronDown, Reply, Copy, Forward, FolderPlus, Bell, CheckSquare } from "lucide-react"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { cn } from "@/lib/utils"

interface Message {
  id: string
  content: string
  sender: "user" | "assistant"
  timestamp?: Date
}

interface UserMessagesProps {
  messages: Message[]
  userAvatar?: string
  userName?: string
}

export function UserMessages({ messages, userAvatar, userName = "You" }: UserMessagesProps) {
  return (
    <div className="space-y-6 mb-8">
      {messages.map((message, index) => (
        <motion.div
          key={message.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: index * 0.1 }}
          className={cn("flex items-end gap-3", message.sender === "user" ? "justify-end" : "justify-start")}
        >
          {/* Message Bubble */}
          <div
            className={cn(
              "group relative max-w-[80%] rounded-2xl px-4 py-3",
              message.sender === "user" ? "bg-[#9FE870]/20 text-[#1C1C1C]" : "bg-white text-[#1C1C1C]",
            )}
          >
            <p className="text-sm leading-relaxed">{message.content}</p>
            {message.timestamp && (
              <p className="mt-1 text-xs text-gray-500">
                {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
              </p>
            )}

            {/* Message Actions Dropdown - Only show for VP messages */}
            {message.sender === "assistant" && (
              <div className="absolute -top-2 -right-2 opacity-0 transition-opacity group-hover:opacity-100">
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <button className="rounded-full bg-white p-1 shadow-md hover:bg-gray-100">
                      <ChevronDown className="h-4 w-4 text-gray-600" />
                    </button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="w-72">
                    <DropdownMenuItem>
                      <Reply className="mr-2 h-4 w-4" />
                      <span>Reply</span>
                    </DropdownMenuItem>
                    <DropdownMenuItem>
                      <Copy className="mr-2 h-4 w-4" />
                      <span>Copy</span>
                    </DropdownMenuItem>
                    <DropdownMenuItem>
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

          {/* Avatar */}
          {message.sender === "assistant" && (
            <Avatar className="h-8 w-8 border border-white/20">
              <AvatarImage src="/placeholder.svg" alt="Assistant" />
            </Avatar>
          )}
        </motion.div>
      ))}
    </div>
  )
}




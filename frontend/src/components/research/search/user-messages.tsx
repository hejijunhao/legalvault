// src/components/research/search/user-messages.tsx

"use client"

import { useEffect, useRef } from "react"
import { motion } from "framer-motion"
import { Avatar, AvatarImage } from "@/components/ui/avatar"
import { ChevronDown, Copy, ThumbsUp, ThumbsDown, RefreshCw, Loader2, AlertCircle, ArrowRight, Share2, FolderPlus, Brain, Library } from "lucide-react"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { cn } from "@/lib/utils"
import { Message, Citation, QueryStatus } from "@/contexts/research/research-context"
import { toast } from "sonner"
import ReactMarkdown from "react-markdown"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"

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
                "relative rounded-[20px] px-4 py-2.5 shadow-sm mb-3",
                message.role === "assistant" 
                  ? "bg-[#FAFAFA] text-[#000000] rounded-bl-md border border-[#E8E8E8]" 
                  : "bg-[#BFEF9C] text-[#1A2E0D] rounded-br-md"
              )}>
                {/* Message Text */}
                <div className="prose prose-sm max-w-none">
                  <div className="text-[15px] leading-[1.6] m-0 break-words font-inter 
                    [&>h1]:text-xl [&>h1]:font-bold [&>h1]:mb-4 [&>h1]:mt-2 [&>h1]:font-inter
                    [&>h2]:text-lg [&>h2]:font-bold [&>h2]:mb-3 [&>h2]:mt-2 [&>h2]:font-inter
                    [&>h3]:font-bold [&>h3]:mb-2 [&>h3]:mt-1 [&>h3]:font-inter
                    [&>p]:mb-3 [&>p]:leading-[1.7] [&>p]:font-inter
                    [&>ul]:mb-3 [&>ul]:pl-4 [&>ul>li]:mb-2 [&>ul>li]:leading-[1.6] [&>ul>li]:font-inter
                    [&>ol]:mb-3 [&>ol]:pl-4 [&>ol>li]:mb-2 [&>ol>li]:leading-[1.6] [&>ol>li]:font-inter
                    [&>*:last-child]:mb-0
                    [&>p:first-child]:mt-0 [&>h1:first-child]:mt-0 [&>h2:first-child]:mt-0">
                    <ReactMarkdown>
                      {typeof message.content === 'object' && message.content?.text ? message.content.text : 'No content available'}
                    </ReactMarkdown>
                  </div>
                </div>

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

              {/* Message Actions */}
              {message.role === "assistant" && (
                <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-sm">
                  <TooltipProvider delayDuration={300}>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <button
                          onClick={() => handleCopyMessage(message.content?.text || '')}
                          className="flex items-center gap-1.5 text-gray-500 hover:text-gray-900 transition-all hover:scale-105"
                        >
                          <Copy className="h-4 w-4" />
                          <span>Copy</span>
                        </button>
                      </TooltipTrigger>
                      <TooltipContent side="top" className="bg-gray-900 text-white text-xs px-2 py-1">
                        Copy this message to your clipboard
                      </TooltipContent>
                    </Tooltip>

                    <Tooltip>
                      <TooltipTrigger asChild>
                        <button
                          className="flex items-center gap-1.5 text-gray-500 hover:text-gray-900 transition-all hover:scale-105"
                        >
                          <ArrowRight className="h-4 w-4" />
                          <span>Share</span>
                        </button>
                      </TooltipTrigger>
                      <TooltipContent side="top" className="bg-gray-900 text-white text-xs px-2 py-1">
                        Share this response with colleagues
                      </TooltipContent>
                    </Tooltip>

                    <Tooltip>
                      <TooltipTrigger asChild>
                        <button
                          className="flex items-center gap-1.5 text-gray-500 hover:text-gray-900 transition-all hover:scale-105"
                        >
                          <svg 
                            className="h-4 w-4" 
                            viewBox="0 0 24 24" 
                            fill="none" 
                            stroke="currentColor" 
                            strokeWidth="1.5" 
                            strokeLinecap="round" 
                            strokeLinejoin="round"
                          >
                            <path d="M4 10V6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v4M4 10h16M4 10v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8M12 7v10M9 14h6" />
                          </svg>
                          <span>Workspace</span>
                        </button>
                      </TooltipTrigger>
                      <TooltipContent side="top" className="bg-gray-900 text-white text-xs px-2 py-1">
                        Save to your workspace for later reference
                      </TooltipContent>
                    </Tooltip>

                    <Tooltip>
                      <TooltipTrigger asChild>
                        <button
                          className="flex items-center gap-1.5 text-gray-500 hover:text-gray-900 transition-all hover:scale-105"
                        >
                          <svg 
                            className="h-4 w-4" 
                            viewBox="0 0 24 24" 
                            fill="none" 
                            stroke="currentColor" 
                            strokeWidth="1.5" 
                            strokeLinecap="round" 
                            strokeLinejoin="round"
                          >
                            <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2h11A2.5 2.5 0 0 1 20 4.5v15a2.5 2.5 0 0 1-2.5 2.5h-11A2.5 2.5 0 0 1 4 19.5z" />
                            <path d="M8 7h8M8 11h8M8 15h5" />
                          </svg>
                          <span>Library</span>
                        </button>
                      </TooltipTrigger>
                      <TooltipContent side="top" className="bg-gray-900 text-white text-xs px-2 py-1">
                        Add to your knowledge library
                      </TooltipContent>
                    </Tooltip>

                    <Tooltip>
                      <TooltipTrigger asChild>
                        <button
                          className="flex items-center gap-1.5 text-gray-500 hover:text-gray-900 transition-all hover:scale-105"
                        >
                          <svg 
                            className="h-4 w-4" 
                            viewBox="0 0 24 24" 
                            fill="none" 
                            stroke="currentColor" 
                            strokeWidth="1.5" 
                            strokeLinecap="round" 
                            strokeLinejoin="round"
                          >
                            <path d="M12 3.5c-4.2 0-7.5 2.5-9 6 1.5 3.5 4.8 6 9 6s7.5-2.5 9-6c-1.5-3.5-4.8-6-9-6z" />
                            <circle cx="12" cy="9.5" r="3" />
                            <path d="M6 17.5l2-2m8 2l-2-2M9 20.5l1.5-1.5m3 0l1.5 1.5" />
                          </svg>
                          <span>Learn</span>
                        </button>
                      </TooltipTrigger>
                      <TooltipContent side="top" className="bg-gray-900 text-white text-xs px-2 py-1">
                        Train your VP with this information
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </div>
              )}
              {message.role === "assistant" && onRegenerateMessage && (
                <button
                  onClick={() => onRegenerateMessage(message.id)}
                  className="flex items-center gap-1.5 text-gray-500 hover:text-gray-900 transition-all hover:scale-105"
                  title="Regenerate response"
                >
                  <RefreshCw className="h-4 w-4" />
                  <span>Regenerate</span>
                </button>
              )}
              {message.role === "assistant" && onRateMessage && (
                <>
                  <button
                    onClick={() => onRateMessage(message.id, 'positive')}
                    className="flex items-center gap-1.5 text-gray-500 hover:text-gray-900 transition-all hover:scale-105"
                    title="Rate positively"
                  >
                    <ThumbsUp className="h-4 w-4" />
                    <span>Like</span>
                  </button>
                  <button
                    onClick={() => onRateMessage(message.id, 'negative')}
                    className="flex items-center gap-1.5 text-gray-500 hover:text-gray-900 transition-all hover:scale-105"
                    title="Rate negatively"
                  >
                    <ThumbsDown className="h-4 w-4" />
                    <span>Dislike</span>
                  </button>
                </>
              )}
            </div>
          </div>
        </motion.div>
      ))}
      <div ref={messagesEndRef} />
    </div>
  )
}

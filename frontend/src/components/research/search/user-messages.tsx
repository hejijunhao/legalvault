// src/components/research/search/user-messages.tsx

"use client"

import { useEffect, useRef } from "react"
import { motion } from "framer-motion"
import { Avatar, AvatarImage } from "@/components/ui/avatar"
import { Copy, ThumbsUp, ThumbsDown, RefreshCw, Loader2, AlertCircle, ArrowRight } from "lucide-react"
import { cn } from "@/lib/utils"
import { Message, QueryStatus } from "@/contexts/research/research-context"
import { toast } from "sonner"
import ReactMarkdown from "react-markdown"
import rehypeRaw from "rehype-raw"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import { CitationHovercard } from "./citation-hovercard"

interface UserMessagesProps {
  messages: Message[]
  userAvatar?: string
  userName?: string
  onRegenerateMessage?: (messageId: string) => void
  onRateMessage?: (messageId: string, rating: 'positive' | 'negative') => void
  onCopyMessage?: (messageId: string) => void
}

export function UserMessages({ 
  messages, 
  userAvatar, 
  userName = "You",
  onRegenerateMessage,
  onRateMessage,
  onCopyMessage
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

  // Process citations in text, replacing [n] with span elements
  const processCitations = (text: string, citations: any[]) => {
    return text.replace(/\[(\d+)\]/g, (match, number) => {
      const index = parseInt(number, 10) - 1
      if (index >= 0 && index < citations.length) {
        return `<span data-citation="${index}"></span>`
      }
      return match
    })
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
              "relative max-w-[85%] space-y-2"
            )}>
              {/* Message Bubble */}
              <div className={cn(
                "relative rounded-[20px] px-5 py-3.5 shadow-sm mb-3",
                message.role === "assistant" 
                  ? "bg-[#FAFAFA] text-[#000000] rounded-bl-md border border-[#E8E8E8]" 
                  : "bg-[#BFEF9C] text-[#1A2E0D] rounded-br-md"
              )}>
                {/* Message Text */}
                <div className="prose prose-sm max-w-none">
                  <div className="text-[15px] leading-[1.65] m-0 break-words font-inter tracking-[-0.01em]
                    /* Adjusted heading styles for elegance */
                    [&>h1]:text-xl [&>h1]:font-semibold [&>h1]:mb-4 [&>h1]:mt-2 [&>h1]:font-inter [&>h1]:leading-[1.35]
                    [&>h2]:text-lg [&>h2]:font-semibold [&>h2]:mb-3 [&>h2]:mt-2 [&>h2]:font-inter [&>h2]:leading-[1.4]
                    [&>h3]:text-base [&>h3]:font-semibold [&>h3]:mb-2.5 [&>h3]:mt-1.5 [&>h3]:font-inter [&>h3]:leading-[1.45]
                    /* Refined paragraph and list spacing */
                    [&>p]:mb-3 [&>p]:leading-[1.65] [&>p]:font-inter
                    [&>ul]:mb-3 [&>ul]:pl-4 [&>ul>li]:mb-1.5 [&>ul>li]:leading-[1.65] [&>ul>li]:font-inter
                    [&>ol]:mb-3 [&>ol]:pl-4 [&>ol>li]:mb-1.5 [&>ol>li]:leading-[1.65] [&>ol>li]:font-inter
                    /* Ensure last element has no bottom margin */
                    [&>*:last-child]:mb-0 
                    /* Ensure first element has no top margin */
                    [&>*:first-child]:mt-0">
                    <ReactMarkdown
                      rehypePlugins={[rehypeRaw]}
                      components={{
                        p: ({ node, children, ...props }) => {
                          // Check if the direct children consist ONLY of whitespace text nodes
                          // and exactly one specific citation span element.
                          let isOnlyCitationSpan = false;
                          if (node && node.children) {
                            const significantChildren = node.children.filter((child: any) => {
                              // Ignore pure whitespace text nodes
                              if (child.type === 'text' && child.value.trim() === '') {
                                return false;
                              }
                              return true;
                            });

                            // Check if there's exactly one significant child, and it's our citation span
                            if (significantChildren.length === 1) {
                              const child = significantChildren[0];
                              if (
                                child.type === 'element' &&
                                child.tagName === 'span' &&
                                child.properties?.['data-citation'] !== undefined
                              ) {
                                isOnlyCitationSpan = true;
                              }
                            }
                          }

                          // If it's effectively just the citation span, render as a div
                          if (isOnlyCitationSpan) {
                            return <div className="mb-3 leading-[1.65] font-inter last:mb-0" {...props}>{children}</div>;
                          }

                          // Otherwise, render as a standard paragraph
                          return <p className="mb-3 leading-[1.65] font-inter last:mb-0" {...props}>{children}</p>;
                        },
                        // Keep div handling for direct divs in markdown
                        div: ({ children, ...props }) => (
                          <div className="mb-3 leading-[1.65] font-inter last:mb-0" {...props}>{children}</div>
                        ),
                        span: ({ node, ...props }) => {
                          // Keep the simplified span override (render CitationHovercard directly)
                          if ('data-citation' in props) {
                            const index = parseInt(props['data-citation'] as string, 10)
                            const citation = message.content?.citations?.[index]
                            if (!citation) return <span>[{index + 1}]</span>
                            return <CitationHovercard index={index + 1} citation={citation} />
                          }
                          return <span {...props} />
                        }
                      }}
                    >
                      {typeof message.content === 'object' && message.content?.text 
                        ? processCitations(message.content.text, message.content.citations || [])
                        : typeof message.content === 'string' // Handle plain string content too
                        ? message.content 
                        : 'No content available'
                      }
                    </ReactMarkdown>
                  </div>
                </div>
              </div>

              {/* Status indicator for user messages */}
              {message.role === "user" && message.status && (
                <div className="flex justify-end -mt-10 mb-2">
                  <div className={cn(
                    "text-[13px] px-1.5 py-0.5 text-gray-500",
                    message.status === QueryStatus.PENDING 
                      ? "text-gray-500" 
                      : message.status === QueryStatus.FAILED 
                        ? "text-red-500" 
                        : "text-gray-500"
                  )}>
                    {message.status === QueryStatus.PENDING && (
                      <span className="flex items-center gap-1.5">
                        <Loader2 className="h-3 w-3 animate-spin" />
                        {getStatusText(message.status)}
                      </span>
                    )}
                    {message.status === QueryStatus.FAILED && (
                      <span className="flex items-center gap-1.5">
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

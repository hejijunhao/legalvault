// src/components/knowledge/past-conversations.tsx

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { MessageSquare, Clock } from "lucide-react"

export function PastConversations() {
  const conversations = [
    {
      id: 1,
      user: "Sarah Chen",
      excerpt: "Discussion about Project Greenbridge merger terms...",
      time: "2h ago",
    },
    {
      id: 2,
      user: "Michael Wong",
      excerpt: "Review of the latest contract draft for Elysian...",
      time: "5h ago",
    },
    {
      id: 3,
      user: "David Kim",
      excerpt: "Analysis of regulatory compliance requirements...",
      time: "1d ago",
    },
  ]

  return (
    <Card className="overflow-hidden backdrop-blur-sm">
      <CardHeader className="border-b bg-white/5 p-6">
        <CardTitle className="flex items-center gap-2 text-lg">
          <MessageSquare className="h-5 w-5" />
          Past Conversations
        </CardTitle>
      </CardHeader>
      <CardContent className="p-6">
        <div className="space-y-4">
          {conversations.map((conversation) => (
            <div key={conversation.id} className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-medium text-[#1C1C1C]">{conversation.user}</span>
                <div className="flex items-center gap-1 text-xs text-[#8992A9]">
                  <Clock className="h-3 w-3" />
                  {conversation.time}
                </div>
              </div>
              <p className="text-sm text-[#525766]">{conversation.excerpt}</p>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}


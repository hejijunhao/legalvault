// components/paralegal/profile-card.tsx
"use client"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import { Mail } from 'lucide-react'
import type { VPProfile } from "@/types/paralegal"

interface ProfileCardProps {
  profile: VPProfile;
}

export default function ProfileCard({ profile }: ProfileCardProps) {
  return (
    <Card className="border-gray-200 bg-white/50 backdrop-blur-sm shadow-sm">
      <CardContent className="flex flex-col items-center p-6">
        <div className="relative">
          <Avatar className="h-32 w-32 border-2 border-primary">
            <AvatarImage src={profile.avatar} />
            <AvatarFallback>{profile.name.slice(0, 2)}</AvatarFallback>
          </Avatar>
          <Badge className="absolute -bottom-2 left-1/2 -translate-x-1/2 transform">
            Level {profile.level}
          </Badge>
        </div>
        <h2 className="mt-4 text-2xl font-bold text-primary">{profile.name}</h2>
        <p className="text-sm text-gray-600">Virtual Paralegal</p>
        <div className="mt-4 flex items-center space-x-2">
          <Mail className="h-4 w-4 text-gray-400" />
          <span className="text-sm text-gray-600">{profile.email}</span>
        </div>
      </CardContent>
    </Card>
  )
}
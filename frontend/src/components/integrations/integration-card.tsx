// components/integrations/integration-card.tsx

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import Image from "next/image"

interface IntegrationCardProps {
  integration: {
    id: string
    name: string
    description: string
    authType: string
    iconUrl: string
    isActive: boolean
  }
  onActivate: () => void
}

export function IntegrationCard({ integration, onActivate }: IntegrationCardProps) {
  return (
    <Card className="overflow-hidden bg-white/80 backdrop-blur-sm border border-white/10 shadow-[0px_4px_15px_0px_rgba(0,0,0,0.05)] transition-all hover:bg-white/90">
      <CardHeader className="border-b border-gray-100/20 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="relative h-12 w-12 overflow-hidden rounded-full bg-gray-50">
              <Image
                src={integration.iconUrl || "/placeholder.svg"}
                alt={integration.name}
                fill
                className="object-cover"
              />
            </div>
            <div>
              <CardTitle className="text-lg font-medium text-[#1C1C1C]">{integration.name}</CardTitle>
              <CardDescription className="text-sm text-[#525766]">{integration.description}</CardDescription>
            </div>
          </div>
          <Badge
            variant={integration.isActive ? "default" : "secondary"}
            className={`${integration.isActive
              ? "bg-black text-white hover:bg-black/90"
              : "bg-gray-100 text-[#525766]"}`}
          >
            {integration.isActive ? "Active" : "Inactive"}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="p-4 bg-white/50">
        <div className="flex items-center justify-between">
          <div className="text-sm text-[#525766]">Auth Type: {integration.authType}</div>
          <Button
            onClick={onActivate}
            className="bg-black text-white hover:bg-black/90"
          >
            {integration.isActive ? "Manage" : "Activate"}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}


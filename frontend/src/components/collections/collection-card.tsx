// src/components/collections/collection-card.tsx

"use client"

import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Clock, FileText } from "lucide-react"
import Image from "next/image"
import Link from "next/link"

interface CollectionCardProps {
  collection: {
    id: string
    name: string
    description: string
    documentCount: number
    lastUpdated: string
    coverImage: string
    gradient: string
  }
}

export function CollectionCard({ collection }: CollectionCardProps) {
  return (
    <Link href={`/collections/${collection.id}`}>
      <Card className="group relative overflow-hidden border-white/20 bg-white/60 backdrop-blur-md transition-all duration-500 hover:shadow-lg hover:shadow-black/5 hover:scale-[1.02]">
        {/* Cover Image */}
        <div className="relative aspect-square overflow-hidden">
          <div className={`absolute inset-0 bg-gradient-to-br ${collection.gradient}`} />
          <Image
            src={collection.coverImage || "/placeholder.svg"}
            alt={collection.name}
            fill
            className="object-cover transition-all duration-500 group-hover:scale-105"
          />
        </div>

        {/* Content */}
        <div className="p-6">
          <h3 className="mb-2 text-xl font-semibold text-gray-900">{collection.name}</h3>
          <p className="mb-4 text-sm text-gray-600">{collection.description}</p>

          <div className="flex items-center justify-between text-sm text-gray-500">
            <div className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              <span>{collection.documentCount} docs</span>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4" />
              <span>{collection.lastUpdated}</span>
            </div>
          </div>
        </div>

        {/* Hover State Button */}
        <div className="absolute bottom-4 right-4 opacity-0 transition-all duration-500 group-hover:opacity-100">
          <Button className="bg-white/80 text-black hover:bg-white">View Collection</Button>
        </div>
      </Card>
    </Link>
  )
}


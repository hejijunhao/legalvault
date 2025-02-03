// src/components/collections/featured-collection.tsx

"use client"

import { motion } from "framer-motion"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import Image from "next/image"

export function FeaturedCollection() {
  return (
    <Card className="group mb-8 overflow-hidden border-white/20 bg-white/60 backdrop-blur-md">
      <div className="relative flex aspect-[3/1] w-full items-end">
        {/* Background Image */}
        <div className="absolute inset-0">
          <Image
            src="/placeholder.svg?height=400&width=1200"
            alt="Featured Collection"
            fill
            className="object-cover opacity-50 transition-all duration-500 group-hover:scale-105"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent" />
        </div>

        {/* Content */}
        <motion.div
          className="relative z-10 p-8 text-white"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="mb-2 text-3xl font-bold">M&A Templates</h2>
          <p className="mb-4 max-w-2xl text-lg text-white/80">
            A comprehensive collection of merger and acquisition templates, including term sheets, due diligence
            checklists, and closing documents.
          </p>
          <div className="flex items-center gap-4">
            <Button variant="default" className="bg-white text-black hover:bg-white/90">
              Browse Collection
            </Button>
            <span className="text-sm text-white/60">156 documents</span>
          </div>
        </motion.div>
      </div>
    </Card>
  )
}


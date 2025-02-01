// src/components/library/blocks/highlights-block.tsx

"use client"

import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Card } from "@/components/ui/card"
import { ChevronLeft, ChevronRight } from "lucide-react"
import { Button } from "@/components/ui/button"

const highlights = [
  {
    id: "1",
    title: "Project Greenbridge Analysis",
    type: "Knowledge Highlight",
    gradient: "from-[#FF6B6B] via-[#FFE66D] to-[#4ECDC4]",
    summary:
      "Comprehensive analysis of the Greenbridge merger potential impact on market dynamics and regulatory implications. Key findings suggest a 15% market share increase and potential synergies in sustainable tech development.",
    image: "/placeholder.svg?height=400&width=800",
  },
  {
    id: "2",
    title: "ESG Compliance 2024",
    type: "Research Report",
    gradient: "from-[#A8E6CF] via-[#DCEDC1] to-[#FFD3B6]",
    summary:
      "Latest research on upcoming ESG compliance requirements affecting tech mergers. Highlights include new carbon disclosure requirements and sustainable governance frameworks.",
    image: "/placeholder.svg?height=400&width=800",
  },
  {
    id: "3",
    title: "Q1 Deal Pipeline",
    type: "Project Overview",
    gradient: "from-[#3494E6] via-[#5B247A] to-[#EC6EAD]",
    summary:
      "Strategic overview of Q1 2024 M&A pipeline, featuring 5 major deals with a combined value of $2.8B. Key sectors include renewable energy and biotech.",
    image: "/placeholder.svg?height=400&width=800",
  },
]

export function HighlightsBlock() {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isHovered, setIsHovered] = useState(false)

  useEffect(() => {
    const intervalId = setInterval(() => {
      setCurrentIndex((prevIndex) => (prevIndex + 1) % highlights.length)
    }, 10000) // Change highlight every 10 seconds

    return () => clearInterval(intervalId)
  }, [])

  const nextSlide = () => {
    setCurrentIndex((prev) => (prev + 1) % highlights.length)
  }

  const prevSlide = () => {
    setCurrentIndex((prev) => (prev - 1 + highlights.length) % highlights.length)
  }

  return (
    <div className="relative h-[350px] w-full overflow-hidden">
      <div
        className="relative h-full overflow-hidden rounded-xl"
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        <AnimatePresence mode="wait">
          <motion.div
            key={currentIndex}
            initial={{ opacity: 0, scale: 1.1 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            transition={{ duration: 0.5 }}
            className="relative h-full w-full"
          >
            <Card className="group relative h-full w-full cursor-pointer overflow-hidden border-white/20">
              {/* Gradient Background */}
              <div
                className={`absolute inset-0 bg-gradient-to-br ${highlights[currentIndex].gradient} opacity-20 transition-opacity duration-300 group-hover:opacity-30`}
              />

              {/* Content */}
              <div className="relative flex h-full flex-col justify-end p-8">
                <div className="max-w-2xl">
                  <p className="text-sm font-medium uppercase tracking-wider text-[#525766]">
                    {highlights[currentIndex].type}
                  </p>
                  <h3 className="mt-2 text-3xl font-medium text-[#1C1C1C]">{highlights[currentIndex].title}</h3>
                  <p className="mt-4 text-lg leading-relaxed text-[#1C1C1C]/80">{highlights[currentIndex].summary}</p>
                </div>
              </div>
            </Card>
          </motion.div>
        </AnimatePresence>

        {/* Navigation Buttons */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: isHovered ? 1 : 0 }}
          transition={{ duration: 0.2 }}
          className="absolute inset-y-0 left-4 flex items-center"
        >
          <Button
            variant="ghost"
            size="icon"
            onClick={prevSlide}
            className="h-10 w-10 rounded-full bg-white/80 backdrop-blur-sm hover:bg-white"
          >
            <ChevronLeft className="h-6 w-6" />
          </Button>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: isHovered ? 1 : 0 }}
          transition={{ duration: 0.2 }}
          className="absolute inset-y-0 right-4 flex items-center"
        >
          <Button
            variant="ghost"
            size="icon"
            onClick={nextSlide}
            className="h-10 w-10 rounded-full bg-white/80 backdrop-blur-sm hover:bg-white"
          >
            <ChevronRight className="h-6 w-6" />
          </Button>
        </motion.div>

        {/* Dots Indicator */}
        <div className="absolute bottom-4 left-1/2 flex -translate-x-1/2 gap-2">
          {highlights.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentIndex(index)}
              className={`h-2 w-2 rounded-full transition-all ${
                index === currentIndex ? "bg-white w-6" : "bg-white/50"
              }`}
            />
          ))}
        </div>
      </div>
    </div>
  )
}





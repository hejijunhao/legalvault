// src/app/(app)/library/coming-soon.tsx

"use client"

import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { Progress } from "@/components/ui/progress"
import { FileText, FileSpreadsheet, FileImage, Film, File } from "lucide-react"

const floatingIcons = [FileText, FileSpreadsheet, FileImage, Film, File]

export default function ComingSoon() {
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    const timer = setTimeout(() => {
      setProgress(72)
    }, 500)
    return () => clearTimeout(timer)
  }, [])

  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* Floating icons */}
      {[...Array(30)].map((_, i) => {
        const Icon = floatingIcons[i % floatingIcons.length]
        return (
          <motion.div
            key={i}
            className="absolute text-white"
            initial={{
              x: Math.random() * window.innerWidth,
              y: Math.random() * window.innerHeight,
              scale: Math.random() * 0.5 + 0.5,
            }}
            animate={{
              x: Math.random() * window.innerWidth,
              y: Math.random() * window.innerHeight,
              rotate: Math.random() * 360,
              transition: {
                duration: Math.random() * 10 + 20,
                repeat: Number.POSITIVE_INFINITY,
                repeatType: "reverse",
              },
            }}
          >
            <Icon size={32} />
          </motion.div>
        )
      })}

      {/* Main content */}
      <div className="relative z-10 flex min-h-screen flex-col items-center justify-center px-4 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="max-w-4xl"
        >
          <h2 className="mb-2 text-sm font-normal uppercase tracking-wide text-gray-500">Your Library</h2>
          <h1 className="mb-4 font-['Libre_Baskerville'] text-4xl font-bold italic text-gray-900 md:text-5xl">
            Where Information turns to Knowledge
          </h1>
          <p className="mb-8 mx-auto max-w-3xl text-xl text-gray-600">
            Imagine a legal knowledge hub that doesn&apos;t just store files, but understands them - connecting concepts,
            uncovering relationships, and delivering instant, context-aware insights.
          </p>
          <div className="mx-auto max-w-lg space-y-2">
            <div className="flex justify-between text-sm text-gray-600">
              <span>Development Progress</span>
              <span>{progress}%</span>
            </div>
            <Progress value={progress} className="h-2 w-full" />
          </div>
        </motion.div>
      </div>
    </div>
  )
}




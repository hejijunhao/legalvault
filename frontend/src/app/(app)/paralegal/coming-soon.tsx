// src/app/(app)/paralegal/coming-soon/page.tsx

"use client"

import Image from "next/image"
import { motion } from "framer-motion"
import { Progress } from "@/components/ui/progress"
import { useEffect, useState } from "react"

export default function ComingSoon() {
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    // Animate progress from 0 to 68 over 1.5 seconds
    const timer = setTimeout(() => {
      setProgress(68)
    }, 500)
    return () => clearTimeout(timer)
  }, [])

  return (
    <div className="relative min-h-[calc(100vh-4rem)]">
      <div className="mx-auto max-w-[1440px] px-8">
        <div className="grid min-h-[calc(100vh-4rem)] grid-cols-[1fr,1fr] items-center gap-12">
          {/* Left Content */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="flex flex-col space-y-6"
          >
            <h1 className="font-['Libre_Baskerville'] text-5xl italic text-gray-900">Your Virtual Paralegal</h1>
            <p className="text-xl text-gray-600 leading-relaxed max-w-[500px]">
              We are crafting an intelligent assistant that understands your legal practice. Coming soon to LegalVault.
            </p>
            <div className="h-[2px] w-24 bg-gray-200" />
            <div className="space-y-2">
              <div className="flex justify-between text-sm text-gray-600">
                <span>Development Progress...</span>
                <span>{progress}%</span>
              </div>
              <Progress value={progress} className="h-2 w-full" />
            </div>
          </motion.div>

          {/* Right Image */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{
              opacity: 1,
              y: [0, -8, 0], // Subtle floating motion
            }}
            transition={{
              duration: 1,
              delay: 0.2,
              y: {
                duration: 4,
                repeat: Number.POSITIVE_INFINITY,
                ease: "easeInOut",
              },
            }}
            className="relative h-[700px]"
          >
            <div className="absolute inset-0 rounded-3xl overflow-hidden backdrop-blur-xl bg-white/30 shadow-2xl border border-white/20">
              <div className="relative h-full w-full">
                <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-white/95 pointer-events-none z-10" />
                <Image
                  src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/Virtual%20Paralegals-fie2JYdrbgShF29etJsoiieb2v8SUT.svg"
                  alt="Virtual Paralegal Preview"
                  layout="fill"
                  objectFit="cover"
                  priority
                  className="p-2 scale-110"
                />
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}


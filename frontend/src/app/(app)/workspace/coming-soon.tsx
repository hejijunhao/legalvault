// src/app/(app)/workspace/coming-soon.tsx

"use client"

import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { Progress } from "@/components/ui/progress"

const workspaceFeatures = [
  {
    id: 1,
    title: "Drafting",
    description: "Streamline your document creation process",
    gradient: "from-cyan-400 to-emerald-600",
    rotate: -20,
    translateY: 30,
    translateX: -280,
    zIndex: 1,
  },
  {
    id: 2,
    title: "Legal Cases",
    description: "Track and manage all your active cases",
    gradient: "from-blue-400 to-teal-600",
    rotate: -10,
    translateY: 15,
    translateX: -140,
    zIndex: 2,
  },
  {
    id: 3,
    title: "Client Matters",
    description: "Organize client information and matters",
    gradient: "from-emerald-400 to-cyan-600",
    rotate: 0,
    translateY: 0,
    translateX: 0,
    zIndex: 5,
  },
  {
    id: 4,
    title: "Notes & Tasks",
    description: "Keep track of important updates",
    gradient: "from-teal-400 to-blue-600",
    rotate: 10,
    translateY: 15,
    translateX: 140,
    zIndex: 2,
  },
  {
    id: 5,
    title: "Client Profiles",
    description: "Manage detailed client information",
    gradient: "from-emerald-400 to-green-600",
    rotate: 20,
    translateY: 30,
    translateX: 280,
    zIndex: 1,
  },
]

export default function ComingSoon() {
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    const timer = setTimeout(() => {
      setProgress(65)
    }, 500)
    return () => clearTimeout(timer)
  }, [])

  return (
    <div className="relative min-h-screen overflow-hidden">
      <div className="relative z-10 flex min-h-screen flex-col items-center justify-center px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="max-w-4xl text-center"
        >
          <h2 className="mb-2 text-sm font-normal uppercase tracking-wide text-gray-500">Your Workspace</h2>
          <h1 className="mb-6 font-['Libre_Baskerville'] text-4xl font-bold italic text-gray-900 md:text-5xl">
            Where Legal Work Happens
          </h1>
          <p className="mb-12 text-xl text-gray-600">
            A unified workspace designed for legal professionals. Manage cases, clients, and tasks with unprecedented
            ease and clarity.
          </p>

          <div className="relative mb-16">
            <div className="relative mx-auto h-[400px] w-[900px]">
              {workspaceFeatures.map((feature) => (
                <motion.div
                  key={feature.id}
                  className="absolute left-1/2 top-1/2"
                  initial={{ opacity: 0, scale: 0.8, x: "-50%", y: "-50%" }}
                  animate={{
                    opacity: 1,
                    scale: 1,
                    x: `calc(-50% + ${feature.translateX}px)`,
                    y: `calc(-50% + ${feature.translateY}px)`,
                    rotate: feature.rotate,
                  }}
                  transition={{
                    duration: 0.8,
                    delay: feature.id * 0.1,
                    ease: [0.23, 1, 0.32, 1],
                  }}
                  whileHover={{
                    scale: 1.05,
                    rotate: 0,
                    y: "calc(-50% - 20px)",
                    zIndex: 10,
                  }}
                  style={{ zIndex: feature.zIndex }}
                >
                  <div
                    className={`w-[240px] h-[240px] rounded-2xl bg-gradient-to-br ${feature.gradient} p-[1px] shadow-2xl`}
                  >
                    <div className="relative h-full rounded-2xl bg-black/20 p-5 backdrop-blur-sm">
                      <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-white/10 to-white/5" />
                      <div className="relative flex h-full flex-col justify-between">
                        <h3 className="text-xl font-semibold text-white">{feature.title}</h3>
                        <p className="text-sm text-white/80">{feature.description}</p>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>

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


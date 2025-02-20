// src/components/library/quick-access.tsx

"use client"

import { motion } from "framer-motion"
import { Card } from "@/components/ui/card"
import Link from "next/link"

const sections = [
  {
    id: "searches",
    title: "Past Searches",
    href: "/library/searches",
    gradient: "from-amber-500/10 via-orange-500/10 to-red-500/10",
    glowColor: "from-amber-500/20 to-orange-500/20",
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <motion.path
          d="M11 19C15.4183 19 19 15.4183 19 11C19 6.58172 15.4183 3 11 3C6.58172 3 3 6.58172 3 11C3 15.4183 6.58172 19 11 19Z"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 2, repeat: Number.POSITIVE_INFINITY, repeatType: "loop", ease: "linear" }}
        />
        <motion.path
          d="M21 21L16.65 16.65"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 1, repeat: Number.POSITIVE_INFINITY, repeatType: "loop", ease: "linear", delay: 1 }}
        />
      </svg>
    ),
  },
  {
    id: "bookmarks",
    title: "Bookmarks",
    href: "/library/bookmarks",
    gradient: "from-blue-500/10 via-indigo-500/10 to-purple-500/10",
    glowColor: "from-blue-500/20 to-purple-500/20",
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <motion.path
          d="M19 21L12 16L5 21V5C5 4.46957 5.21071 3.96086 5.58579 3.58579C5.96086 3.21071 6.46957 3 7 3H17C17.5304 3 18.0391 3.21071 18.4142 3.58579C18.7893 3.96086 19 4.46957 19 5V21Z"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          initial={{ y: 2 }}
          animate={{ y: 0 }}
          transition={{ duration: 0.5, repeat: Number.POSITIVE_INFINITY, repeatType: "reverse", ease: "easeInOut" }}
        />
      </svg>
    ),
  },
  {
    id: "collections",
    title: "Collections",
    href: "/library/collections",
    gradient: "from-emerald-500/10 via-teal-500/10 to-cyan-500/10",
    glowColor: "from-emerald-500/20 to-cyan-500/20",
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <motion.rect
          x="3"
          y="3"
          width="18"
          height="18"
          rx="2"
          stroke="currentColor"
          strokeWidth="2"
          initial={{ rotate: -5 }}
          animate={{ rotate: 5 }}
          transition={{ duration: 2, repeat: Number.POSITIVE_INFINITY, repeatType: "reverse", ease: "easeInOut" }}
        />
        <motion.rect
          x="6"
          y="6"
          width="12"
          height="12"
          rx="1"
          stroke="currentColor"
          strokeWidth="2"
          initial={{ rotate: 5 }}
          animate={{ rotate: -5 }}
          transition={{ duration: 2, repeat: Number.POSITIVE_INFINITY, repeatType: "reverse", ease: "easeInOut" }}
        />
      </svg>
    ),
  },
]

export function QuickAccessSections() {
  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
      {sections.map((section, index) => (
        <motion.div
          key={section.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: index * 0.1 }}
        >
          <Link href={section.href}>
            <Card className="group relative isolate flex h-20 cursor-pointer items-center overflow-hidden rounded-2xl border-0 bg-white/20 p-6 backdrop-blur-md transition-all duration-500">
              {/* Gradient background */}
              <div
                className={`absolute inset-0 -z-20 bg-gradient-to-br ${section.gradient} opacity-50 transition-opacity duration-500 group-hover:opacity-100`}
              />

              {/* Frosted glass effect */}
              <div className="absolute inset-0 -z-10 backdrop-blur-xl" />

              {/* Glow effect */}
              <div
                className={`absolute -inset-px -z-10 rounded-2xl bg-gradient-to-br ${section.glowColor} opacity-0 blur-xl transition-opacity duration-500 group-hover:opacity-100`}
              />

              {/* Content */}
              <motion.h2
                className="text-lg font-light tracking-wide text-gray-800 transition-colors duration-300 group-hover:text-gray-900"
                initial={{ x: 0 }}
                whileHover={{ x: -4 }}
              >
                {section.title}
              </motion.h2>

              <motion.div
                className="ml-auto text-gray-400 transition-colors duration-300 group-hover:text-gray-600"
                initial={{ x: 0 }}
                whileHover={{ x: 4 }}
              >
                {section.icon}
              </motion.div>
            </Card>
          </Link>
        </motion.div>
      ))}
    </div>
  )
}


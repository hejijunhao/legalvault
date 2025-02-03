// src/components/profile/user-profile/personal-info.tsx

"use client"

import { motion } from "framer-motion"
import Image from "next/image"
import { Card } from "@/components/ui/card"
import { Mail, Phone, MapPin, Globe, Languages } from "lucide-react"

interface PersonalInfoProps {
  data: {
    profilePicture: string
    fullName: string
    jobTitle: string
    email: string
    phone: string
    officeLocation: string
    timeZone: string
    languages: string[]
    bio: string
  }
}

export function PersonalInfo({ data }: PersonalInfoProps) {
  return (
    <Card className="overflow-hidden bg-white/60 backdrop-blur-md">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="relative h-40 bg-gradient-to-r from-blue-400 to-purple-500"
      >
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: "spring", stiffness: 260, damping: 20 }}
          className="absolute -bottom-16 left-6"
        >
          <Image
            src={data.profilePicture || "/placeholder.svg"}
            alt={data.fullName}
            width={120}
            height={120}
            className="rounded-full border-4 border-white shadow-lg"
          />
        </motion.div>
      </motion.div>
      <div className="p-6 pt-20">
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          className="text-2xl font-bold text-gray-900"
        >
          {data.fullName}
        </motion.h2>
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.5 }}
          className="text-gray-600"
        >
          {data.jobTitle}
        </motion.p>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.5 }}
          className="mt-4 space-y-2"
        >
          <div className="flex items-center text-gray-600">
            <Mail className="mr-2 h-5 w-5" />
            {data.email}
          </div>
          <div className="flex items-center text-gray-600">
            <Phone className="mr-2 h-5 w-5" />
            {data.phone}
          </div>
          <div className="flex items-center text-gray-600">
            <MapPin className="mr-2 h-5 w-5" />
            {data.officeLocation}
          </div>
          <div className="flex items-center text-gray-600">
            <Globe className="mr-2 h-5 w-5" />
            {data.timeZone}
          </div>
          <div className="flex items-center text-gray-600">
            <Languages className="mr-2 h-5 w-5" />
            {data.languages.join(", ")}
          </div>
        </motion.div>
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.5 }}
          className="mt-4 text-gray-600"
        >
          {data.bio}
        </motion.p>
      </div>
    </Card>
  )
}


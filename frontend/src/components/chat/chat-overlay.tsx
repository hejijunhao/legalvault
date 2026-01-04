// src/components/chat/chat-overlay.tsx

"use client"

import { AnimatePresence, motion } from "framer-motion"
import { animations, transitions } from "@/lib/animations"
import { ChatWindow } from "./chat-window"

interface ChatOverlayProps {
  isOpen: boolean
  onClose: () => void
}

export function ChatOverlay({ isOpen, onClose }: ChatOverlayProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            {...animations.fadeIn}
            className="fixed inset-0 z-50 bg-black/20 backdrop-blur-sm"
            onClick={onClose}
          />

          {/* Chat Window */}
          <motion.div
            {...animations.popIn}
            transition={transitions.spring}
            className="fixed right-4 top-20 z-50 w-full max-w-md"
          >
            <ChatWindow onClose={onClose} />
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}


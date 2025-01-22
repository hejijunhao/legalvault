// src/components/chat/chat-overlay.tsx

"use client"

import { AnimatePresence, motion } from "framer-motion"
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
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-black/20 backdrop-blur-sm"
            onClick={onClose}
          />

          {/* Chat Window */}
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{
              opacity: 1,
              y: 0,
              scale: 1,
              transition: {
                type: "spring",
                stiffness: 300,
                damping: 30,
              },
            }}
            exit={{
              opacity: 0,
              y: 20,
              scale: 0.95,
              transition: {
                duration: 0.2,
              },
            }}
            className="fixed right-4 top-20 z-50 w-full max-w-md"
          >
            <ChatWindow onClose={onClose} />
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}


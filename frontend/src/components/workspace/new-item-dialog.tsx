// src/components/workspace/new-item-dialog.tsx

"use client"

import * as React from "react"
import { motion, AnimatePresence } from "framer-motion"
import * as DialogPrimitive from "@radix-ui/react-dialog"
import { X } from 'lucide-react'
import { cn } from "@/lib/utils"

interface NewItemDialogProps {
  isOpen: boolean
  onClose: () => void
}

export function NewItemDialog({ isOpen, onClose }: NewItemDialogProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <DialogPrimitive.Root open={isOpen} onOpenChange={onClose}>
          <DialogPrimitive.Portal forceMount>
            <div className="fixed inset-0 z-50">
              <div className="mx-auto max-w-[1440px] px-4 h-full flex items-center justify-center">
                <DialogPrimitive.Overlay className="fixed inset-0 bg-black/20 backdrop-blur-sm" />
                <DialogPrimitive.Content asChild forceMount>
                  <motion.div
                    className={cn(
                      "relative z-50 grid w-full max-w-lg gap-4 border border-white/10 bg-white/80 p-6 shadow-lg duration-200 sm:rounded-lg",
                      "backdrop-blur-md"
                    )}
                    style={{
                      width: 'calc(100% - 2rem)',
                      maxWidth: '28rem',
                    }}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    transition={{ duration: 0.3, ease: "easeInOut" }}
                  >
                    <DialogPrimitive.Title className="text-lg font-semibold leading-none tracking-tight text-[#1C1C1C]">
                      Create New Workspace
                    </DialogPrimitive.Title>
                    <DialogPrimitive.Description className="text-sm text-[#525766]">
                      Choose the type of Workspace you would like to create.
                    </DialogPrimitive.Description>
                    <div className="flex gap-4">
                      <button
                        onClick={() => {
                          // Handle creating a new project
                          onClose()
                        }}
                        className="flex-1 rounded-md bg-[#9FE870]/20 p-4 text-center text-sm font-medium text-[#09332B] transition-colors hover:bg-[#9FE870]/30"
                      >
                        New Project
                      </button>
                      <button
                        onClick={() => {
                          // Handle creating a new client profile
                          onClose()
                        }}
                        className="flex-1 rounded-md bg-[#93C5FD]/20 p-4 text-center text-sm font-medium text-[#1E3A8A] transition-colors hover:bg-[#93C5FD]/30"
                      >
                        New Client Profile
                      </button>
                    </div>
                    <DialogPrimitive.Close className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-accent data-[state=open]:text-muted-foreground">
                      <X className="h-4 w-4 text-[#525766]" />
                      <span className="sr-only">Close</span>
                    </DialogPrimitive.Close>
                  </motion.div>
                </DialogPrimitive.Content>
              </div>
            </div>
          </DialogPrimitive.Portal>
        </DialogPrimitive.Root>
      )}
    </AnimatePresence>
  )
}
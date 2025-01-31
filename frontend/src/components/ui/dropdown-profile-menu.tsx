// src/components/ui/dropdown-profile-menu.tsx

"use client"

import { useRef, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import Link from "next/link"
import { User, Settings, Building, LogOut, CreditCard } from "lucide-react"

interface DropdownProfileMenuProps {
  isOpen: boolean
  onClose: () => void
}

const menuItems = [
  { icon: User, label: "Profile", href: "/profile" },
  { icon: CreditCard, label: "Billing", href: "/billing" },
  { icon: Settings, label: "Settings", href: "/settings" },
  { icon: Building, label: "Company", href: "/company" },
  { icon: LogOut, label: "Logout", href: "/logout" },
]

export function DropdownProfileMenu({ isOpen, onClose }: DropdownProfileMenuProps) {
  const dropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        onClose()
      }
    }

    document.addEventListener("mousedown", handleClickOutside)
    return () => {
      document.removeEventListener("mousedown", handleClickOutside)
    }
  }, [onClose])

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          ref={dropdownRef}
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.2 }}
          className="absolute right-0 mt-2 w-48 rounded-md bg-white py-2 shadow-lg ring-1 ring-black ring-opacity-5"
        >
          {menuItems.map((item) => (
            <Link
              key={item.label}
              href={item.href}
              className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              onClick={onClose}
            >
              <item.icon className="mr-3 h-4 w-4 text-gray-400" />
              {item.label}
            </Link>
          ))}
        </motion.div>
      )}
    </AnimatePresence>
  )
}
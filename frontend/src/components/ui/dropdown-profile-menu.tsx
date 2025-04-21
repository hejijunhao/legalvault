// src/components/ui/dropdown-profile-menu.tsx

"use client"

import { useRef, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import Link from "next/link"
import { User, Settings, Building, LogOut, CreditCard } from "lucide-react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/contexts/auth-context"

interface DropdownProfileMenuProps {
  isOpen: boolean
  onClose: () => void
}

export function DropdownProfileMenu({ isOpen, onClose }: DropdownProfileMenuProps) {
  const dropdownRef = useRef<HTMLDivElement>(null)
  const router = useRouter()
  const { user, logout, isLoading } = useAuth()

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

  const handleLogout = async () => {
    await logout()
    onClose()
    router.push('/login')
  }

  const menuItems = [
    { 
      icon: User, 
      label: "Profile", 
      href: user ? `/profile/${user.id}` : "#",
      onClick: () => user && onClose()
    },
    { icon: CreditCard, label: "Billing", href: "/billing", onClick: onClose },
    { icon: Settings, label: "Settings", href: "/settings", onClick: onClose },
    { icon: Building, label: "Company", href: "/company", onClick: onClose },
    { 
      icon: LogOut, 
      label: "Logout", 
      href: "#",
      onClick: handleLogout
    },
  ]

  if (isLoading) {
    return null
  }

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
              className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 transition-colors hover:bg-gray-100"
              onClick={item.onClick}
            >
              <item.icon className="h-4 w-4" />
              <span>{item.label}</span>
            </Link>
          ))}
        </motion.div>
      )}
    </AnimatePresence>
  )
}
"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Bell, Globe, Settings } from 'lucide-react'
import { Button } from "@/components/ui/button"
import Image from "next/image"

const navigation = [
  { name: "Workspace", href: "/workspace" },
  { name: "Library", href: "/library" },
  { name: "Paralegal", href: "/paralegal" },
]

export function Header() {
  const pathname = usePathname()

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-white">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <div className="flex items-center">
          <Link href="/" className="flex items-center space-x-2">
            <Image
              src="/placeholder.svg"
              alt="LegalVault Logo"
              width={32}
              height={32}
              className="h-8 w-8"
            />
          </Link>
        </div>

        <nav className="flex items-center space-x-8">
          {navigation.map((item) => (
            <Link
              key={item.name}
              href={item.href}
              className={`text-sm font-medium transition-colors hover:text-gray-900 ${
                pathname === item.href ? "text-gray-900" : "text-gray-500"
              }`}
            >
              {item.name}
            </Link>
          ))}
        </nav>

        <div className="flex items-center space-x-2">
          <Button variant="ghost" size="icon">
            <Settings className="h-5 w-5 text-gray-500" />
            <span className="sr-only">Settings</span>
          </Button>
          <Button variant="ghost" size="icon">
            <Bell className="h-5 w-5 text-gray-500" />
            <span className="sr-only">Notifications</span>
          </Button>
          <Button variant="ghost" size="icon">
            <Globe className="h-5 w-5 text-gray-500" />
            <span className="sr-only">Language</span>
          </Button>
        </div>
      </div>
    </header>
  )
}
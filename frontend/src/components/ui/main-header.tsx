// src/components/ui/main-header.tsx

"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import Image from "next/image"
import { cn } from "@/lib/utils"
import { DropdownProfileMenu } from "@/components/ui/dropdown-profile-menu"

type NavItem = { name: string; href: string };
const navigation: NavItem[] = [
  { name: "Workspace", href: "/workspace" },
  { name: "Library", href: "/library" },
  { name: "Research", href: "/research" },
  { name: "Paralegal", href: "/paralegal" },
];

export function MainHeader() {
  const pathname = usePathname()
  const [isProfileDropdownOpen, setIsProfileDropdownOpen] = useState(false)
  const [isScrolled, setIsScrolled] = useState(false)
  
  // Check if we're on a research page
  const isResearchPage = pathname.startsWith('/research/') && pathname !== '/research'
  
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10)
    }
    
    if (isResearchPage) {
      window.addEventListener('scroll', handleScroll)
      handleScroll() // Check initial scroll position
    }
    
    return () => {
      window.removeEventListener('scroll', handleScroll)
    }
  }, [isResearchPage])

  return (
    <>
      <header 
        className={cn(
          "sticky top-0 z-50 w-full transition-all duration-300",
          isResearchPage && isScrolled
            ? "bg-white/25 backdrop-blur-2xl backdrop-saturate-150 border-b border-white/5 shadow-[0_8px_32px_rgba(0,0,0,0.02)] bg-gradient-to-b from-white/30 to-white/20"
            : "bg-transparent"
        )}
      >
        <div className="mx-auto w-full max-w-[1440px] px-4">
          <div className="flex h-16 items-center justify-between" style={{ position: 'relative' }}>
            <div className="flex items-center">
              <Link href="/" className="flex items-center space-x-2">
                <Image
                  src="/images/legalvault-logo.svg"
                  alt="LegalVault Logo"
                  width={0}
                  height={32}
                  className="h-8 w-auto"
                />
              </Link>
            </div>

            <nav className="flex items-center space-x-8">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`text-center font-inter text-base font-normal leading-6 ${
                    pathname.startsWith(item.href) ? "text-[#525766]" : "text-[#8992A9]"
                  }`}
                >
                  {item.name}
                </Link>
              ))}
            </nav>

            <div className="flex items-center space-x-4">
              <svg xmlns="http://www.w3.org/2000/svg" width="25" height="24" viewBox="0 0 25 24" fill="none">
                <path
                  d="M6.57575 8.90991V11.7999C6.57575 12.4099 6.31575 13.3399 6.00575 13.8599L4.85575 15.7699C4.14575 16.9499 4.63575 18.2599 5.93575 18.6999C10.2458 20.1399 14.8958 20.1399 19.2058 18.6999C20.4158 18.2999 20.9458 16.8699 20.2858 15.7699L19.1358 13.8599C18.8358 13.3399 18.5758 12.4099 18.5758 11.7999V8.90991C18.5758 5.60991 15.8758 2.90991 12.5758 2.90991C9.26575 2.90991 6.57575 5.59991 6.57575 8.90991Z"
                  stroke="#8992A9"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                />
                <path
                  d="M13.4656 2.99994C12.5056 2.87994 11.5856 2.94994 10.7256 3.19994C11.0156 2.45994 11.7356 1.93994 12.5756 1.93994C13.4156 1.93994 14.1356 2.45994 14.4256 3.19994C14.1156 3.10994 13.7956 3.03994 13.4656 2.99994Z"
                  stroke="#8992A9"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                <path
                  d="M15.5757 19.0601C15.5757 20.7101 14.2257 22.0601 12.5757 22.0601C11.7557 22.0601 10.9957 21.7201 10.4557 21.1801C9.91568 20.6401 9.57568 19.8801 9.57568 19.0601"
                  stroke="#8992A9"
                  strokeWidth="1.5"
                />
              </svg>
              <div className="relative">
                <button
                  onClick={() => setIsProfileDropdownOpen(!isProfileDropdownOpen)}
                  className="rounded-full p-2 transition-colors hover:bg-black/5"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="25" height="24" viewBox="0 0 25 24" fill="none">
                    <path
                      d="M7.55566 21C3.55566 21 2.55566 20 2.55566 16V8C2.55566 4 3.55566 3 7.55566 3H17.5557C21.5557 3 22.5557 4 22.5557 8V16C22.5557 20 21.5557 21 17.5557 21H7.55566Z"
                      stroke="#8992A9"
                      strokeWidth="1.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                    <path
                      d="M14.5557 8H19.5557"
                      stroke="#8992A9"
                      strokeWidth="1.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                    <path
                      d="M15.5557 12H19.5557"
                      stroke="#8992A9"
                      strokeWidth="1.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                    <path
                      d="M17.5557 16H19.5557"
                      stroke="#8992A9"
                      strokeWidth="1.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                    <path
                      fillRule="evenodd"
                      clipRule="evenodd"
                      d="M9.05561 11.2899C8.05597 11.2899 7.24561 10.4796 7.24561 9.47992C7.24561 8.48029 8.05597 7.66992 9.05561 7.66992C10.0552 7.66992 10.8656 8.48029 10.8656 9.47992C10.8656 10.4796 10.0552 11.2899 9.05561 11.2899Z"
                      stroke="#8992A9"
                      strokeWidth="1.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                    <path
                      d="M12.5557 16.33C12.4157 14.88 11.2657 13.74 9.81566 13.61C9.31566 13.56 8.80566 13.56 8.29566 13.61C6.84566 13.75 5.69566 14.88 5.55566 16.33"
                      stroke="#8992A9"
                      strokeWidth="1.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </button>
                <DropdownProfileMenu
                  isOpen={isProfileDropdownOpen}
                  onClose={() => setIsProfileDropdownOpen(false)}
                />
              </div>
            </div>
          </div>
        </div>
      </header>
    </>
  )
}

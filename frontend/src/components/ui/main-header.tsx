// src/components/ui/main-header.tsx

"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import Image from "next/image"

const navigation = [
  { name: "Workspace", href: "/workspace" },
  { name: "Library", href: "/library" },
  { name: "Paralegal", href: "/paralegal" },
]

export function MainHeader() {
  const pathname = usePathname()

  return (
    <header className="sticky top-0 z-50 w-full bg-transparent">
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
              className={`text-center font-inter text-base font-normal leading-6 ${
                pathname === item.href
                  ? "text-[#525766]"
                  : "text-[#8992A9]"
              }`}
            >
              {item.name}
            </Link>
          ))}
        </nav>

        <div className="flex items-center space-x-4">
          <svg xmlns="http://www.w3.org/2000/svg" width="25" height="24" viewBox="0 0 25 24" fill="none">
            <path d="M12.5557 22C13.6602 22 14.5557 21.1046 14.5557 20C14.5557 18.8954 13.6602 18 12.5557 18C11.4511 18 10.5557 18.8954 10.5557 20C10.5557 21.1046 11.4511 22 12.5557 22Z" fill="#8992A9"/>
            <path d="M12.5557 6C13.6602 6 14.5557 5.10457 14.5557 4C14.5557 2.89543 13.6602 2 12.5557 2C11.4511 2 10.5557 2.89543 10.5557 4C10.5557 5.10457 11.4511 6 12.5557 6Z" fill="#8992A9"/>
            <path d="M6.89868 19.657C8.00325 19.657 8.89868 18.7616 8.89868 17.657C8.89868 16.5524 8.00325 15.657 6.89868 15.657C5.79411 15.657 4.89868 16.5524 4.89868 17.657C4.89868 18.7616 5.79411 19.657 6.89868 19.657Z" fill="#8992A9"/>
            <path d="M18.2126 8.34302C19.3172 8.34302 20.2126 7.44759 20.2126 6.34302C20.2126 5.23845 19.3172 4.34302 18.2126 4.34302C17.1081 4.34302 16.2126 5.23845 16.2126 6.34302C16.2126 7.44759 17.1081 8.34302 18.2126 8.34302Z" fill="#8992A9"/>
            <path d="M4.55569 14.001C5.66081 14.001 6.55669 13.1051 6.55669 12C6.55669 10.8949 5.66081 9.99902 4.55569 9.99902C3.45057 9.99902 2.55469 10.8949 2.55469 12C2.55469 13.1051 3.45057 14.001 4.55569 14.001Z" fill="#8992A9"/>
            <path d="M20.5557 14C21.6602 14 22.5557 13.1046 22.5557 12C22.5557 10.8954 21.6602 10 20.5557 10C19.4511 10 18.5557 10.8954 18.5557 12C18.5557 13.1046 19.4511 14 20.5557 14Z" fill="#8992A9"/>
            <path d="M6.89868 8.34399C8.00325 8.34399 8.89868 7.44856 8.89868 6.34399C8.89868 5.23942 8.00325 4.34399 6.89868 4.34399C5.79411 4.34399 4.89868 5.23942 4.89868 6.34399C4.89868 7.44856 5.79411 8.34399 6.89868 8.34399Z" fill="#8992A9"/>
            <path d="M18.2126 19.658C19.3172 19.658 20.2126 18.7625 20.2126 17.658C20.2126 16.5534 19.3172 15.658 18.2126 15.658C17.1081 15.658 16.2126 16.5534 16.2126 17.658C16.2126 18.7625 17.1081 19.658 18.2126 19.658Z" fill="#8992A9"/>
          </svg>
          <svg xmlns="http://www.w3.org/2000/svg" width="25" height="24" viewBox="0 0 25 24" fill="none">
            <path d="M6.57575 8.90991V11.7999C6.57575 12.4099 6.31575 13.3399 6.00575 13.8599L4.85575 15.7699C4.14575 16.9499 4.63575 18.2599 5.93575 18.6999C10.2458 20.1399 14.8958 20.1399 19.2058 18.6999C20.4158 18.2999 20.9458 16.8699 20.2858 15.7699L19.1358 13.8599C18.8358 13.3399 18.5758 12.4099 18.5758 11.7999V8.90991C18.5758 5.60991 15.8758 2.90991 12.5758 2.90991C9.26575 2.90991 6.57575 5.59991 6.57575 8.90991Z" stroke="#8992A9" strokeWidth="1.5" strokeLinecap="round"/>
            <path d="M13.4656 2.99994C12.5056 2.87994 11.5856 2.94994 10.7256 3.19994C11.0156 2.45994 11.7356 1.93994 12.5756 1.93994C13.4156 1.93994 14.1356 2.45994 14.4256 3.19994C14.1156 3.10994 13.7956 3.03994 13.4656 2.99994Z" stroke="#8992A9" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M15.5757 19.0601C15.5757 20.7101 14.2257 22.0601 12.5757 22.0601C11.7557 22.0601 10.9957 21.7201 10.4557 21.1801C9.91568 20.6401 9.57568 19.8801 9.57568 19.0601" stroke="#8992A9" strokeWidth="1.5"/>
          </svg>
          <svg xmlns="http://www.w3.org/2000/svg" width="25" height="24" viewBox="0 0 25 24" fill="none">
            <path d="M7.55566 21C3.55566 21 2.55566 20 2.55566 16V8C2.55566 4 3.55566 3 7.55566 3H17.5557C21.5557 3 22.5557 4 22.5557 8V16C22.5557 20 21.5557 21 17.5557 21H7.55566Z" stroke="#8992A9" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M14.5557 8H19.5557" stroke="#8992A9" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M15.5557 12H19.5557" stroke="#8992A9" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M17.5557 16H19.5557" stroke="#8992A9" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            <path fillRule="evenodd" clipRule="evenodd" d="M9.05561 11.2899C8.05597 11.2899 7.24561 10.4796 7.24561 9.47992C7.24561 8.48029 8.05597 7.66992 9.05561 7.66992C10.0552 7.66992 10.8656 8.48029 10.8656 9.47992C10.8656 10.4796 10.0552 11.2899 9.05561 11.2899Z" stroke="#8992A9" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M12.5557 16.33C12.4157 14.88 11.2657 13.74 9.81566 13.61C9.31566 13.56 8.80566 13.56 8.29566 13.61C6.84566 13.75 5.69566 14.88 5.55566 16.33" stroke="#8992A9" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </div>
      </div>
    </header>
  )
}


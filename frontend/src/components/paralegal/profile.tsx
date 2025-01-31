// src/components/paralegal/profile.tsx

import { Card } from "@/components/ui/card"
import Image from "next/image"

interface ProfileProps {
  name: string
  email: string
}

export function Profile({ name, email }: ProfileProps) {
  return (
    <div className="relative h-[674px] w-[412px] flex-shrink-0">
      <Card className="h-full w-full overflow-hidden rounded-[22.547px]">
        <div className="relative h-full w-full">
          {/* Background Pattern */}
          <div
            className="absolute inset-0"
            style={{
              backgroundImage: `url("/images/vp-background-pattern.svg")`,
              backgroundSize: 'cover',
              backgroundPosition: 'center',
            }}
          />

          {/* VP Profile Image */}
          <div className="absolute inset-0">
            <Image
              src="/images/vp-robert-mcnamara.png"
              alt="Virtual Paralegal Robert McNamara"
              width={412}
              height={674}
              className="h-full w-full object-cover"
              priority
            />
          </div>
        </div>
      </Card>

      {/* Text Overlay */}
      <div className="absolute bottom-0 left-0 h-[132px] w-full flex-shrink-0">
        <svg
          width="412"
          height="132"
          viewBox="0 0 412 132"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="absolute bottom-0 left-0"
        >
          <path d="M0 0H412V112C412 123.046 403.046 132 392 132H20C8.95431 132 0 123.046 0 112V0Z" fill="#111827"/>
          <path d="M0 0H412V112C412 123.046 403.046 132 392 132H20C8.95431 132 0 123.046 0 112V0Z" fill="url(#paint0_linear_1277_5828)" fillOpacity="0.2"/>
          <path d="M0 0H412V112C412 123.046 403.046 132 392 132H20C8.95431 132 0 123.046 0 112V0Z" fill="url(#paint1_linear_1277_5828)" fillOpacity="0.15"/>
          <defs>
            <linearGradient id="paint0_linear_1277_5828" x1="206" y1="0" x2="206.77" y2="194.915" gradientUnits="userSpaceOnUse">
              <stop stopColor="#2E2E2E"/>
              <stop offset="0.457944" stopColor="#4B4748"/>
              <stop offset="1" stopColor="#73263F"/>
              <stop offset="1" stopColor="#1C1C1C" stopOpacity="0.34"/>
            </linearGradient>
            <linearGradient id="paint1_linear_1277_5828" x1="30.6283" y1="46.8785" x2="451.436" y2="93.8859" gradientUnits="userSpaceOnUse">
              <stop stopColor="#F9F9F9" stopOpacity="0.39"/>
              <stop offset="0.428195" stopColor="#242424" stopOpacity="0.52"/>
              <stop offset="1" stopOpacity="0"/>
              <stop offset="1" stopColor="#484848" stopOpacity="0.62"/>
            </linearGradient>
          </defs>
        </svg>
        <div className="absolute bottom-0 left-0 flex h-full w-full flex-col justify-end p-6">
          <div className="w-[340px] flex-shrink-0">
            <h1 className="h-[29px] w-[338px] flex-shrink-0 text-[20px] font-bold text-white text-shadow-sm">
              {name}
            </h1>
            <p className="h-[29px] w-[340px] flex-shrink-0 text-[18px] font-normal text-[#FAFAFA] text-shadow-xs">
              {email}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
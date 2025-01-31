// src/components/library/search-bar.tsx

"use client"

import { useState } from "react"

export function SearchBar() {
  const [value, setValue] = useState("")

  return (
    <div className="w-full border-b border-[#8992A9]/20">
      <div className="mx-auto max-w-[1440px] px-4">
        <div className="relative w-full">
          <input
            type="text"
            placeholder="I'm looking for..."
            value={value}
            onChange={(e) => setValue(e.target.value)}
            className={`
              font-['Libre_Baskerville'] 
              w-full max-w-auto h-[44px] 
              flex flex-col justify-center flex-shrink-0
              bg-transparent
              text-[32px] font-normal italic leading-[24px]
              ${value ? "text-[#1C1C1C]" : "text-[#8992A9]/60"}
              placeholder:text-[#8992A9]/60 
              placeholder:italic
              focus:outline-none
              transition-colors
              duration-200
            `}
          />
        </div>
      </div>
    </div>
  )
}

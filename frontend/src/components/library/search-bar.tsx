// src/components/library/search-bar.tsx

import { Search } from 'lucide-react'

export function SearchBar() {
  return (
    <div className="flex w-full flex-col items-start gap-[15px]">
      <div className="relative w-full max-w-[467px]">
        <input
          type="text"
          placeholder="I'm looking for..."
          className="search-input h-[44px] w-full border-b border-[#8992A9]/20 bg-transparent text-[32px] font-normal italic leading-6 text-[#8992A9]/60 placeholder:text-[#8992A9]/60 focus:outline-none"
        />
        <Search className="absolute right-4 top-1/2 h-5 w-5 -translate-y-1/2 text-[#8992A9]/60" />
      </div>
    </div>
  )
}


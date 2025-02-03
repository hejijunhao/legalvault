// src/components/collections/collections-nav.tsx

"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Search, Grid, List } from "lucide-react"

export function CollectionsNav() {
  const [view, setView] = useState<"grid" | "list">("grid")

  return (
    <div className="mb-8 flex items-center justify-between">
      <div className="relative w-full max-w-md">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
        <Input placeholder="Search collections..." className="pl-10" />
      </div>
      <div className="flex items-center gap-2">
        <Button variant={view === "grid" ? "default" : "ghost"} size="icon" onClick={() => setView("grid")}>
          <Grid className="h-4 w-4" />
        </Button>
        <Button variant={view === "list" ? "default" : "ghost"} size="icon" onClick={() => setView("list")}>
          <List className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}


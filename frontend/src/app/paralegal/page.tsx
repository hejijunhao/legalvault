// app/paralegal/page.tsx

import { Profile } from "@/components/paralegal/profile"
import { Abilities } from "@/components/paralegal/abilities"
import { Behaviours } from "@/components/paralegal/behaviours"
import { Knowledge } from "@/components/paralegal/knowledge"
import { Access } from "@/components/paralegal/access"

export default function ParalegalPage() {
  return (
    <div className="mx-auto max-w-[1440px] px-4 py-6">
      <div className="grid gap-6 lg:grid-cols-[412px,1fr]">
        <Profile
          name="Robert McNamara"
          email="robert.mcnamara@lppartners.com"
        />
        <div className="grid h-[674px] grid-rows-[1fr,1fr,1fr] gap-6">
          <Abilities />
          <Behaviours />
          <div className="grid grid-cols-2 gap-6">
            <Knowledge />
            <Access />
          </div>
        </div>
      </div>
    </div>
  )
}


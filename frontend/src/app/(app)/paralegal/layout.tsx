// src/app/(app)/paralegal/layout.tsx

import React from 'react'

export default function ParalegalLayout({
                                          children,
                                        }: {
  children: React.ReactNode
}) {
  return (
    <div>
      {children}
    </div>
  )
}
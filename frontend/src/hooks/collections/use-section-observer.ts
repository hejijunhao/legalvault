// src/hooks/collections/use-section-observer.ts

"use client"

import { useState, useEffect, type RefObject } from "react"

interface Section {
  id: string
  title: string
  ref: RefObject<HTMLDivElement | null> // Changed from HTMLDivElement
}

export function useSectionObserver(sections: Section[], offset = 0) {
  const [currentSectionId, setCurrentSectionId] = useState<string>("")

  useEffect(() => {
    const handleScroll = () => {
      const sectionElements = sections.filter(
        (section): section is Section & { ref: { current: HTMLDivElement | null } } => section.ref.current !== null
      )

      const currentSection = sectionElements.find((section) => {
        const rect = section.ref.current?.getBoundingClientRect()
        return rect !== undefined && rect.top <= offset && rect.bottom > offset
      })

      if (currentSection) {
        setCurrentSectionId(currentSection.id)
      } else if (sectionElements.length > 0) {
        const isAtBottom = window.innerHeight + window.scrollY >= document.documentElement.scrollHeight
        if (isAtBottom) {
          setCurrentSectionId(sectionElements[sectionElements.length - 1].id)
        }
      }
    }

    handleScroll()
    window.addEventListener("scroll", handleScroll, { passive: true })
    return () => window.removeEventListener("scroll", handleScroll)
  }, [sections, offset])

  const scrollToSection = (sectionId: string) => {
    const section = sections.find((s) => s.id === sectionId)
    if (section?.ref.current) {
      const sectionTop = section.ref.current.getBoundingClientRect().top + window.scrollY
      const scrollPosition = sectionTop - offset

      window.scrollTo({
        top: scrollPosition,
        behavior: "smooth",
      })
    }
  }

  return { currentSectionId, scrollToSection }
}



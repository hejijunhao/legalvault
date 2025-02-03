// src/hooks/collections/use-section-observer.ts

"use client"

import { useState, useEffect, type RefObject } from "react"

interface Section {
  id: string
  ref: RefObject<HTMLElement>
}

export function useSectionObserver(sections: Section[], offset = 0) {
  const [currentSectionId, setCurrentSectionId] = useState<string>("")

  useEffect(() => {
    const handleScroll = () => {
      // Get all section elements
      const sectionElements = sections
        .map((section) => ({
          id: section.id,
          element: section.ref.current,
        }))
        .filter((section): section is { id: string; element: HTMLElement } => section.element !== null)

      // Find the first section that's in view
      const currentSection = sectionElements.find((section) => {
        const rect = section.element.getBoundingClientRect()
        // Consider a section "in view" when its top is at or above the offset
        // and its bottom is still below the offset
        return rect.top <= offset && rect.bottom > offset
      })

      if (currentSection) {
        setCurrentSectionId(currentSection.id)
      } else if (sectionElements.length > 0) {
        // If no section is in view, use the last section if we're at the bottom of the page
        const isAtBottom = window.innerHeight + window.scrollY >= document.documentElement.scrollHeight
        if (isAtBottom) {
          setCurrentSectionId(sectionElements[sectionElements.length - 1].id)
        }
      }
    }

    // Set initial section
    handleScroll()

    // Add scroll listener
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




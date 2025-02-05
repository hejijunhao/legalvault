// src/components/library/file-finder.tsx

"use client"

import { useState, useEffect } from "react"
import { FileList, type File } from "./file-list"
import { FileDetails } from "./file-details"
import { SectionNav } from "./section-nav"
import { FileText, FileSignature, Scale, Building2, FileSpreadsheet } from "lucide-react"

interface FileFinderProps {
  files: File[]
}

export function FileFinder({ files }: FileFinderProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [hoveredFile, setHoveredFile] = useState<File | null>(null)
  const [activeSection, setActiveSection] = useState<string>("")

  // Group files by category
  const groupedFiles = files.reduce(
    (acc, file) => {
      if (!acc[file.category]) {
        acc[file.category] = []
      }
      acc[file.category].push(file)
      return acc
    },
    {} as Record<string, File[]>,
  )

  // Create sections data
  const sections = Object.entries(groupedFiles).map(([category, files]) => {
    const getIcon = (category: string) => {
      switch (category.toLowerCase()) {
        case "agreements":
          return FileSignature
        case "legal":
          return Scale
        case "sales":
          return FileSpreadsheet
        case "project documentation":
          return Building2
        default:
          return FileText
      }
    }

    return {
      id: category.toLowerCase(),
      name: category,
      icon: getIcon(category),
      count: files.length,
    }
  })

  // Set initial active section
  useEffect(() => {
    if (sections.length > 0 && !activeSection) {
      setActiveSection(sections[0].id)
    }
  }, [sections, activeSection])

  const handleFileSelect = (file: File) => {
    setSelectedFile(file)
  }

  const handleFileHover = (file: File | null) => {
    if (!selectedFile) {
      setHoveredFile(file)
    }
  }

  const handleSectionClick = (sectionId: string) => {
    setActiveSection(sectionId)
    // Scroll to section
    const sectionElement = document.getElementById(sectionId)
    if (sectionElement) {
      sectionElement.scrollIntoView({ behavior: "smooth" })
    }
  }

  // Show details for the selected file if there is one, otherwise show the hovered file
  const fileToShow = selectedFile || hoveredFile

  return (
    <div className="flex h-[calc(100vh-200px)] gap-6">
      {/* Section Navigation */}
      <div className="w-64 flex-shrink-0 rounded-xl border border-neutral-200 bg-white/50 backdrop-blur-sm">
        <SectionNav sections={sections} activeSection={activeSection} onSectionClick={handleSectionClick} />
      </div>

      {/* File List */}
      <div className="w-[480px] flex-shrink-0 overflow-y-auto rounded-xl border border-neutral-200 bg-white/50 backdrop-blur-sm px-6 pb-24 [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden">
        <FileList
          groupedFiles={groupedFiles}
          onFileHover={handleFileHover}
          onFileSelect={handleFileSelect}
          selectedFileId={selectedFile?.id || null}
        />
      </div>

      {/* File Details */}
      <div className="flex-1 relative">
        <div className={`sticky top-4 ${selectedFile ? "transition-all duration-300 ease-in-out" : ""}`}>
          <FileDetails file={fileToShow} onHoverStart={() => {}} onHoverEnd={() => {}} isSticky={!!selectedFile} />
        </div>
      </div>
    </div>
  )
}








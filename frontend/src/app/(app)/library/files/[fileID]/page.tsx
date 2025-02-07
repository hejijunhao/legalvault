// src/app/(app)/library/files/[fileID]/page.tsx

"use client"

import Link from "next/link"
import Image from "next/image"
import { ChevronLeft } from "lucide-react"
import { cn } from "@/lib/utils"
import { VersionsPanel } from "@/components/library/file-viewer/versions-panel"
import { InformationPanel } from "@/components/library/file-viewer/information-panel"
import { ModePanel } from "@/components/library/file-viewer/mode-panel"
import { ActionsPanel } from "@/components/library/file-viewer/actions-panel"

// Custom SVG components for the metadata icons
const DocumentIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="17" viewBox="0 0 16 17" fill="none">
    <path
      d="M3.0502 14.7501C2.3252 14.7501 1.73145 14.1688 1.73145 13.4563V4.18135C1.73145 2.54385 2.9502 1.8001 4.44395 2.53135L7.21895 3.89385C7.81895 4.1876 8.3127 4.96885 8.3127 5.63135V14.7501H3.0502Z"
      stroke="#1C1C1C"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path
      d="M14.2312 12.7751C14.2312 14.1251 13.6062 14.7501 12.2562 14.7501H8.3125V7.51257L8.60625 7.57507L11.4187 8.20632L12.6875 8.48757C13.5125 8.66882 14.1875 9.09382 14.225 10.2938C14.2312 10.3313 14.2312 10.3688 14.2312 10.4126V12.7751Z"
      stroke="#1C1C1C"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path d="M3.9375 6.625H6.10625" stroke="#1C1C1C" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M3.9375 9.125H6.10625" stroke="#1C1C1C" strokeLinecap="round" strokeLinejoin="round" />
    <path
      d="M11.4189 10.2188C11.4189 10.9938 10.7877 11.625 10.0127 11.625C9.2377 11.625 8.60645 10.9938 8.60645 10.2188V7.57501L11.4189 8.20626V10.2188Z"
      stroke="#1C1C1C"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path
      d="M12.8252 11.625C12.0502 11.625 11.4189 10.9938 11.4189 10.2188V8.2063L12.6877 8.48755C13.5127 8.6688 14.1877 9.0938 14.2252 10.2938C14.1877 11.0313 13.5752 11.625 12.8252 11.625Z"
      stroke="#1C1C1C"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path opacity="0.01" fillRule="evenodd" clipRule="evenodd" d="M15.5 1V16H0.5V1H15.5Z" stroke="#1C1C1C" />
  </svg>
)

const CrossIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="15" viewBox="0 0 16 15" fill="none">
    <path
      d="M9.59961 13.0875C8.72461 13.9625 7.28712 13.9625 6.40587 13.0875L2.41211 9.09375C1.53711 8.21875 1.53711 6.78126 2.41211 5.90001L6.40587 1.90625C7.28087 1.03125 8.71836 1.03125 9.59961 1.90625L13.5934 5.90001C14.4684 6.78126 14.4684 8.21875 13.5934 9.09375L9.59961 13.0875Z"
      stroke="#1C1C1C"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path d="M4.40625 3.90625L11.5938 11.0938" stroke="#1C1C1C" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M11.5938 3.90625L4.40625 11.0938" stroke="#1C1C1C" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
)

const FolderIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="15" viewBox="0 0 16 15" fill="none">
    <path
      d="M13.625 10.625C13.625 12.5 12.6875 13.75 10.5 13.75H5.5C3.3125 13.75 2.375 12.5 2.375 10.625V4.375C2.375 2.5 3.3125 1.25 5.5 1.25H10.5C12.6875 1.25 13.625 2.5 13.625 4.375V10.625Z"
      stroke="#1C1C1C"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path
      d="M10.1875 6.16249C10.1875 6.43749 9.86248 6.57499 9.66248 6.39374L8.21252 5.05627C8.09377 4.94377 7.90623 4.94377 7.78748 5.05627L6.33752 6.39374C6.13752 6.57499 5.8125 6.43749 5.8125 6.16249V1.25H10.1875V6.16249Z"
      stroke="#1C1C1C"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path d="M8.78125 8.75H11.4375" stroke="#1C1C1C" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M6.125 11.25H11.4375" stroke="#1C1C1C" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
)

const CubeIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="15" viewBox="0 0 16 15" fill="none">
    <path
      d="M12.6438 3.60621C13.1188 3.86246 13.1188 4.59371 12.6438 4.84996L8.575 7.04371C8.2125 7.23746 7.7875 7.23746 7.425 7.04371L3.35625 4.84996C2.88125 4.59371 2.88125 3.86246 3.35625 3.60621L7.425 1.41246C7.7875 1.21871 8.2125 1.21871 8.575 1.41246L12.6438 3.60621Z"
      stroke="#1C1C1C"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path
      d="M6.5375 8.22505C7.00625 8.46255 7.30625 8.9438 7.30625 9.4688V13.0438C7.30625 13.5625 6.7625 13.8938 6.3 13.6625L2.51875 11.7688C2.05 11.5313 1.75 11.05 1.75 10.525V6.95005C1.75 6.4313 2.29375 6.10005 2.75625 6.3313L6.5375 8.22505Z"
      stroke="#1C1C1C"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path
      d="M9.46211 8.22505C8.99336 8.46255 8.69336 8.9438 8.69336 9.4688V13.0438C8.69336 13.5625 9.23711 13.8938 9.69961 13.6625L13.4809 11.7688C13.9496 11.5313 14.2496 11.05 14.2496 10.525V6.95005C14.2496 6.4313 13.7059 6.10005 13.2434 6.3313L9.46211 8.22505Z"
      stroke="#1C1C1C"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
)

const FileIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="15" viewBox="0 0 16 15" fill="none">
    <path
      d="M13.625 10.625C13.625 12.5 12.6875 13.75 10.5 13.75H5.5C3.3125 13.75 2.375 12.5 2.375 10.625V4.375C2.375 2.5 3.3125 1.25 5.5 1.25H10.5C12.6875 1.25 13.625 2.5 13.625 4.375V10.625Z"
      stroke="#1C1C1C"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path
      d="M9.5625 2.8125V4.0625C9.5625 4.75 10.125 5.3125 10.8125 5.3125H12.0625"
      stroke="#1C1C1C"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path d="M6.75 8.125L5.5 9.375L6.75 10.625" stroke="#1C1C1C" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M9.25 8.125L10.5 9.375L9.25 10.625" stroke="#1C1C1C" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
)

const CalendarIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="15" viewBox="0 0 16 15" fill="none">
    <path d="M5.5 1.25V3.125" stroke="#1C1C1C" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M10.5 1.25V3.125" stroke="#1C1C1C" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M2.6875 5.68121H13.3125" stroke="#1C1C1C" strokeLinecap="round" strokeLinejoin="round" />
    <path
      d="M13.625 10.625C13.625 12.5 12.6875 13.75 10.5 13.75H5.5C3.3125 13.75 2.375 12.5 2.375 10.625V5.3125C2.375 3.4375 3.3125 2.1875 5.5 2.1875H10.5C12.6875 2.1875 13.625 3.4375 13.625 5.3125V10.625Z"
      stroke="#1C1C1C"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path d="M10.3091 8.5625H10.3147" stroke="#1C1C1C" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M10.3091 10.4375H10.3147" stroke="#1C1C1C" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M7.99754 8.5625H8.00316" stroke="#1C1C1C" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M7.99754 10.4375H8.00316" stroke="#1C1C1C" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M5.68407 8.5625H5.68968" stroke="#1C1C1C" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M5.68407 10.4375H5.68968" stroke="#1C1C1C" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
)

// Metadata for the file
const fileMetadata = {
  created: "20 Feb 2024",
  modified: "24 Feb 2024",
  size: "2.4 MB",
  creator: "Sarah Chen",
  collaborators: ["Michael Wong", "David Kim"],
  tags: ["Term Sheet", "M&A", "Draft", "Greenbridge"],
  source: "OneDrive",
}

// File data (same as before)
const fileData = {
  id: "project-greenbridge",
  name: "Project Greenbridge Term Sheet",
  metadata: [
    { id: "client", label: "Greenbridge Corp", icon: DocumentIcon },
    { id: "type", label: "Term Sheets", icon: CrossIcon },
    { id: "workspace", label: "M&A Deals", icon: FolderIcon },
    { id: "format", label: "PDF Document", icon: CubeIcon },
    { id: "source", label: "OneDrive", icon: FileIcon },
    { id: "date", label: "24.02.2024", icon: CalendarIcon },
  ],
}

export default function FileOverviewPage() {
  return (
    <div className="min-h-screen">
      <div className="mx-auto max-w-[1440px] px-4 py-6">
        {/* Header row with back button, title, and metadata */}
        <div className="mb-8 flex items-center justify-between">
          {/* Back Navigation */}
          <Link
            href="/library"
            className="inline-flex items-center text-sm text-[#525766] transition-colors hover:text-[#1c1c1c]"
          >
            <ChevronLeft className="mr-1 h-4 w-4" />
            All Workspaces
          </Link>

          {/* Title and Metadata Container */}
          <div className="flex flex-1 flex-col items-center">
            <h1
              className={cn(
                "text-[32px] font-normal italic leading-normal text-[#1c1c1c]",
                "font-['Libre_Baskerville']",
              )}
            >
              {fileData.name}
            </h1>

            {/* Metadata Tags */}
            <div className="mt-2 flex flex-wrap justify-center gap-2">
              {fileData.metadata.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center gap-[6px] rounded-xl bg-[rgba(137,146,169,0.30)] px-2 py-1"
                >
                  <item.icon />
                  <span className="text-sm text-[#1c1c1c]">{item.label}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Empty div to balance the layout */}
          <div className="w-[100px]"></div>
        </div>

        {/* Main content with panels */}
        <div className="relative mt-8 grid grid-cols-[280px_1fr_280px] gap-6">
          {/* Left panels */}
          <div className="space-y-6">
            <div className="h-[120px]">
              <VersionsPanel />
            </div>
            <div className="h-[calc(100%-136px)]">
              <InformationPanel metadata={fileMetadata} />
            </div>
          </div>

          {/* Center document preview */}
          <div className="flex items-center justify-center px-8">
            <div className="relative aspect-[3/4] w-full max-w-[400px]">
              <Image src="/placeholder.svg" alt="Document Preview" fill className="object-contain" priority />
            </div>
          </div>

          {/* Right panels */}
          <div className="space-y-6">
            <div className="h-[120px]">
              <ModePanel />
            </div>
            <div className="h-[calc(100%-136px)]">
              <ActionsPanel />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}



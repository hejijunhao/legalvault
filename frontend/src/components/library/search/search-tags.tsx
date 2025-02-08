// src/components/library/search/search-tags.tsx

"use client"

import { motion } from "framer-motion"

// Custom SVG components for the metadata icons
const ClientIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none">
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
  </svg>
)

const CollectionIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none">
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

const WorkspaceIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none">
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

const DocumentTypeIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none">
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

const SourceIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none">
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

const DateIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none">
    <path d="M5.5 1.25V3.125" stroke="#1C1C1C" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M10.5 1.25V3.125" stroke="#1C1C1C" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M2.6875 5.68121H13.3125" stroke="#1C1C1C" strokeLinecap="round" strokeLinejoin="round" />
    <path
      d="M13.625 10.625C13.625 12.5 12.6875 13.75 10.5 13.75H5.5C3.3125 13.75 2.375 12.5 2.375 10.625V5.3125C2.375 3.4375 3.3125 2.1875 5.5 2.1875H10.5C12.6875 2.1875 13.625 3.4375 13.625 5.3125V10.625Z"
      stroke="#1C1C1C"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
)

interface Metadata {
  id: string
  label: string
  value: string
}

interface SearchTagsProps {
  metadata: Metadata[]
}

const getIcon = (id: string) => {
  switch (id) {
    case "client":
      return <ClientIcon />
    case "collection":
      return <CollectionIcon />
    case "workspace":
      return <WorkspaceIcon />
    case "type":
      return <DocumentTypeIcon />
    case "source":
      return <SourceIcon />
    case "date":
      return <DateIcon />
    default:
      return null
  }
}

export function SearchTags({ metadata }: SearchTagsProps) {
  return (
    <>
      {metadata.map((item, index) => (
        <motion.div
          key={item.id}
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{
            duration: 0.2,
            delay: index * 0.05,
            ease: [0, 0.71, 0.2, 1.01],
          }}
        >
          <div className="flex items-center gap-[6px] rounded-xl bg-[rgba(137,146,169,0.30)] px-2 py-1">
            {getIcon(item.id)}
            <span className="text-sm text-[#1c1c1c]">{item.value}</span>
          </div>
        </motion.div>
      ))}
    </>
  )
}


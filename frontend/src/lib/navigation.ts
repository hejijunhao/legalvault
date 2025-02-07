// src/lib/navigation.ts

// Map of routes to their display names
export const routeDisplayNames: Record<string, string> = {
  library: "Library",
  collections: "Collections",
  documents: "Documents",
  workspace: "Workspace",
  files: "Files",
  search: "Search Results",
}

// Function to get display name from path
export function getDisplayNameFromPath(path: string): string {
  // Remove leading slash and get the first segment
  const segment = path.split("/")[1]
  return routeDisplayNames[segment] || "Previous Page"
}

// Function to format the back link text
export function formatBackLinkText(displayName: string): string {
  return `Back to ${displayName}`
}


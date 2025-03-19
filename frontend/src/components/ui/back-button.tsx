// src/components/ui/back-button.tsx

"use client"

import { useRouter } from "next/navigation"
import { ChevronLeft } from "lucide-react"
import { useEffect, useState } from "react"
import { getDisplayNameFromPath, formatBackLinkText } from "@/lib/navigation"

interface BackButtonProps {
  customText?: string;
  className?: string;
  onClick?: () => void;
  "aria-label"?: string;
}

export function BackButton({ customText, className, onClick, "aria-label": ariaLabel }: BackButtonProps) {
  const router = useRouter()
  const [backText, setBackText] = useState("Back")

  useEffect(() => {
    if (!customText) {
      // Try to determine the back text dynamically
      try {
        // Get the previous path from sessionStorage if available
        const previousPaths = JSON.parse(sessionStorage.getItem('navigationHistory') || '[]');
        const previousPath = previousPaths.length > 1 ? previousPaths[previousPaths.length - 2] : '';
        
        if (previousPath) {
          const displayName = getDisplayNameFromPath(previousPath);
          setBackText(formatBackLinkText(displayName));
        } else {
          setBackText("Back");
        }
      } catch (error) {
        console.error("Error setting back text:", error);
        setBackText("Back");
      }
    } else {
      setBackText(customText);
    }
    
    // Store current path in navigation history
    try {
      const currentPath = window.location.pathname;
      const previousPaths = JSON.parse(sessionStorage.getItem('navigationHistory') || '[]');
      
      // Only add if it's different from the last entry
      if (previousPaths.length === 0 || previousPaths[previousPaths.length - 1] !== currentPath) {
        previousPaths.push(currentPath);
        // Keep only the last 10 paths to avoid excessive storage
        if (previousPaths.length > 10) {
          previousPaths.shift();
        }
        sessionStorage.setItem('navigationHistory', JSON.stringify(previousPaths));
      }
    } catch (error) {
      console.error("Error updating navigation history:", error);
    }
  }, [customText]);

  const handleBack = () => {
    // If custom onClick is provided, use that instead
    if (onClick) {
      onClick();
      return;
    }
    
    // Use browser history if available
    if (window.history.length > 1) {
      router.back();
    } else {
      // Fallback to navigation history in sessionStorage
      try {
        const previousPaths = JSON.parse(sessionStorage.getItem('navigationHistory') || '[]');
        if (previousPaths.length > 1) {
          const previousPath = previousPaths[previousPaths.length - 2];
          router.push(previousPath);
          
          // Update navigation history
          previousPaths.pop();
          sessionStorage.setItem('navigationHistory', JSON.stringify(previousPaths));
        } else {
          // Default fallback
          router.push("/");
        }
      } catch (error) {
        console.error("Error navigating back:", error);
        router.push("/");
      }
    }
  }

  return (
    <button
      onClick={handleBack}
      className={`inline-flex items-center text-sm text-[#525766] transition-colors hover:text-[#1c1c1c] ${className || ''}`}
      aria-label={ariaLabel || `Go back to ${backText}`}
    >
      <ChevronLeft className="mr-1 h-4 w-4" />
      {backText}
    </button>
  )
}

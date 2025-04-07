// src/components/research/research-prompt-suggestions.tsx

import { useState } from "react"
import { motion } from "framer-motion"

interface PromptSuggestion {
  category: string
  text: string
}

interface ResearchPromptSuggestionsProps {
  onSelectPrompt: (prompt: string) => void
}

export function ResearchPromptSuggestions({ onSelectPrompt }: ResearchPromptSuggestionsProps) {
  // Randomly select 3 suggestions to display
  const [displayedSuggestions] = useState(() => {
    const allSuggestions: PromptSuggestion[] = [
      // Case Law Analysis
      { category: "Case Law", text: "Analyze recent Supreme Court decisions on privacy rights" },
      { category: "Case Law", text: "Find precedents for contract disputes in technology licensing" },
      { category: "Case Law", text: "Summarize key cases on employment discrimination in the last 5 years" },
      
      // Regulatory Compliance
      { category: "Regulatory", text: "Explain GDPR requirements for small businesses" },
      { category: "Regulatory", text: "Summarize recent changes to SEC disclosure requirements" },
      { category: "Regulatory", text: "What are the key environmental regulations affecting manufacturing?" },
      
      // Corporate Law
      { category: "Corporate", text: "Explain director fiduciary duties in Delaware corporations" },
      { category: "Corporate", text: "What are the legal requirements for a valid shareholders' agreement?" },
      { category: "Corporate", text: "Compare LLC and C-Corp structures for a tech startup" },
      
      // Client Advice
      { category: "Client Advice", text: "Draft a client memo on trademark protection strategies" },
      { category: "Client Advice", text: "Explain force majeure clauses in simple terms" },
      { category: "Client Advice", text: "What should I tell clients about recent changes to tax law?" },
    ]
    
    // Shuffle and pick 3 random suggestions
    return [...allSuggestions]
      .sort(() => 0.5 - Math.random())
      .slice(0, 3)
  })

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6 }}
      className="mt-4 w-full"
    >
      <div className="text-xs text-gray-500 mb-2 ml-1">Try asking about:</div>
      
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        {displayedSuggestions.map((suggestion, index) => (
          <div
            key={index}
            onClick={() => onSelectPrompt(suggestion.text)}
            className="cursor-pointer rounded-lg border border-gray-200/50 bg-white/70 backdrop-blur-[2px] p-3 transition-all hover:border-gray-300/70 hover:shadow-md hover:bg-white/80"
          >
            <div className="mb-1.5">
              <span className="text-xs font-medium text-gray-500">
                {suggestion.category}
              </span>
            </div>
            <p className="text-sm text-gray-700">{suggestion.text}</p>
          </div>
        ))}
      </div>
    </motion.div>
  )
}
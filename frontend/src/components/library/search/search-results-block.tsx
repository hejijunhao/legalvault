// src/components/library/search/search-results-block.tsx

"use client"

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"

interface SearchResultsBlockProps {
  content: {
    introduction: string
    sections: {
      title: string
      content: string | string[]
    }[]
  }
}

export function SearchResultsBlock({ content }: SearchResultsBlockProps) {
  return (
    <Card className="h-full">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium text-[#1C1C1C]">Summary</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm text-[#1C1C1C]">{content.introduction}</p>

        {content.sections.map((section, index) => (
          <div key={index} className="space-y-2">
            <h3 className="text-sm font-medium text-[#1C1C1C]">{section.title}</h3>
            {Array.isArray(section.content) ? (
              <ul className="space-y-1">
                {section.content.map((item, itemIndex) => (
                  <li key={itemIndex} className="flex text-sm text-[#1C1C1C]">
                    <span className="mr-2">•</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-[#1C1C1C]">{section.content}</p>
            )}
          </div>
        ))}
      </CardContent>
    </Card>
  )
}


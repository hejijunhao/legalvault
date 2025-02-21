// src/components/research/legal-news-feed.tsx

"use client"

import { motion } from "framer-motion"
import { Bookmark, Scale, Gavel, Globe, BookOpen, Building2 } from "lucide-react"
import { useState } from "react"

const categories = [
  { id: "all", label: "All Updates", icon: Scale },
  { id: "cases", label: "Case Law", icon: Gavel },
  { id: "international", label: "International", icon: Globe },
  { id: "legislation", label: "Legislation", icon: BookOpen },
  { id: "corporate", label: "Corporate", icon: Building2 },
]

const newsItems = [
  {
    id: 1,
    category: "cases",
    title: "Supreme Court Rules on Digital Privacy Rights",
    description:
      "Landmark decision establishes new precedent for data protection and privacy in the digital age, affecting how businesses must handle personal information.",
    image: "/placeholder.svg?height=400&width=800",
    author: "Sarah Chen",
    date: "21 Feb 2024",
    featured: true,
  },
  {
    id: 2,
    category: "legislation",
    title: "New Companies Act Amendments",
    description: "Major updates to corporate governance requirements coming into effect March 2024.",
    image: "/placeholder.svg?height=200&width=300",
    author: "Michael Wong",
    date: "20 Feb 2024",
  },
  {
    id: 3,
    category: "international",
    title: "EU-Singapore Digital Partnership",
    description: "Framework agreement signed for cross-border data flows and digital trade.",
    image: "/placeholder.svg?height=200&width=300",
    author: "Lisa Mueller",
    date: "19 Feb 2024",
  },
  {
    id: 4,
    category: "corporate",
    title: "Corporate Liability Framework Review",
    description: "Ministry of Law announces comprehensive review of corporate liability framework.",
    image: "/placeholder.svg?height=200&width=300",
    author: "David Tan",
    date: "19 Feb 2024",
  },
]

export function LegalNewsFeed() {
  const [activeCategory, setActiveCategory] = useState("all")
  const filteredNews =
    activeCategory === "all" ? newsItems : newsItems.filter((item) => item.category === activeCategory)
  const featuredArticle = filteredNews.find((item) => item.featured)
  const regularArticles = filteredNews.filter((item) => !item.featured)

  return (
    <div className="w-full space-y-6">
      {/* Categories */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="flex space-x-2 overflow-x-auto pb-2"
      >
        {categories.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveCategory(id)}
            className={`flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              activeCategory === id
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-muted-foreground hover:bg-muted/80"
            }`}
          >
            <Icon className="h-4 w-4" />
            {label}
          </button>
        ))}
      </motion.div>

      {/* Featured Article */}
      {featuredArticle && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="group relative overflow-hidden rounded-xl bg-card"
        >
          <div className="aspect-[2/1] overflow-hidden">
            <img
              src={featuredArticle.image || "/placeholder.svg"}
              alt={featuredArticle.title}
              className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
            />
          </div>
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
          <div className="absolute bottom-0 p-6 text-white">
            <h2 className="mb-2 text-2xl font-semibold">{featuredArticle.title}</h2>
            <p className="mb-4 text-sm text-gray-200">{featuredArticle.description}</p>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="h-8 w-8 rounded-full bg-gray-300" />
                <div>
                  <p className="text-sm font-medium">{featuredArticle.author}</p>
                  <p className="text-xs text-gray-300">{featuredArticle.date}</p>
                </div>
              </div>
              <button className="rounded-full p-2 text-white/80 hover:bg-white/10 hover:text-white">
                <Bookmark className="h-5 w-5" />
              </button>
            </div>
          </div>
        </motion.div>
      )}

      {/* Regular Articles Grid */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3"
      >
        {regularArticles.map((article, index) => (
          <motion.div
            key={article.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 + index * 0.1 }}
            className="group overflow-hidden rounded-lg border bg-card"
          >
            <div className="aspect-[3/2] overflow-hidden">
              <img
                src={article.image || "/placeholder.svg"}
                alt={article.title}
                className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
              />
            </div>
            <div className="p-4">
              <h3 className="mb-2 text-lg font-semibold">{article.title}</h3>
              <p className="mb-4 text-sm text-muted-foreground">{article.description}</p>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="h-6 w-6 rounded-full bg-gray-200" />
                  <div>
                    <p className="text-sm font-medium">{article.author}</p>
                    <p className="text-xs text-muted-foreground">{article.date}</p>
                  </div>
                </div>
                <button className="rounded-full p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground">
                  <Bookmark className="h-4 w-4" />
                </button>
              </div>
            </div>
          </motion.div>
        ))}
      </motion.div>
    </div>
  )
}


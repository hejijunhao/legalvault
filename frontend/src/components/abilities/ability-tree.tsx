// src/components/abilities/ability-tree.tsx

"use client"

import { useRef, useEffect } from "react"
import { AbilityNode } from "./ability-node"

interface Position {
  x: number
  y: number
}

interface Node {
  id: string
  name: string
  description: string
  level: number
  position: Position
  children: string[]
  unlocked: boolean
}

interface Tree {
  name: string
  gradient: string
  nodes: Node[]
}

interface AbilityTreeProps {
  tree: Tree
}

export function AbilityTree({ tree }: AbilityTreeProps) {
  const svgRef = useRef<SVGSVGElement>(null)

  useEffect(() => {
    // Draw connection lines
    const drawConnections = () => {
      const svg = svgRef.current
      if (!svg) return

      // Clear existing paths
      while (svg.firstChild) {
        svg.removeChild(svg.firstChild)
      }

      // Create paths between connected nodes
      tree.nodes.forEach((node) => {
        node.children.forEach((childId) => {
          const childNode = tree.nodes.find((n) => n.id === childId)
          if (!childNode) return

          // Calculate start and end positions
          const startX = (node.position.x + 1) * 300 + 150
          const startY = node.position.y * 200 + 100
          const endX = (childNode.position.x + 1) * 300 + 150
          const endY = childNode.position.y * 200 + 100

          // Create path
          const path = document.createElementNS("http://www.w3.org/2000/svg", "path")
          path.setAttribute("d", `M ${startX} ${startY} L ${endX} ${endY}`)
          path.setAttribute("stroke", "#8992A9")
          path.setAttribute("stroke-width", "2")
          path.setAttribute("fill", "none")

          // Add glow effect
          const glow = document.createElementNS("http://www.w3.org/2000/svg", "filter")
          glow.setAttribute("id", `glow-${node.id}-${childId}`)
          glow.innerHTML = `
            <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          `
          svg.appendChild(glow)
          path.setAttribute("filter", `url(#glow-${node.id}-${childId})`)

          svg.appendChild(path)
        })
      })
    }

    drawConnections()
    window.addEventListener("resize", drawConnections)
    return () => window.removeEventListener("resize", drawConnections)
  }, [tree])

  return (
    <div className="relative min-h-[800px] w-full overflow-x-auto">
      {/* Connection lines */}
      <svg ref={svgRef} className="absolute inset-0 h-full w-full" style={{ minWidth: "1200px" }} />

      {/* Ability nodes */}
      <div className="relative" style={{ minWidth: "1200px" }}>
        {tree.nodes.map((node) => (
          <div
            key={node.id}
            className="absolute"
            style={{
              left: `${(node.position.x + 1) * 300}px`,
              top: `${node.position.y * 200}px`,
            }}
          >
            <AbilityNode
              name={node.name}
              description={node.description}
              unlocked={node.unlocked}
              gradient={tree.gradient}
            />
          </div>
        ))}
      </div>
    </div>
  )
}


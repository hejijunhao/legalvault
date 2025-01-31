// src/components/abilities/ability-tree-flow.tsx

"use client"

import { useMemo } from "react"
import ReactFlow, { type Node, type Edge, ConnectionMode } from "reactflow"
import "reactflow/dist/style.css"
import { CustomNode } from "./custom-node"
import type { AbilityTree, AbilityNode } from "@/lib/ability-data"

const NODE_WIDTH = 300
const LEVEL_HEIGHT = 250
const HORIZONTAL_SPACING = 400

interface AbilityTreeFlowProps {
  tree: AbilityTree
}

const nodeTypes = {
  custom: CustomNode,
}

export function AbilityTreeFlow({ tree }: AbilityTreeFlowProps) {
  const { nodes, edges } = useMemo(() => {
    const nodes: Node[] = []
    const edges: Edge[] = []
    const levelNodes: { [key: number]: AbilityNode[] } = {}

    // Group nodes by level
    tree.nodes.forEach((node) => {
      if (!levelNodes[node.level]) {
        levelNodes[node.level] = []
      }
      levelNodes[node.level].push(node)
    })

    // Calculate positions for each node
    Object.entries(levelNodes).forEach(([level, nodesInLevel]) => {
      const levelNum = Number.parseInt(level)
      const totalWidth =
        nodesInLevel.length * NODE_WIDTH + (nodesInLevel.length - 1) * (HORIZONTAL_SPACING - NODE_WIDTH)
      const startX = -totalWidth / 2

      nodesInLevel.forEach((node, index) => {
        const xPosition = startX + index * HORIZONTAL_SPACING
        const yPosition = (levelNum - 1) * LEVEL_HEIGHT

        nodes.push({
          id: node.id,
          type: "custom",
          position: { x: xPosition, y: yPosition },
          data: {
            name: node.name,
            description: node.description,
            status: node.status,
            gradient: tree.gradient,
          },
          draggable: false, // Prevent node dragging
        })

        // Create edges from prerequisites
        node.prerequisites.forEach((prereqId) => {
          edges.push({
            id: `${prereqId}-${node.id}`,
            source: prereqId,
            target: node.id,
            type: "smoothstep",
            animated: node.status === "active",
            style: { stroke: "#000000", strokeWidth: 1, strokeDasharray: "5 5" },
          })
        })
      })
    })

    return { nodes, edges }
  }, [tree])

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      nodeTypes={nodeTypes}
      connectionMode={ConnectionMode.Strict}
      fitView
      fitViewOptions={{ padding: 0.2 }}
      minZoom={1}
      maxZoom={1}
      className="bg-transparent"
      proOptions={{ hideAttribution: true }}
      nodesDraggable={false} // Prevent node dragging
      nodesConnectable={false} // Prevent new connections
      elementsSelectable={false} // Prevent selection
      panOnScroll={false} // Prevent panning
      zoomOnScroll={false} // Prevent zooming
      panOnDrag={false} // Prevent panning
      selectNodesOnDrag={false} // Prevent selection
      preventScrolling={true} // Prevent scrolling
    ></ReactFlow>
  )
}



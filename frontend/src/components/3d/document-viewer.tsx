// src/components/3d/document-viewer.tsx

"use client"

import { Canvas } from "@react-three/fiber"

function Box() {
  return (
    <mesh>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color="white" />
    </mesh>
  )
}

export function DocumentViewer() {
  return (
    <div className="h-96 w-full">
      <Canvas>
        <ambientLight intensity={0.5} />
        <Box />
      </Canvas>
    </div>
  )
}

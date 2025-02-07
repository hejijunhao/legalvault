// src/types/three-jsx.d.ts

import { Euler, Vector3 } from 'three'
import { MeshStandardMaterial, BoxGeometry, PlaneGeometry } from 'three'
import { ReactThreeFiber } from '@react-three/fiber'

declare module '@react-three/fiber' {
  interface ThreeElements {
    group: ReactThreeFiber.Object3DNode<THREE.Group, typeof THREE.Group>
    mesh: ReactThreeFiber.Object3DNode<THREE.Mesh, typeof THREE.Mesh>
    boxGeometry: ReactThreeFiber.BufferGeometryNode<BoxGeometry, typeof BoxGeometry>
    planeGeometry: ReactThreeFiber.BufferGeometryNode<PlaneGeometry, typeof PlaneGeometry>
    meshStandardMaterial: ReactThreeFiber.MaterialNode<MeshStandardMaterial, typeof MeshStandardMaterial>
    pointLight: ReactThreeFiber.LightNode<THREE.PointLight, typeof THREE.PointLight>
    ambientLight: ReactThreeFiber.LightNode<THREE.AmbientLight, typeof THREE.AmbientLight>
  }
}
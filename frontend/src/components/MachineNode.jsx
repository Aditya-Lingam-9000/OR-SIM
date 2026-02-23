/**
 * MachineNode.jsx
 * A single machine in the 3D OR scene.
 *
 * Appearance:
 *   OFF → dark box, dim self-illumination, small
 *   ON  → bright glowing box, white point-light, pulsing scale, green ring
 *
 * Uses @react-three/drei Html for the label (always faces camera).
 */
import React, { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import { Html } from '@react-three/drei'
import * as THREE from 'three'

// OFF / ON visual params
const OFF_EMISSIVE   = new THREE.Color(0x050810)
const OFF_ROUGHNESS  = 0.9
const OFF_METALNESS  = 0.1

export default function MachineNode({ name, position, baseColor, icon, isOn }) {
  const meshRef  = useRef()
  const phase    = useRef(Math.random() * Math.PI * 2)   // random phase for pulse

  const onColor  = new THREE.Color(baseColor)
  const offColor = new THREE.Color(0x1a2234)

  useFrame((_, delta) => {
    if (!meshRef.current) return
    phase.current += delta * 2.2

    if (isOn) {
      // Soft pulse: scale between 1.0 and 1.06
      const pulse = 1.0 + 0.03 * Math.sin(phase.current)
      meshRef.current.scale.setScalar(pulse)
      meshRef.current.material.emissiveIntensity =
        0.35 + 0.15 * Math.sin(phase.current)
    } else {
      meshRef.current.scale.setScalar(1.0)
      meshRef.current.material.emissiveIntensity = 0.04
    }
  })

  const [x, z] = position
  const y       = 0.45   // sits on floor (box height = 0.9)

  return (
    <group position={[x, y, z]}>
      {/* Machine body */}
      <mesh ref={meshRef} castShadow receiveShadow>
        <boxGeometry args={[1.1, 0.9, 0.7]} />
        <meshStandardMaterial
          color           = {isOn ? onColor  : offColor}
          emissive        = {isOn ? onColor  : OFF_EMISSIVE}
          emissiveIntensity = {isOn ? 0.35 : 0.04}
          roughness       = {isOn ? 0.35 : OFF_ROUGHNESS}
          metalness       = {isOn ? 0.6  : OFF_METALNESS}
        />
      </mesh>

      {/* Point light when ON */}
      {isOn && (
        <pointLight
          color     = {baseColor}
          intensity = {1.8}
          distance  = {3.5}
          decay     = {2}
          position  = {[0, 0.8, 0]}
        />
      )}

      {/* Green ON / gray OFF status ring on top */}
      <mesh position={[0, 0.46, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[0.32, 0.40, 32]} />
        <meshBasicMaterial
          color       = {isOn ? '#00ff88' : '#2a3a4a'}
          transparent = {true}
          opacity     = {isOn ? 0.9 : 0.4}
          side        = {THREE.DoubleSide}
        />
      </mesh>

      {/* HTML label — always faces camera */}
      <Html
        position    = {[0, 1.05, 0]}
        center
        distanceFactor = {14}
        style={{
          pointerEvents: 'none',
          userSelect:    'none',
          textAlign:     'center',
          whiteSpace:    'nowrap',
        }}
      >
        <div style={{
          fontSize:    12,
          fontFamily:  'Segoe UI, system-ui, sans-serif',
          fontWeight:  isOn ? 700 : 400,
          color:       isOn ? '#e8f8ff' : '#3a5060',
          padding:     '2px 6px',
          background:  isOn ? 'rgba(0,200,255,0.12)' : 'rgba(0,0,0,0.25)',
          borderRadius: 4,
          border:      `1px solid ${isOn ? 'rgba(0,200,255,0.3)' : 'transparent'}`,
          transition:  'color 0.3s',
        }}>
          {icon} {name}
        </div>
      </Html>
    </group>
  )
}

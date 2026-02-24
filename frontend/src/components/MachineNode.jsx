/**
 * MachineNode.jsx
 * Renders a specific 3D medical equipment model for each machine type.
 * Uses getMachineModel() from MedicalModels3D to select the right model.
 * All models sit with y=0 at floor level.
 */
import React, { useRef } from 'react'
import { useFrame }       from '@react-three/fiber'
import { Html }           from '@react-three/drei'
import { getMachineModel } from './MedicalModels3D'
import { useMachineStore }      from '../store/machineStore'
import { use3DHover }           from '../hooks/use3DHover'
import { MACHINE_DESCRIPTIONS } from '../data/descriptions'
import * as THREE from 'three'

export default function MachineNode({ name, position, baseColor, icon, isOn }) {
  const phase = useRef(Math.random() * Math.PI * 2)
  const lightRef = useRef()
  const isRotating = useMachineStore((s) => s.isRotating)

  const hoverHandlers = use3DHover({
    label:       name,
    subtitle:    isOn ? 'ACTIVE' : 'STANDBY',
    description: MACHINE_DESCRIPTIONS[name] ?? 'Medical equipment used during surgical procedures.',
    accentColor: baseColor,
  })

  useFrame((_, delta) => {
    phase.current += delta * 1.6
    if (lightRef.current && isOn) {
      lightRef.current.intensity = 1.6 + 0.4 * Math.sin(phase.current)
    }
  })

  const [x, z] = position

  return (
    <group position={[x, 0, z]} {...hoverHandlers}>
      {/* 3D machine model — y=0 is floor */}
      {getMachineModel(name, isOn, baseColor)}

      {/* Soft point light when active */}
      {isOn && (
        <pointLight
          ref={lightRef}
          color={baseColor}
          intensity={1.6}
          distance={3.5}
          decay={2.2}
          position={[0, 1.2, 0]}
        />
      )}

      {/* Large, always-visible label rendered in screen space */}
      <Html
        position={[0, 2.1, 0]}
        center
        distanceFactor={10}
        zIndexRange={[19, 1]}
        style={{ pointerEvents: 'none', userSelect: 'none' }}
      >
        <div style={{
          fontFamily:  'Segoe UI, system-ui, sans-serif',
          fontSize:    isRotating ? 10.5 : 13,
          fontWeight:  isOn ? 700 : 500,
          color:       isOn ? '#ffffff' : '#607080',
          background:  isOn ? `rgba(0,0,0,0.82)` : 'rgba(0,0,0,0.55)',
          border:      `1.5px solid ${isRotating ? 'rgba(0,200,255,0.25)' : (isOn ? baseColor : 'rgba(80,100,120,0.4)')}`,
          borderRadius: 6,
          padding:     isRotating ? '2px 7px' : '4px 10px',
          boxShadow:   isOn && !isRotating ? `0 0 12px ${baseColor}55` : 'none',
          whiteSpace:  'nowrap',
          textShadow:  isOn && !isRotating ? `0 0 8px ${baseColor}` : 'none',
          opacity:     isRotating ? 0.28 : 1,
          transform:   isRotating ? 'scale(0.82)' : 'scale(1)',
          filter:      isRotating ? 'blur(0.6px)' : 'none',
          transition:  isRotating
            ? 'all 0.18s cubic-bezier(0.4,0,0.2,1)'
            : 'all 0.45s cubic-bezier(0.34,1.56,0.64,1)',
          letterSpacing: isRotating ? 0 : 0.2,
        }}>
          <span style={{ marginRight: 5 }}>{icon}</span>{name}
        </div>
      </Html>

      {/* Status indicator dot at base */}
      <mesh position={[0, 0.02, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[0.22, 0.30, 32]} />
        <meshBasicMaterial
          color={isOn ? '#00ff88' : '#1e2c3c'}
          transparent opacity={isOn ? 0.88 : 0.28}
          side={THREE.DoubleSide}
        />
      </mesh>
    </group>
  )
}

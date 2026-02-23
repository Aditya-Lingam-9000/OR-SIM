/**
 * ORRoom.jsx
 * Three.js 3D operating room rendered via @react-three/fiber.
 *
 * Scene:
 *  - Tiled floor (dark OR tiles)
 *  - Surgical table in centre
 *  - All 12 machines positioned around table (scene-specific data)
 *  - Overhead surgical lights (mesh + SpotLight)
 *  - Ambient + directional fill light
 *  - OrbitControls (mouse drag / scroll to inspect)
 *
 * Machine state comes from useMachineStore — no props needed.
 */
import React, { useMemo } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, Grid } from '@react-three/drei'

import { useMachineStore }      from '../store/machineStore'
import MachineNode              from './MachineNode'
import { HEART_MACHINES }       from '../scenes/HeartTransplantRoom'
import { LIVER_MACHINES }       from '../scenes/LiverResectionRoom'
import { KIDNEY_MACHINES }      from '../scenes/KidneyPCNLRoom'

// Map surgery name fragment → machine layout
const SCENE_MAP = {
  heart:  HEART_MACHINES,
  liver:  LIVER_MACHINES,
  kidney: KIDNEY_MACHINES,
}

function getSurgeryKey(surgeryValue) {
  if (!surgeryValue) return 'heart'
  const v = surgeryValue.toLowerCase()
  if (v.includes('heart'))  return 'heart'
  if (v.includes('liver'))  return 'liver'
  if (v.includes('kidney')) return 'kidney'
  return 'heart'
}

// ── Surgical table ─────────────────────────────────────────────────────────
function SurgicalTable() {
  return (
    <group position={[0, 0, 0]}>
      {/* Table surface */}
      <mesh position={[0, 0.35, 0]} receiveShadow castShadow>
        <boxGeometry args={[1.4, 0.08, 3.2]} />
        <meshStandardMaterial color="#c8d8e0" roughness={0.4} metalness={0.7} />
      </mesh>
      {/* Table leg column */}
      <mesh position={[0, 0.15, 0]} receiveShadow>
        <boxGeometry args={[0.2, 0.3, 0.2]} />
        <meshStandardMaterial color="#7a8898" roughness={0.5} metalness={0.8} />
      </mesh>
      {/* Patient silhouette */}
      <mesh position={[0, 0.49, 0]} receiveShadow>
        <boxGeometry args={[0.55, 0.08, 2.4]} />
        <meshStandardMaterial color="#dde8ee" roughness={0.8} />
      </mesh>
    </group>
  )
}

// ── Overhead surgical light fixture ────────────────────────────────────────
function SurgicalLightFixture({ position, isOn }) {
  return (
    <group position={position}>
      <mesh>
        <cylinderGeometry args={[0.3, 0.4, 0.12, 24]} />
        <meshStandardMaterial
          color="#d0d8e8" roughness={0.3} metalness={0.8}
          emissive={isOn ? '#fffdd0' : '#050810'}
          emissiveIntensity={isOn ? 0.6 : 0.02}
        />
      </mesh>
      {isOn && (
        <spotLight
          color      = "#fff8e0"
          intensity  = {80}
          angle      = {0.55}
          penumbra   = {0.5}
          distance   = {8}
          decay      = {1.5}
          position   = {[0, -0.1, 0]}
          target-position = {[0, -5, 0]}
          castShadow
        />
      )}
    </group>
  )
}

// ── OR floor tiles ──────────────────────────────────────────────────────────
function ORFloor() {
  return (
    <>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]} receiveShadow>
        <planeGeometry args={[14, 14]} />
        <meshStandardMaterial color="#0c1420" roughness={0.95} metalness={0.05} />
      </mesh>
      <Grid
        position      = {[0, 0.01, 0]}
        args          = {[14, 14]}
        cellSize      = {1}
        cellThickness = {0.5}
        cellColor     = "#1a2a3a"
        sectionSize   = {3}
        sectionThickness = {1}
        sectionColor  = "#223344"
        fadeDistance  = {20}
        fadeStrength  = {1}
        infiniteGrid  = {false}
      />
    </>
  )
}

// ── Main scene ──────────────────────────────────────────────────────────────
function ORScene({ machines, machinesOn }) {
  const onSet    = useMemo(() => new Set(machinesOn), [machinesOn])
  const lightsOn = onSet.has('Surgical Lights')

  return (
    <>
      {/* Environment lighting */}
      <ambientLight intensity={0.25} color="#102030" />
      <directionalLight
        position  = {[5, 10, 5]}
        intensity = {0.4}
        color     = "#c0d0e0"
        castShadow
        shadow-mapSize-width  = {1024}
        shadow-mapSize-height = {1024}
      />

      {/* OR floor */}
      <ORFloor />

      {/* Surgical table */}
      <SurgicalTable />

      {/* Overhead lights (two fixtures) */}
      <SurgicalLightFixture position={[0, 3.5,  0.8]} isOn={lightsOn} />
      <SurgicalLightFixture position={[0, 3.5, -0.8]} isOn={lightsOn} />

      {/* All machines */}
      {machines.map((m) => (
        <MachineNode
          key      = {m.name}
          name     = {m.name}
          position = {m.pos}
          baseColor= {m.color}
          icon     = {m.icon}
          isOn     = {onSet.has(m.name)}
        />
      ))}

      {/* Camera controls */}
      <OrbitControls
        enablePan   = {true}
        enableZoom  = {true}
        enableRotate= {true}
        minDistance = {4}
        maxDistance = {20}
        target      = {[0, 0.3, 0]}
      />
    </>
  )
}

// ── Exported ORRoom wrapper ─────────────────────────────────────────────────
export default function ORRoom() {
  const surgery    = useMachineStore((s) => s.surgery)
  const machinesOn = useMachineStore((s) => s.machinesOn)

  const sceneKey = getSurgeryKey(surgery)
  const machines = SCENE_MAP[sceneKey]

  return (
    <Canvas
      style    = {{ width: '100%', height: '100%' }}
      shadows
      gl       = {{ antialias: true }}
      camera   = {{ position: [0, 9, 10], fov: 45, near: 0.1, far: 100 }}
    >
      <ORScene machines={machines} machinesOn={machinesOn} />
    </Canvas>
  )
}

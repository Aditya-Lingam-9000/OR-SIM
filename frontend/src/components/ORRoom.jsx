/**
 * ORRoom.jsx
 * Realistic 3D Operating Room - @react-three/fiber
 *
 * Room structure: tiled floor, painted walls, false ceiling with fluorescent
 * panels, ceiling-mounted surgical light assemblies, detailed surgical bed.
 */
import React, { useMemo, useRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import * as THREE from 'three'

import { useMachineStore }           from '../store/machineStore'
import MachineNode                   from './MachineNode'
import { ORPersonnel }               from './MedicalModels3D'
import { use3DHover }                from '../hooks/use3DHover'
import {
  SURGICAL_LIGHT_DESCRIPTION,
  PATIENT_DESCRIPTION_TEMPLATE,
  PATIENT_FIRST_NAMES, PATIENT_LAST_NAMES,
  pickRandom,
}                                    from '../data/descriptions'
import { HEART_MACHINES }            from '../scenes/HeartTransplantRoom'
import { LIVER_MACHINES }            from '../scenes/LiverResectionRoom'
import { KIDNEY_MACHINES }           from '../scenes/KidneyPCNLRoom'
import { CABG_MACHINES }             from '../scenes/CABGRoom'
import { APPENDECTOMY_MACHINES }     from '../scenes/AppendectomyRoom'
import { CHOLECYSTECTOMY_MACHINES }  from '../scenes/CholecystectomyRoom'
import { HIP_REPLACEMENT_MACHINES }  from '../scenes/HipReplacementRoom'
import { KNEE_REPLACEMENT_MACHINES } from '../scenes/KneeReplacementRoom'
import { CAESAREAN_MACHINES }        from '../scenes/CaesareanSectionRoom'
import { SPINAL_FUSION_MACHINES }    from '../scenes/SpinalFusionRoom'
import { CATARACT_MACHINES }         from '../scenes/CataractSurgeryRoom'
import { HYSTERECTOMY_MACHINES }     from '../scenes/HysterectomyRoom'
import { THYROIDECTOMY_MACHINES }    from '../scenes/ThyroidectomyRoom'
import { COLECTOMY_MACHINES }        from '../scenes/ColectomyRoom'
import { PROSTATECTOMY_MACHINES }    from '../scenes/ProstatectomyRoom'
import { CRANIOTOMY_MACHINES }       from '../scenes/CraniotomyRoom'
import { MASTECTOMY_MACHINES }       from '../scenes/MastectomyRoom'
import { AORTIC_MACHINES }           from '../scenes/AorticAneurysmRepairRoom'
import { GASTRECTOMY_MACHINES }      from '../scenes/GastrectomyRoom'
import { LUNG_LOBECTOMY_MACHINES }   from '../scenes/LungLobectomyRoom'

export const SCENE_MAP = {
  heart:           HEART_MACHINES,
  liver:           LIVER_MACHINES,
  kidney:          KIDNEY_MACHINES,
  cabg:            CABG_MACHINES,
  appendectomy:    APPENDECTOMY_MACHINES,
  cholecystectomy: CHOLECYSTECTOMY_MACHINES,
  hip:             HIP_REPLACEMENT_MACHINES,
  knee:            KNEE_REPLACEMENT_MACHINES,
  caesarean:       CAESAREAN_MACHINES,
  spinal:          SPINAL_FUSION_MACHINES,
  cataract:        CATARACT_MACHINES,
  hysterectomy:    HYSTERECTOMY_MACHINES,
  thyroidectomy:   THYROIDECTOMY_MACHINES,
  colectomy:       COLECTOMY_MACHINES,
  prostatectomy:   PROSTATECTOMY_MACHINES,
  craniotomy:      CRANIOTOMY_MACHINES,
  mastectomy:      MASTECTOMY_MACHINES,
  aortic:          AORTIC_MACHINES,
  gastrectomy:     GASTRECTOMY_MACHINES,
  lobectomy:       LUNG_LOBECTOMY_MACHINES,
}

export function getSurgeryKey(v) {
  if (!v) return 'heart'
  const s = v.toLowerCase()
  if (s.includes('heart'))                         return 'heart'
  if (s.includes('liver'))                         return 'liver'
  if (s.includes('kidney'))                        return 'kidney'
  if (s.includes('bypass') || s.includes('cabg'))  return 'cabg'
  if (s.includes('append'))                        return 'appendectomy'
  if (s.includes('cholecyst'))                     return 'cholecystectomy'
  if (s.includes('hip'))                           return 'hip'
  if (s.includes('knee'))                          return 'knee'
  if (s.includes('caesar') || s.includes('section')) return 'caesarean'
  if (s.includes('spinal'))                        return 'spinal'
  if (s.includes('cataract'))                      return 'cataract'
  if (s.includes('hyster'))                        return 'hysterectomy'
  if (s.includes('thyroid'))                       return 'thyroidectomy'
  if (s.includes('colect'))                        return 'colectomy'
  if (s.includes('prostat'))                       return 'prostatectomy'
  if (s.includes('craniot'))                       return 'craniotomy'
  if (s.includes('mastect'))                       return 'mastectomy'
  if (s.includes('aortic') || s.includes('aneurysm')) return 'aortic'
  if (s.includes('gastrect'))                      return 'gastrectomy'
  if (s.includes('lobect') || s.includes('lung'))  return 'lobectomy'
  return 'heart'
}

// â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
// Texture helper (canvas-based, created once)
// â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function makeTileTex(bg, line, divs, repeatU, repeatV) {
  const px = 512
  const c  = document.createElement('canvas')
  c.width = c.height = px
  const ctx = c.getContext('2d')
  ctx.fillStyle = bg
  ctx.fillRect(0, 0, px, px)
  ctx.strokeStyle = line
  ctx.lineWidth = 1.5
  const step = px / divs
  for (let i = 0; i <= px; i += step) {
    ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, px); ctx.stroke()
    ctx.beginPath(); ctx.moveTo(0, i); ctx.lineTo(px, i); ctx.stroke()
  }
  const tex = new THREE.CanvasTexture(c)
  tex.wrapS = tex.wrapT = THREE.RepeatWrapping
  tex.repeat.set(repeatU, repeatV)
  return tex
}

// â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
// Floor â€” polished clinical vinyl tiles
// â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function ORFloor() {
  const tex = useMemo(() => makeTileTex('#b8c8cc', '#8898a0', 4, 8, 8), [])
  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]} receiveShadow>
      <planeGeometry args={[16, 16]} />
      <meshStandardMaterial map={tex} roughness={0.15} metalness={0.05}
        envMapIntensity={0.3} />
    </mesh>
  )
}

// â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
// Ceiling â€” drop ceiling with tile grid
// â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function ORCeiling() {
  const tex = useMemo(() => makeTileTex('#eef2f5', '#ccd5da', 4, 6, 6), [])
  return (
    <mesh rotation={[Math.PI / 2, 0, 0]} position={[0, 5.0, 0]}>
      <planeGeometry args={[16, 16]} />
      <meshStandardMaterial map={tex} roughness={0.9} metalness={0.0} side={THREE.FrontSide} />
    </mesh>
  )
}

// â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
// Walls â€” painted OR sage-green/off-white with dado rail + baseboard
// â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function ORWall({ pos, rot, w, h }) {
  const tex = useMemo(() => makeTileTex('#ccd8d5', '#b0c0be', 1, w / 2.5, h / 2.5), [w, h])
  return (
    <group position={pos} rotation={rot}>
      <mesh receiveShadow>
        <planeGeometry args={[w, h]} />
        <meshStandardMaterial map={tex} roughness={0.8} metalness={0.02} />
      </mesh>
      {/* Dado rail */}
      <mesh position={[0, -h / 2 + 1.25, 0.015]}>
        <boxGeometry args={[w, 0.055, 0.055]} />
        <meshStandardMaterial color="#90a5a0" roughness={0.4} metalness={0.65} />
      </mesh>
      {/* Baseboard */}
      <mesh position={[0, -h / 2 + 0.08, 0.02]}>
        <boxGeometry args={[w, 0.16, 0.07]} />
        <meshStandardMaterial color="#788890" roughness={0.45} metalness={0.55} />
      </mesh>
    </group>
  )
}

function ORWalls() {
  const rW = 14, rH = 5
  return (
    <>
      <ORWall pos={[0, rH / 2, -rW / 2]} rot={[0, 0, 0]}              w={rW} h={rH} />
      <ORWall pos={[0, rH / 2,  rW / 2]} rot={[0, Math.PI, 0]}        w={rW} h={rH} />
      <ORWall pos={[-rW / 2, rH / 2, 0]} rot={[0,  Math.PI / 2, 0]}   w={rW} h={rH} />
      <ORWall pos={[ rW / 2, rH / 2, 0]} rot={[0, -Math.PI / 2, 0]}   w={rW} h={rH} />
    </>
  )
}

// â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
// Ceiling fluorescent panels
// â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function CeilingFluorescents() {
  const grid = [
    [-3.5, -3.5], [0, -3.5], [3.5, -3.5],
    [-3.5,  0  ], [0,  0  ], [3.5,  0  ],
    [-3.5,  3.5], [0,  3.5], [3.5,  3.5],
  ]
  return (
    <>
      {grid.map(([x, z], i) => (
        <group key={i} position={[x, 4.98, z]}>
          {/* Recessed panel */}
          <mesh rotation={[Math.PI / 2, 0, 0]}>
            <planeGeometry args={[1.55, 0.32]} />
            <meshStandardMaterial
              color="#f4faff"
              emissive="#dceeff"
              emissiveIntensity={1.4}
              roughness={0.9}
            />
          </mesh>
          <mesh rotation={[Math.PI / 2, Math.PI / 2, 0]}>
            <planeGeometry args={[1.55, 0.32]} />
            <meshStandardMaterial
              color="#f4faff"
              emissive="#dceeff"
              emissiveIntensity={1.4}
              roughness={0.9}
            />
          </mesh>
          <pointLight color="#d8eeff" intensity={4} distance={7} decay={2} />
        </group>
      ))}
    </>
  )
}

// â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
// Surgical light head â€” round dish with multi-lens array
// â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function SurgicalLightHead({ offset, isOn }) {
  const panelRef = useRef()
  useFrame(() => {
    if (!panelRef.current) return
    if (!isOn) { panelRef.current.emissiveIntensity = 0; return }
    panelRef.current.emissiveIntensity = 1.55 + 0.22 * Math.sin(Date.now() * 0.0019)
  })

  // Concentric LED ring definitions (Trumpf TruLight / Zeiss Polaris style)
  const ledRings = [
    { r: 0,    w: 0.10  }, // central filled disc
    { r: 0.16, w: 0.055 }, // inner ring
    { r: 0.28, w: 0.055 }, // middle ring
    { r: 0.40, w: 0.050 }, // outer ring
    { r: 0.52, w: 0.040 }, // outermost ring
  ]

  return (
    <group position={offset}>
      {/* Main housing — large flat disc, 70 cm diameter */}
      <mesh castShadow>
        <cylinderGeometry args={[0.70, 0.70, 0.060, 40]} />
        <meshStandardMaterial color="#d8e2ec" roughness={0.10} metalness={0.90} />
      </mesh>
      {/* Raised chrome outer rim */}
      <mesh position={[0, 0.01, 0]}>
        <torusGeometry args={[0.70, 0.020, 10, 40]} />
        <meshStandardMaterial color="#bccbd8" roughness={0.06} metalness={0.96} />
      </mesh>
      {/* Recessed LED face panel — animates with brightness */}
      <mesh ref={panelRef} position={[0, -0.033, 0]}>
        <cylinderGeometry args={[0.65, 0.65, 0.010, 40]} />
        <meshStandardMaterial
          color={isOn ? '#fff9f2' : '#aab8c4'}
          emissive={isOn ? '#fff6e8' : '#000000'}
          emissiveIntensity={0}
          roughness={0.05}
          metalness={0.04}
          transparent
          opacity={0.82}
        />
      </mesh>
      {/* Concentric LED rings on light face */}
      {ledRings.map((ring, i) => (
        <mesh key={i} position={[0, -0.030, 0]} rotation={[Math.PI / 2, 0, 0]}>
          {ring.r === 0
            ? <circleGeometry args={[ring.w, 36]} />
            : <ringGeometry   args={[ring.r, ring.r + ring.w, 40]} />
          }
          <meshStandardMaterial
            color={isOn ? '#fffcf8' : '#d4dfe8'}
            emissive={isOn ? '#fff8e8' : '#000000'}
            emissiveIntensity={isOn ? 3.0 : 0}
            roughness={0.95}
          />
        </mesh>
      ))}
      {/* Sterile back handle */}
      <mesh position={[0, 0.052, -0.20]} castShadow>
        <boxGeometry args={[0.12, 0.042, 0.38]} />
        <meshStandardMaterial color="#c0ccd8" roughness={0.40} metalness={0.72} />
      </mesh>
      {/* Pivot knuckle at arm connection */}
      <mesh position={[0, 0.042, -0.40]} rotation={[Math.PI / 2, 0, 0]}>
        <cylinderGeometry args={[0.058, 0.058, 0.12, 14]} />
        <meshStandardMaterial color="#8898a8" roughness={0.28} metalness={0.90} />
      </mesh>
      {/* Lights when on */}
      {isOn && (
        <>
          {/* Primary surgical spotlight — very bright, surgical-grade */}
          <spotLight
            color="#fff8ec" intensity={280} angle={0.36} penumbra={0.60}
            distance={13} decay={1.0} castShadow
            shadow-mapSize-width={1024} shadow-mapSize-height={1024}
          />
          {/* Six offset fill-lights for shadowless surgical illumination */}
          {[0, 60, 120, 180, 240, 300].map((deg, i) => {
            const a = deg * Math.PI / 180
            return (
              <spotLight key={i}
                color="#fff4e0" intensity={36} angle={0.60} penumbra={0.88}
                distance={9} decay={1.5}
                position={[0.30 * Math.cos(a), 0, 0.30 * Math.sin(a)]}
              />
            )
          })}
          {/* Subtle wide light cone for visual depth */}
          <mesh position={[0, -3.8, 0]} rotation={[Math.PI, 0, 0]}>
            <coneGeometry args={[3.8, 7.6, 36, 1, true]} />
            <meshBasicMaterial color="#fffde8" transparent opacity={0.013}
              side={THREE.DoubleSide} depthWrite={false} />
          </mesh>
        </>
      )}
    </group>
  )
}

// â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
// Surgical light arm assembly (ceiling-mounted)
// â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function SurgicalLightArm({ position, headOffsets, isOn }) {
  const hoverHandlers = use3DHover({
    label:       'Surgical Lights',
    subtitle:    isOn ? 'ACTIVE' : 'STANDBY',
    description: SURGICAL_LIGHT_DESCRIPTION,
    accentColor: '#fff8d0',
  })
  return (
    <group position={position} {...hoverHandlers}>
      {/* Ceiling mounting plate — square forged aluminium profile */}}
      <mesh castShadow>
        <boxGeometry args={[0.28, 0.05, 0.28]} />
        <meshStandardMaterial color="#6a7a88" roughness={0.28} metalness={0.90} />
      </mesh>
      {/* Main pivot dome on ceiling plate */}
      <mesh position={[0, -0.040, 0]}>
        <sphereGeometry args={[0.075, 14, 8, 0, Math.PI * 2, 0, Math.PI * 0.55]} />
        <meshStandardMaterial color="#7888a0" roughness={0.25} metalness={0.90} />
      </mesh>
      {/* Primary vertical drop arm — thick column */}
      <mesh position={[0, -0.66, 0]} castShadow>
        <cylinderGeometry args={[0.050, 0.050, 1.22, 12]} />
        <meshStandardMaterial color="#8898a8" roughness={0.22} metalness={0.88} />
      </mesh>
      {/* Spring balance counterweight housing */}
      <mesh position={[0, -0.38, 0]} castShadow>
        <cylinderGeometry args={[0.080, 0.080, 0.28, 12]} />
        <meshStandardMaterial color="#7a8ea0" roughness={0.28} metalness={0.88} />
      </mesh>
      {/* Elbow joint A */}
      <mesh position={[0, -1.28, 0]} castShadow>
        <sphereGeometry args={[0.072, 14, 10]} />
        <meshStandardMaterial color="#6e8098" roughness={0.24} metalness={0.90} />
      </mesh>
      {/* Horizontal pantograph reach arm */}
      <mesh position={[0, -1.36, 0]} rotation={[0, 0, Math.PI / 2]} castShadow>
        <cylinderGeometry args={[0.036, 0.036, 0.92, 10]} />
        <meshStandardMaterial color="#8898a8" roughness={0.22} metalness={0.88} />
      </mesh>
      {/* Elbow joints at each head connection point */}
      {headOffsets.map((off, i) => (
        <mesh key={i} position={[off[0], off[1] + 0.07, off[2]]} castShadow>
          <sphereGeometry args={[0.062, 12, 8]} />
          <meshStandardMaterial color="#6e8098" roughness={0.24} metalness={0.90} />
        </mesh>
      ))}
      {/* Light heads */}
      {headOffsets.map((off, i) => (
        <SurgicalLightHead key={i} offset={off} isOn={isOn} />
      ))}
    </group>
  )
}

// â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
// Detailed Surgical Table
// â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function SurgicalTable() {
  const surgery      = useMachineStore((s) => s.surgery)
  const patientName  = useMemo(
    () => pickRandom(PATIENT_FIRST_NAMES) + ' ' + pickRandom(PATIENT_LAST_NAMES),
    [],
  )
  const hoverHandlers = use3DHover({
    label:       patientName,
    subtitle:    surgery ?? 'AWAITING SURGERY',
    description: PATIENT_DESCRIPTION_TEMPLATE(
      patientName,
      surgery ?? 'a scheduled procedure',
    ),
    accentColor: '#ffcc80',
  })

  const chestRef   = useRef()
  const abdomenRef = useRef()
  useFrame(() => {
    const breathe = 0.014 * Math.sin(Date.now() * 0.0024)
    if (chestRef.current) {
      chestRef.current.scale.y    = 1 + breathe * 2.8
      chestRef.current.scale.x    = 1 + breathe * 0.55
      chestRef.current.position.y = 0.670 + breathe * 0.44
    }
    if (abdomenRef.current) {
      abdomenRef.current.scale.y    = 1 + breathe * 1.4
      abdomenRef.current.position.y = 0.656 + breathe * 0.22
    }
  })
  return (
    <group {...hoverHandlers}>
      {/* Hydraulic base pedestal */}
      <mesh position={[0, 0.06, 0]} receiveShadow>
        <boxGeometry args={[0.72, 0.12, 0.46]} />
        <meshStandardMaterial color="#606878" roughness={0.4} metalness={0.88} />
      </mesh>
      {/* Center column */}
      <mesh position={[0, 0.3, 0]} castShadow>
        <cylinderGeometry args={[0.115, 0.13, 0.44, 16]} />
        <meshStandardMaterial color="#7a8898" roughness={0.3} metalness={0.88} />
      </mesh>
      {/* Table chassis */}
      <mesh position={[0, 0.56, 0]} castShadow receiveShadow>
        <boxGeometry args={[0.7, 0.065, 3.25]} />
        <meshStandardMaterial color="#8ca0b4" roughness={0.2} metalness={0.82} />
      </mesh>
      {/* Side safety rails */}
      {[-0.385, 0.385].map((x, i) => (
        <mesh key={i} position={[x, 0.635, 0]} castShadow>
          <boxGeometry args={[0.022, 0.038, 3.2]} />
          <meshStandardMaterial color="#aabcc8" roughness={0.15} metalness={0.92} />
        </mesh>
      ))}
      {/* Head rail (top end) */}
      <mesh position={[0, 0.635, 1.615]} castShadow>
        <boxGeometry args={[0.78, 0.038, 0.022]} />
        <meshStandardMaterial color="#aabcc8" roughness={0.15} metalness={0.92} />
      </mesh>
      {/* Foot rail */}
      <mesh position={[0, 0.635, -1.615]} castShadow>
        <boxGeometry args={[0.78, 0.038, 0.022]} />
        <meshStandardMaterial color="#aabcc8" roughness={0.15} metalness={0.92} />
      </mesh>
      {/* Lower surgical drape covering pelvis + legs */}
      <mesh position={[0, 0.598, -0.55]} receiveShadow>
        <boxGeometry args={[0.60, 0.038, 1.90]} />
        <meshStandardMaterial color="#c8dce8" roughness={0.90} metalness={0.0} />
      </mesh>
      {/* Upper sterile drape over chest incision area */}
      <mesh position={[0, 0.598, 0.52]} receiveShadow>
        <boxGeometry args={[0.62, 0.038, 1.18]} />
        <meshStandardMaterial color="#d8eaf4" roughness={0.90} metalness={0.0} />
      </mesh>
      {/* Patient â€” torso */}
      {/* Shoulders */}
      <mesh position={[0, 0.672, 0.94]} castShadow>
        <boxGeometry args={[0.50, 0.12, 0.22]} />
        <meshStandardMaterial color="#c8a888" roughness={0.88} metalness={0.0} />
      </mesh>
      {/* Chest with breathing ref */}
      <mesh ref={chestRef} position={[0, 0.670, 0.50]} castShadow>
        <boxGeometry args={[0.44, 0.13, 0.72]} />
        <meshStandardMaterial color="#c4a480" roughness={0.88} metalness={0.0} />
      </mesh>
      {/* EKG electrode dots */}
      {[[-0.18,0.740,0.70],[0.18,0.740,0.70],[0,0.742,0.52],[-0.10,0.738,0.38],[0.10,0.738,0.38]].map((p,i) => (
        <mesh key={i} position={p}>
          <sphereGeometry args={[0.013,6,4]} />
          <meshStandardMaterial color="#c8d828" emissive="#aacc00" emissiveIntensity={1.0} roughness={0.4} />
        </mesh>
      ))}
      {/* Abdomen with breathing ref */}
      <mesh ref={abdomenRef} position={[0, 0.656, 0.02]} castShadow>
        <boxGeometry args={[0.40, 0.11, 0.72]} />
        <meshStandardMaterial color="#dae4f0" roughness={0.90} metalness={0.0} />
      </mesh>
      {/* Patient arms, skin tone, resting at sides */}
      <mesh position={[0.32, 0.645, 0.32]} castShadow>
        <boxGeometry args={[0.10, 0.095, 0.78]} />
        <meshStandardMaterial color="#c8a888" roughness={0.88} metalness={0.0} />
      </mesh>
      <mesh position={[-0.32, 0.645, 0.32]} castShadow>
        <boxGeometry args={[0.10, 0.095, 0.78]} />
        <meshStandardMaterial color="#c8a888" roughness={0.88} metalness={0.0} />
      </mesh>
      {/* Patient â€” head */}
      {/* Neck */}
      <mesh position={[0, 0.720, 1.14]} castShadow>
        <cylinderGeometry args={[0.055, 0.070, 0.13, 12]} />
        <meshStandardMaterial color="#c8a888" roughness={0.88} metalness={0.0} />
      </mesh>
      {/* Head, realistic skin tone */}
      <mesh position={[0, 0.740, 1.26]} castShadow>
        <sphereGeometry args={[0.165, 20, 14]} />
        <meshStandardMaterial color="#c8a888" roughness={0.85} metalness={0.0} />
      </mesh>
      {/* Ears */}
      <mesh position={[ 0.168, 0.740, 1.26]}>
        <sphereGeometry args={[0.043, 8, 6]} />
        <meshStandardMaterial color="#ba9878" roughness={0.88} metalness={0.0} />
      </mesh>
      <mesh position={[-0.168, 0.740, 1.26]}>
        <sphereGeometry args={[0.043, 8, 6]} />
        <meshStandardMaterial color="#ba9878" roughness={0.88} metalness={0.0} />
      </mesh>
      {/* Closed eyes */}
      <mesh position={[ 0.055, 0.758, 1.415]} rotation={[0, -0.18, 0]}>
        <boxGeometry args={[0.053, 0.011, 0.009]} />
        <meshStandardMaterial color="#3a2e24" roughness={0.8} />
      </mesh>
      <mesh position={[-0.055, 0.758, 1.415]} rotation={[0, 0.18, 0]}>
        <boxGeometry args={[0.053, 0.011, 0.009]} />
        <meshStandardMaterial color="#3a2e24" roughness={0.8} />
      </mesh>
      {/* Anaesthesia mask */}
      <mesh position={[0, 0.740, 1.32]} castShadow>
        <sphereGeometry args={[0.175, 14, 10, 0, Math.PI * 2, 0, Math.PI * 0.55]} />
        <meshStandardMaterial color="#88aacc" roughness={0.60} metalness={0.2} transparent opacity={0.55} />
      </mesh>
      {/* Mask elastic strap */}
      <mesh position={[0, 0.740, 1.26]} rotation={[0, 0, Math.PI / 2]}>
        <cylinderGeometry args={[0.006, 0.006, 0.38, 6]} />
        <meshStandardMaterial color="#5580a4" roughness={0.80} />
      </mesh>
      {/* Patient â€” legs */}
      {/* Legs under surgical drape */}
      <mesh position={[0, 0.654, -0.86]} castShadow>
        <boxGeometry args={[0.36, 0.11, 1.24]} />
        <meshStandardMaterial color="#dae4f0" roughness={0.92} metalness={0.0} />
      </mesh>
      {/* IV pole */}
      <mesh position={[0.52, 1.55, 1.15]} castShadow>
        <cylinderGeometry args={[0.018, 0.018, 2.1, 8]} />
        <meshStandardMaterial color="#c0cad4" roughness={0.28} metalness={0.9} />
      </mesh>
      {/* IV bag hook (T-bar) */}
      <mesh position={[0.52, 2.62, 1.15]} rotation={[0, 0, Math.PI / 2]}>
        <cylinderGeometry args={[0.012, 0.012, 0.3, 8]} />
        <meshStandardMaterial color="#c0cad4" roughness={0.28} metalness={0.9} />
      </mesh>
      {/* IV bag translucent */}
      <mesh position={[0.52, 2.50, 1.15]}>
        <boxGeometry args={[0.12, 0.20, 0.06]} />
        <meshStandardMaterial color="#d8f0f8" roughness={0.20} metalness={0.0} transparent opacity={0.70} />
      </mesh>
    </group>
  )
}

// â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
// Main OR Scene
// â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function ORScene({ machines, machinesOn }) {
  const onSet        = useMemo(() => new Set(machinesOn), [machinesOn])
  const lightsOn     = onSet.has('Surgical Lights')
  const setIsRotating = useMachineStore((s) => s.setIsRotating)

  return (
    <>
      {/* Global ambient â€” the room is lit by ceiling fluorescents */}
      <ambientLight intensity={0.55} color="#c8dce8" />
      {/* Soft fill from above */}
      <directionalLight
        position={[0, 8, 2]} intensity={0.25} color="#d0e8f8"
        castShadow shadow-mapSize-width={2048} shadow-mapSize-height={2048}
        shadow-camera-left={-10} shadow-camera-right={10}
        shadow-camera-top={10} shadow-camera-bottom={-10}
      />

      {/* Room geometry */}
      <ORFloor />
      <ORCeiling />
      <ORWalls />

      {/* Ceiling fluorescent lighting panels */}
      <CeilingFluorescents />

      {/* Surgical table with patient */}
      <SurgicalTable />

      {/* Surgical light arms (two assemblies offset for dual coverage) */}
      <SurgicalLightArm
        position={[-0.45, 5.0,  0.55]}
        headOffsets={[[0, -1.55, 0], [0.65, -1.55, 0]]}
        isOn={lightsOn}
      />
      <SurgicalLightArm
        position={[ 0.45, 5.0, -0.55]}
        headOffsets={[[0, -1.55, 0], [-0.65, -1.55, 0]]}
        isOn={lightsOn}
      />

      {/* OR surgical team */}
      <ORPersonnel />

      {/* Machine nodes — skip Surgical Lights (rendered as ceiling fixtures) */}
      {machines.filter(m => m.name !== 'Surgical Lights').map((m) => (
        <MachineNode
          key={m.name} name={m.name}
          position={m.pos} baseColor={m.color} icon={m.icon}
          isOn={onSet.has(m.name)}
        />
      ))}

      {/* Camera controls */}
      <OrbitControls
        enablePan={true} enableZoom={true} enableRotate={true}
        minDistance={4} maxDistance={18}
        target={[0, 0.5, 0]}
        minPolarAngle={0.05} maxPolarAngle={Math.PI * 0.46}
        zoomSpeed={0.8} rotateSpeed={0.6} panSpeed={0.7}
        onStart={() => setIsRotating(true)}
        onEnd={() => setIsRotating(false)}
      />
    </>
  )
}

// â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
// Exported wrapper
// â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
export default function ORRoom() {
  const surgery    = useMachineStore((s) => s.surgery)
  const machinesOn = useMachineStore((s) => s.machinesOn)

  const sceneKey = getSurgeryKey(surgery)
  const machines = SCENE_MAP[sceneKey]

  return (
    <Canvas
      style={{ width: '100%', height: '100%' }}
      shadows
      gl={{ antialias: true, toneMapping: THREE.ACESFilmicToneMapping, toneMappingExposure: 1.1 }}
      camera={{ position: [0, 9, 12], fov: 42, near: 0.1, far: 120 }}
    >
      <ORScene machines={machines} machinesOn={machinesOn} />
    </Canvas>
  )}
/**
 * MedicalModels3D.jsx
 * Detailed procedural 3D models for every OR machine type + OR personnel.
 * All models sit with y=0 at floor level.
 */
import React, { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

//  Primitive helpers 
function Box({ p = [0, 0, 0], s = [1, 1, 1], rot = [0, 0, 0], color = '#aabbcc',
               rough = 0.35, metal = 0.65, emissive = null, emissiveIntensity = 0, transparent = false, opacity = 1, side }) {
  return (
    <mesh position={p} rotation={rot} castShadow receiveShadow>
      <boxGeometry args={s} />
      <meshStandardMaterial color={color} roughness={rough} metalness={metal}
        emissive={emissive || color} emissiveIntensity={emissiveIntensity}
        transparent={transparent} opacity={opacity} side={side} />
    </mesh>
  )
}
function Cyl({ p = [0, 0, 0], r = 0.1, h = 1, top, segs = 14, rot = [0, 0, 0],
               color = '#aabbcc', rough = 0.35, metal = 0.7, emissive = null, emissiveIntensity = 0 }) {
  return (
    <mesh position={p} rotation={rot} castShadow>
      <cylinderGeometry args={[top ?? r, r, h, segs]} />
      <meshStandardMaterial color={color} roughness={rough} metalness={metal}
        emissive={emissive || color} emissiveIntensity={emissiveIntensity} />
    </mesh>
  )
}
function Sph({ p = [0, 0, 0], r = 0.1, color = '#ddccbb', rough = 0.6, metal = 0.0 }) {
  return (
    <mesh position={p} castShadow>
      <sphereGeometry args={[r, 12, 10]} />
      <meshStandardMaterial color={color} roughness={rough} metalness={metal} />
    </mesh>
  )
}
function Screen({ p, w, h, isOn, color, rough = 0.1, metal = 0.05 }) {
  const ref = useRef()
  useFrame(() => {
    if (ref.current && isOn) ref.current.material.emissiveIntensity = 0.6 + 0.15 * Math.sin(Date.now() * 0.0018)
  })
  return (
    <mesh ref={ref} position={p} castShadow>
      <boxGeometry args={[w, h, 0.012]} />
      <meshStandardMaterial color={isOn ? '#090e18' : '#06090e'}
        emissive={isOn ? color : '#000000'} emissiveIntensity={isOn ? 0.6 : 0}
        roughness={rough} metalness={metal} />
    </mesh>
  )
}
function Wheel({ p }) {
  return (
    <group position={p}>
      <Cyl r={0.06} h={0.04} rot={[Math.PI / 2, 0, 0]} color="#222" rough={0.9} metal={0.1} />
    </group>
  )
}
function Wheels4({ y = 0.06, span = 0.28, depth = 0.22 }) {
  const corners = [[-span, 0, depth], [span, 0, depth], [-span, 0, -depth], [span, 0, -depth]]
  return <>{corners.map((c, i) => <Wheel key={i} p={[c[0], y, c[2]]} />)}</>
}

// ─── Animated atom components ────────────────────────────────────────────────

/** Blinking status LED — pulses at ~2 Hz when isOn */
function AnimLED({ isOn, position, color = '#00ff88', r = 0.016, speed = 1.4, phase = 0 }) {
  const matRef = useRef()
  useFrame(() => {
    if (!matRef.current) return
    if (!isOn) { matRef.current.emissiveIntensity = 0; return }
    const t = (Date.now() * 0.001 * speed + phase) % 1.0
    matRef.current.emissiveIntensity = t < 0.5 ? 2.8 : 0.25
  })
  return (
    <mesh position={position}>
      <sphereGeometry args={[r, 8, 6]} />
      <meshStandardMaterial ref={matRef} color={color} emissive={color}
        emissiveIntensity={0} roughness={0.2} metalness={0} />
    </mesh>
  )
}

/** Roller pump module with spinning drum for HeartLungMachine */
function RollerPump({ position, isOn, speed = 2.8 }) {
  const drumRef = useRef()
  useFrame((_, delta) => {
    if (drumRef.current && isOn) drumRef.current.rotation.z += delta * speed
  })
  return (
    <group position={position}>
      {/* Housing plate */}
      <Box p={[0, 0, 0]} s={[0.88, 0.22, 0.04]} color="#8898a8" rough={0.3} metal={0.7} />
      {/* Spinning drum + roller arms */}
      <group ref={drumRef}>
        <mesh position={[0, 0, 0.03]} rotation={[Math.PI / 2, 0, 0]} castShadow>
          <cylinderGeometry args={[0.08, 0.08, 0.30, 10]} />
          <meshStandardMaterial color="#3a5a6a" roughness={0.3} metalness={0.65}
            emissive={isOn ? '#004488' : '#000'} emissiveIntensity={isOn ? 0.25 : 0} />
        </mesh>
        {/* Two roller arms at 180° offset */}
        {[0.092, -0.092].map((offset, i) => (
          <mesh key={i} position={[offset, 0, 0.03]} rotation={[Math.PI / 2, 0, 0]} castShadow>
            <cylinderGeometry args={[0.018, 0.018, 0.32, 8]} />
            <meshStandardMaterial color="#cc3333" roughness={0.4} metalness={0.55} />
          </mesh>
        ))}
      </group>
      <Screen p={[0.31, 0, 0.032]} w={0.20} h={0.14} isOn={isOn} color="#00ff88" />
    </group>
  )
}

//  Machine 3D Models 

export function AnesthesiaMachine({ isOn }) {
  return (
    <group>
      <Wheels4 y={0.055} span={0.32} depth={0.27} />
      {/* Main body */}
      <Box p={[0, 0.85, 0]} s={[0.72, 1.28, 0.62]} color="#b8c8cc" rough={0.25} metal={0.72} />
      {/* Vaporizer column (right side) */}
      <Box p={[0.3, 0.78, 0]} s={[0.14, 1.08, 0.58]} color="#8898a8" rough={0.2} metal={0.8} />
      {/* O2 cylinder (green) — back left */}
      <Cyl p={[-0.28, 0.80, -0.32]} r={0.07} h={0.9} color="#1a8c1a" rough={0.4} metal={0.6} />
      <Cyl p={[-0.28, 1.28, -0.32]} r={0.06} h={0.06} color="#ccc" rough={0.3} metal={0.9} />
      {/* N2O cylinder (blue) — back right */}
      <Cyl p={[0.18, 0.78, -0.32]} r={0.065} h={0.85} color="#1a4aaa" rough={0.4} metal={0.6} />
      {/* Absorber canister (round, front low) */}
      <Cyl p={[-0.18, 0.36, 0.32]} r={0.1} h={0.28} color="#e8eeff" rough={0.3} metal={0.2} />
      {/* Control panel front */}
      <Box p={[0, 1.0, 0.32]} s={[0.58, 0.4, 0.01]} color="#1c2c3c" rough={0.8} metal={0.05} />
      {/* Main screen / display */}
      <Screen p={[-0.12, 1.24, 0.32]} w={0.3} h={0.22} isOn={isOn} color="#00d8a0" />
      {/* Small numeric display right */}
      <Screen p={[0.2, 1.24, 0.32]} w={0.16} h={0.2} isOn={isOn} color="#00ccff" />
      {/* Knobs row */}
      {[-0.2, -0.05, 0.1].map((x, i) => (
        <Cyl key={i} p={[x, 0.88, 0.33]} r={0.028} h={0.025} rot={[Math.PI/2,0,0]} color="#3a4a5a" rough={0.5} metal={0.7} />
      ))}
      {/* Breathing circuit arm */}
      <Cyl p={[-0.28, 1.52, 0]} r={0.018} h={0.28} color="#ccc" rough={0.3} metal={0.85} />
      <Cyl p={[-0.28, 1.67, 0.14]} r={0.016} h={0.28} rot={[Math.PI/4,0,0]} color="#ccc" rough={0.3} metal={0.85} />
      {/* Corrugated circuit hose */}
      {[0,1,2,3,4].map(i => (
        <Cyl key={i} p={[-0.28, 1.73, 0.28 + i*0.04]} r={0.022} h={0.038} rot={[Math.PI/2,0,0]} color="#88aacc" rough={0.6} metal={0.1} />
      ))}
      {/* Top shelf */}
      <Box p={[0, 1.52, 0]} s={[0.72, 0.04, 0.6]} color="#a0b8c0" rough={0.3} metal={0.7} />
      {/* Monitor on arm above */}
      <Cyl p={[0, 1.60, 0]} r={0.025} h={0.35} color="#888" rough={0.3} metal={0.8} />
      <Box p={[0, 1.87, 0.15]} s={[0.38, 0.28, 0.04]} color="#1a2030" rough={0.2} metal={0.3} />
      <Screen p={[0, 1.87, 0.17]} w={0.34} h={0.24} isOn={isOn} color="#00e8b0" />
      {/* LED row front panel */}
      {isOn && [[-0.22,0.78,0.33],[0,0.78,0.33],[0.22,0.78,0.33]].map(([x,y,z],i) => (
        <Sph key={i} p={[x,y,z]} r={0.015} color={i===0?'#00ff66':i===1?'#ffcc00':'#ff4444'} rough={0.05} metal={0} />
      ))}
    </group>
  )
}

export function PatientMonitor({ isOn }) {
  return (
    <group>
      {/* Base cross */}
      <Box p={[0, 0.04, 0]} s={[0.55, 0.07, 0.18]} color="#8898a8" rough={0.3} metal={0.8} />
      <Box p={[0, 0.04, 0]} s={[0.18, 0.07, 0.55]} color="#8898a8" rough={0.3} metal={0.8} />
      <Wheels4 y={0.04} span={0.24} depth={0.24} />
      {/* Pole */}
      <Cyl p={[0, 0.82, 0]} r={0.025} h={1.5} color="#b4c0c8" rough={0.25} metal={0.88} />
      {/* Articulated arm */}
      <Box p={[0, 1.52, 0.15]} s={[0.06, 0.055, 0.32]} color="#9aabb8" rough={0.3} metal={0.8} />
      {/* Monitor housing */}
      <Box p={[0, 1.52, 0.35]} s={[0.56, 0.42, 0.08]} color="#1c2838" rough={0.3} metal={0.5} />
      {/* Main screen */}
      <Screen p={[0, 1.55, 0.40]} w={0.5} h={0.34} isOn={isOn} color="#00ff88" />
      {/* ECG trace overlay (static lines) */}
      {isOn && (
        <Box p={[0, 1.56, 0.405]} s={[0.46, 0.005, 0.001]} color="#00ff88"
          rough={0.1} metal={0} emissive="#00ff88" emissiveIntensity={2} />
      )}
      {/* SpO2 reading */}
      <Screen p={[-0.15, 1.42, 0.40]} w={0.16} h={0.08} isOn={isOn} color="#00ccff" />
      {/* NIBP reading */}
      <Screen p={[0.15, 1.42, 0.40]} w={0.16} h={0.08} isOn={isOn} color="#ff4488" />
      {/* Alarm buttons */}
      {isOn && [[-0.2, 1.63, 0.40],[0,1.63,0.40],[0.2,1.63,0.40]].map(([x,y,z],i) => (
        <Sph key={i} p={[x,y,z]} r={0.016} color={i===0?'#00ff88':i===1?'#ffcc00':'#ff3333'} rough={0.1} metal={0} />
      ))}
    </group>
  )
}

export function Ventilator({ isOn }) {
  const bellowsRef = useRef()
  useFrame(() => {
    if (!bellowsRef.current) return
    if (!isOn) { bellowsRef.current.scale.y = 1; bellowsRef.current.scale.x = 1; return }
    const breathe = 0.5 + 0.5 * Math.sin(Date.now() * 0.0016)
    bellowsRef.current.scale.y = 0.72 + 0.50 * breathe
    bellowsRef.current.scale.x = 0.72 + 0.50 * breathe
  })
  return (
    <group>
      <Wheels4 y={0.055} span={0.26} depth={0.22} />
      {/* Main body */}
      <Box p={[0, 0.68, 0]} s={[0.58, 1.24, 0.52]} color="#c0cccc" rough={0.28} metal={0.72} />
      {/* Transparent bellows window frame */}
      <Box p={[0, 0.88, 0.264]} s={[0.44, 0.36, 0.006]} color="#1a2a3a" rough={0.3} metal={0.7} />
      {/* Animated bellows accordion visible through window */}
      <group ref={bellowsRef}>
        {[0,1,2,3,4].map(i => (
          <mesh key={i} position={[0, 0.75 + i * 0.044, 0.267]} rotation={[Math.PI/2, 0, 0]} castShadow>
            <cylinderGeometry args={[0.13 + (i % 2) * 0.028, 0.13 + (i % 2) * 0.028, 0.028, 18]} />
            <meshStandardMaterial color={isOn ? '#88c0e0' : '#3a4a5a'} roughness={0.4} metalness={0.1} />
          </mesh>
        ))}
      </group>
      {/* Text display */}
      <Screen p={[0, 1.12, 0.27]} w={0.44} h={0.18} isOn={isOn} color="#00e0ff" />
      {/* Knobs */}
      {[[-0.16,0.64,0.27],[0,0.64,0.27],[0.16,0.64,0.27]].map(([x,y,z],i) => (
        <Cyl key={i} p={[x,y,z]} r={0.035} h={0.03} rot={[Math.PI/2,0,0]} color="#4a5a6a" rough={0.4} metal={0.7} />
      ))}
      {/* Tubing ports */}
      <Cyl p={[-0.15, 0.38, 0.27]} r={0.025} h={0.04} rot={[Math.PI/2,0,0]} color="#88aaaa" rough={0.4} metal={0.5} />
      <Cyl p={[0.15, 0.38, 0.27]} r={0.025} h={0.04} rot={[Math.PI/2,0,0]} color="#8aaa88" rough={0.4} metal={0.5} />
      {/* Corrugated breathing tubes */}
      {[0,1,2,3,4,5].map(i => (
        <Cyl key={i} p={[-0.15, 0.38-i*0.06, 0.3+i*0.04]} r={0.022} h={0.038} rot={[Math.PI/3,0,0]} color="#99bbcc" rough={0.6} metal={0.1} />
      ))}
      {/* Blinking LED status */}
      <AnimLED isOn={isOn} position={[0.20, 1.22, 0.27]} color="#00ff88" speed={1.6} />
      {/* Top vents */}
      {[-0.2,-0.13,-0.06,0.01,0.08,0.15,0.22].map((x,i) => (
        <Box key={i} p={[x, 1.31, 0]} s={[0.018, 0.02, 0.48]} color="#8898a8" rough={0.6} metal={0.4} />
      ))}
    </group>
  )
}

export function HeartLungMachine({ isOn }) {
  return (
    <group>
      <Wheels4 y={0.055} span={0.48} depth={0.4} />
      {/* Main console body */}
      <Box p={[0, 1.0, 0]} s={[1.05, 1.82, 0.88]} color="#b0bccc" rough={0.25} metal={0.75} />
      {/* Console screen (top) */}
      <Screen p={[0, 1.74, 0.45]} w={0.78} h={0.28} isOn={isOn} color="#00ffaa" />
      {/* 4 Animated roller pump modules */}
      {[0, 1, 2, 3].map(i => (
        <RollerPump key={i} position={[0, 0.72 + i * 0.28, 0.45]}
          isOn={isOn} speed={2.4 + i * 0.18} />
      ))}
      {/* Oxygenator column (right side, transparent) */}
      <Cyl p={[0.62, 0.85, 0]} r={0.10} h={1.0} color="#e8f0f8" rough={0.2} metal={0.1} />
      <Box p={[0.62, 1.42, 0]} s={[0.22, 0.12, 0.22]} color="#9aabb8" rough={0.3} metal={0.7} />
      {/* Cardiotomy reservoir */}
      <Cyl p={[-0.6, 0.72, 0]} r={0.09} h={0.80} color="#aaddff" rough={0.1} metal={0.05} transparent={true} />
      {/* Tubing connectors */}
      {[-0.3,-0.15,0,0.15,0.3].map((x,i) => (
        <Cyl key={i} p={[x, 0.2, 0.45]} r={0.022} h={0.05} rot={[Math.PI/2,0,0]} color="#cc8844" rough={0.3} metal={0.5} />
      ))}
      {/* Blinking status LEDs */}
      {[[-0.4,1.56,0.45],[0,1.56,0.45],[0.4,1.56,0.45]].map(([x,y,z],i) => (
        <AnimLED key={i} isOn={isOn} position={[x,y,z]}
          color={i===0?'#00ff66':i===1?'#00ccff':'#ff4422'} phase={i * 0.33} />
      ))}
    </group>
  )
}

export function Defibrillator({ isOn }) {
  return (
    <group>
      <Wheels4 y={0.055} span={0.22} depth={0.18} />
      {/* Cart body */}
      <Box p={[0, 0.42, 0]} s={[0.54, 0.72, 0.45]} color="#c8d0d8" rough={0.28} metal={0.72} />
      {/* Main device box on top */}
      <Box p={[0, 0.95, 0]} s={[0.48, 0.36, 0.40]} color="#2a3848" rough={0.4} metal={0.5} />
      {/* Big screen */}
      <Screen p={[0, 0.97, 0.21]} w={0.4} h={0.28} isOn={isOn} color="#00ff88" />
      {/* ECG shock waveform stripe */}
      {isOn && <Box p={[0, 0.97, 0.215]} s={[0.36, 0.004, 0.001]} color="#00ff88" rough={0.1} metal={0} emissive="#00ff88" emissiveIntensity={3} />}
      {/* Energy selector knob */}
      <Cyl p={[-0.14, 0.82, 0.21]} r={0.04} h={0.03} rot={[Math.PI/2,0,0]} color="#4a5a6a" rough={0.4} metal={0.7} />
      {/* Paddle cable connectors */}
      <Cyl p={[0.1, 0.82, 0.21]} r={0.025} h={0.03} rot={[Math.PI/2,0,0]} color="#cc2222" rough={0.4} metal={0.5} />
      <Cyl p={[0.18, 0.82, 0.21]} r={0.025} h={0.03} rot={[Math.PI/2,0,0]} color="#222288" rough={0.4} metal={0.5} />
      {/* Paddles hanging on side */}
      <Box p={[0.3, 0.88, 0]} s={[0.04, 0.28, 0.16]} color="#cc2222" rough={0.5} metal={0.4} />
      <Box p={[0.3, 0.60, 0]} s={[0.06, 0.06, 0.18]} color="#dd3333" rough={0.4} metal={0.5} />
      {/* SHOCK button */}
      <Box p={[0, 0.80, 0.21]} s={[0.06, 0.04, 0.01]}
        color={isOn ? '#ff4400' : '#440000'} rough={0.4} metal={0.3}
        emissive={isOn ? '#ff4400' : '#000'} emissiveIntensity={isOn ? 1.2 : 0} />
      {/* Blinking charge indicator */}
      <AnimLED isOn={isOn} position={[0.20, 1.06, 0.21]} color="#00ff88" speed={2.2} />
    </group>
  )
}

export function ESU({ isOn }) {
  return (
    <group>
      <Wheels4 y={0.04} span={0.24} depth={0.2} />
      {/* Stacked unit body */}
      <Box p={[0, 0.38, 0]} s={[0.62, 0.64, 0.52]} color="#d0d8dc" rough={0.3} metal={0.65} />
      {/* Front panel */}
      <Box p={[0, 0.38, 0.27]} s={[0.58, 0.6, 0.01]} color="#1c2c38" rough={0.8} metal={0.05} />
      {/* Power indicator */}
      <Cyl p={[-0.18, 0.55, 0.28]} r={0.03} h={0.01} segs={12} rot={[Math.PI/2,0,0]}
        color={isOn ? '#00ff44' : '#1a2a1a'} rough={0.2} metal={0.05}
        emissive={isOn ? '#00ff44' : '#000'} emissiveIntensity={isOn ? 2.0 : 0} />
      {/* Power meter / screen */}
      <Screen p={[0.08, 0.52, 0.28]} w={0.28} h={0.2} isOn={isOn} color="#ff8800" />
      {/* Cut / coag selector */}
      {[[-0.2, 0.3], [-0.04, 0.3], [0.12, 0.3]].map(([x, y], i) => (
        <Cyl key={i} p={[x, y, 0.28]} r={0.032} h={0.012} rot={[Math.PI/2,0,0]} color="#5a6a7a" rough={0.4} metal={0.7} />
      ))}
      {/* Neutral / active electrode sockets */}
      <Cyl p={[-0.18, 0.16, 0.28]} r={0.025} h={0.015} rot={[Math.PI/2,0,0]} color="#bb3300" rough={0.4} metal={0.5} />
      <Cyl p={[0.08, 0.16, 0.28]} r={0.025} h={0.015} rot={[Math.PI/2,0,0]} color="#003388" rough={0.4} metal={0.5} />
      {/* Foot pedal cable socket */}
      <Box p={[0, 0.08, 0.27]} s={[0.12, 0.04, 0.01]} color="#3a4a5a" rough={0.5} metal={0.5} />
    </group>
  )
}

export function SuctionDevice({ isOn }) {
  return (
    <group>
      <Wheels4 y={0.04} span={0.2} depth={0.16} />
      <Box p={[0, 0.34, 0]} s={[0.5, 0.56, 0.42]} color="#c8d4d8" rough={0.3} metal={0.65} />
      {/* Suction canister (transparent) */}
      <Cyl p={[0, 0.5, 0.22]} r={0.1} h={0.44} color="#aaddee" rough={0.1} metal={0.05}
        emissive={isOn ? '#cc3322' : '#220000'} emissiveIntensity={isOn ? 0.1 : 0} />
      {/* Canister cap */}
      <Cyl p={[0, 0.73, 0.22]} r={0.105} h={0.04} color="#6a8898" rough={0.3} metal={0.7} />
      {/* Motor box */}
      <Box p={[0, 0.16, 0]} s={[0.44, 0.2, 0.38]} color="#a8b8c0" rough={0.3} metal={0.7} />
      {/* Suction tubing port */}
      <Cyl p={[0, 0.73, 0.33]} r={0.018} h={0.05} rot={[Math.PI/2,0,0]} color="#88aaaa" rough={0.4} metal={0.5} />
      {/* Control panel */}
      <Screen p={[0, 0.44, 0.22]} w={0.3} h={0.1} isOn={isOn} color="#00ccff" />
      {/* Power LED */}
      {isOn && <Sph p={[0.14, 0.56, 0.22]} r={0.015} color="#00ff88" rough={0.1} metal={0} />}
    </group>
  )
}

export function WarmingBlanket({ isOn }) {
  return (
    <group>
      <Wheels4 y={0.04} span={0.18} depth={0.14} />
      <Box p={[0, 0.3, 0]} s={[0.44, 0.48, 0.38]} color="#e8d8b0" rough={0.5} metal={0.3} />
      {/* Display */}
      <Screen p={[0, 0.38, 0.20]} w={0.3} h={0.2} isOn={isOn} color="#ff8800" />
      {/* Hose port (warm air) */}
      <Cyl p={[0.14, 0.15, 0.20]} r={0.045} h={0.04} rot={[Math.PI/2,0,0]} color="#cc8844" rough={0.5} metal={0.4} />
      {/* Temperature knob */}
      <Cyl p={[-0.1, 0.22, 0.20]} r={0.035} h={0.02} rot={[Math.PI/2,0,0]} color="#4a3a2a" rough={0.4} metal={0.6} />
      {/* Logo plate */}
      <Box p={[0, 0.52, 0.20]} s={[0.26, 0.04, 0.01]} color="#c8a878" rough={0.6} metal={0.4} />
      {isOn && <Sph p={[0.14, 0.4, 0.20]} r={0.014} color="#ff6600" rough={0.05} metal={0} />}
    </group>
  )
}

export function InstrumentTable({ isOn }) {
  /* Mayo stand – cross base, vertical pole, overbed tray */
  return (
    <group>
      {/* Cross base */}
      <Box p={[0, 0.03, 0]} s={[0.72, 0.045, 0.16]} color="#8090a0" rough={0.3} metal={0.85} />
      <Box p={[0, 0.03, 0]} s={[0.16, 0.045, 0.72]} color="#8090a0" rough={0.3} metal={0.85} />
      <Wheels4 y={0.03} span={0.33} depth={0.33} />
      {/* Vertical pole */}
      <Cyl p={[0, 0.65, 0]} r={0.025} h={1.18} color="#b0bcc8" rough={0.25} metal={0.88} />
      {/* Horizontal arm extending out */}
      <Box p={[0, 1.22, 0.3]} s={[0.055, 0.05, 0.64]} color="#9aaab8" rough={0.28} metal={0.85} />
      {/* Tray surface */}
      <Box p={[0, 1.26, 0.56]} s={[0.8, 0.025, 0.55]} color="#c8d8e0" rough={0.2} metal={0.9} />
      {/* Sterile drape on tray */}
      <Box p={[0, 1.28, 0.56]} s={[0.78, 0.01, 0.52]} color="#e4eef0" rough={0.9} metal={0.0} />
      {/* Instrument suggestions */}
      {[[-0.28,1.295,0.38],[-0.14,1.295,0.38],[0,1.295,0.38],[0.14,1.295,0.38],[0.28,1.295,0.38],
        [-0.28,1.295,0.6],[0,1.295,0.6],[0.28,1.295,0.6]].map(([x,y,z],i) => (
        <Cyl key={i} p={[x,y,z]} r={0.008} h={0.04} color="#d8e8ec" rough={0.2} metal={0.9} />
      ))}
    </group>
  )
}

export function CellSaver({ isOn }) {
  const centRef = useRef()
  useFrame((_, delta) => {
    if (centRef.current && isOn) centRef.current.rotation.y += delta * 9.0
  })
  return (
    <group>
      <Wheels4 y={0.055} span={0.28} depth={0.24} />
      <Box p={[0, 0.72, 0]} s={[0.68, 1.22, 0.58]} color="#c0ccd4" rough={0.28} metal={0.72} />
      {/* Centrifuge bowl housing (static outer) */}
      <Cyl p={[0, 1.40, 0.1]} r={0.16} h={0.22} color="#e8f4f8" rough={0.2} metal={0.2} />
      {/* Spinning centrifuge bowl + fins */}
      <group ref={centRef} position={[0, 1.42, 0.1]}>
        <mesh castShadow>
          <cylinderGeometry args={[0.11, 0.08, 0.14, 14]} />
          <meshStandardMaterial color="#cc4444" roughness={0.1} metalness={0.05}
            emissive={isOn ? '#cc2222' : '#000'} emissiveIntensity={isOn ? 0.18 : 0} />
        </mesh>
        {/* Centrifuge fins (5) */}
        {[0, 72, 144, 216, 288].map((deg, i) => {
          const a = deg * Math.PI / 180
          return (
            <mesh key={i} position={[0.065 * Math.cos(a), 0, 0.065 * Math.sin(a)]} castShadow>
              <boxGeometry args={[0.016, 0.10, 0.040]} />
              <meshStandardMaterial color="#bb3333" roughness={0.2} metalness={0.2} />
            </mesh>
          )
        })}
      </group>
      {/* Blood reservoir bag */}
      <Box p={[-0.22, 1.26, 0]} s={[0.18, 0.28, 0.10]}
        color={isOn ? '#cc2222' : '#550000'} rough={0.5} metal={0.0} />
      {/* Screen */}
      <Screen p={[0, 0.85, 0.30]} w={0.46} h={0.22} isOn={isOn} color="#00ff88" />
      {/* Control panel */}
      <Box p={[0, 0.56, 0.30]} s={[0.56, 0.2, 0.01]} color="#1c2838" rough={0.8} metal={0.05} />
      {[[-0.2,0.56,0.31],[-0.06,0.56,0.31],[0.08,0.56,0.31],[0.22,0.56,0.31]].map(([x,y,z],i) => (
        <Cyl key={i} p={[x,y,z]} r={0.028} h={0.012} rot={[Math.PI/2,0,0]} color="#4a6a7a" rough={0.4} metal={0.7} />
      ))}
      <AnimLED isOn={isOn} position={[0.24, 0.88, 0.30]} color="#00ff44" speed={1.2} />
    </group>
  )
}

export function BloodWarmer({ isOn }) {
  return (
    <group>
      {/* IV pole base */}
      <Box p={[0, 0.03, 0]} s={[0.52, 0.045, 0.16]} color="#8090a0" rough={0.3} metal={0.85} />
      <Box p={[0, 0.03, 0]} s={[0.16, 0.045, 0.52]} color="#8090a0" rough={0.3} metal={0.85} />
      <Wheels4 y={0.03} span={0.23} depth={0.23} />
      {/* IV pole */}
      <Cyl p={[0, 0.9, 0]} r={0.022} h={1.68} color="#b0bcc8" rough={0.25} metal={0.88} />
      {/* Warmer unit (clipped to pole) */}
      <Box p={[0.1, 0.9, 0]} s={[0.22, 0.42, 0.18]} color="#c8d0d8" rough={0.3} metal={0.65} />
      <Screen p={[0.12, 0.95, 0.10]} w={0.16} h={0.14} isOn={isOn} color="#ff6600" />
      {/* IV hooks at top */}
      <Box p={[0, 1.76, 0]} rot={[0,0,Math.PI/2]} s={[0.024, 0.3, 0.024]} color="#c0bcc8" rough={0.3} metal={0.88} />
      <Cyl p={[-0.13, 1.76, 0]} r={0.012} h={0.04} rot={[Math.PI/2,0,0]} color="#c0bcc8" rough={0.3} metal={0.88} />
      <Cyl p={[0.13, 1.76, 0]} r={0.012} h={0.04} rot={[Math.PI/2,0,0]} color="#c0bcc8" rough={0.3} metal={0.88} />
      {/* Tubing coil */}
      {[0,1,2,3,4].map(i => (
        <Cyl key={i} p={[0.1, 0.70+i*0.03, 0.09+i*0.005]} r={0.008} h={0.022} rot={[Math.PI/2,0,0]} color="#88ccee" rough={0.4} metal={0.1} />
      ))}
      {isOn && <Sph p={[0.18, 1.04, 0.10]} r={0.014} color="#ff6600" rough={0.05} metal={0} />}
    </group>
  )
}

export function IABPump({ isOn }) {
  return (
    <group>
      <Wheels4 y={0.055} span={0.26} depth={0.22} />
      {/* Tall body */}
      <Box p={[0, 0.92, 0]} s={[0.6, 1.62, 0.55]} color="#c8d0dc" rough={0.28} metal={0.72} />
      {/* Balloon waveform screen */}
      <Screen p={[0, 1.32, 0.28]} w={0.46} h={0.36} isOn={isOn} color="#ff4488" />
      {/* Helium cylinder (side) */}
      <Cyl p={[0.35, 0.72, 0]} r={0.075} h={0.8} color="#ddee44" rough={0.4} metal={0.65} />
      <Cyl p={[0.35, 1.14, 0]} r={0.055} h={0.04} color="#aaa" rough={0.3} metal={0.85} />
      {/* Control knobs */}
      {[-0.16,0,0.16].map((x,i) => (
        <Cyl key={i} p={[x, 0.92, 0.28]} r={0.032} h={0.022} rot={[Math.PI/2,0,0]} color="#4a5a6a" rough={0.4} metal={0.7} />
      ))}
      {/* Catheter port  */}
      <Cyl p={[0, 0.60, 0.28]} r={0.02} h={0.03} rot={[Math.PI/2,0,0]} color="#ee3366" rough={0.4} metal={0.5} />
      {/* Alarm panel */}
      <Box p={[0, 1.62, 0.28]} s={[0.44, 0.12, 0.01]} color="#1c2838" rough={0.8} metal={0.05} />
      {/* Blinking alarm LEDs */}
      {[[-0.16,1.62,0.285],[0,1.62,0.285],[0.16,1.62,0.285]].map(([x,y,z],i) => (
        <AnimLED key={i} isOn={isOn} position={[x,y,z]}
          color={i===0?'#00ff44':i===1?'#ffcc00':'#ff2244'} phase={i * 0.28} speed={1.8 + i * 0.4} />
      ))}
    </group>
  )
}

export function LaparoscopyTower({ isOn }) {
  return (
    <group>
      <Wheels4 y={0.055} span={0.34} depth={0.28} />
      {/* Cart rail/frame */}
      <Box p={[0, 0.92, 0]} s={[0.08, 1.72, 0.08]} color="#787888" rough={0.3} metal={0.8} />
      <Box p={[0.34, 0.92, 0]} s={[0.08, 1.72, 0.08]} color="#787888" rough={0.3} metal={0.8} />
      <Box p={[-0.34, 0.92, 0]} s={[0.08, 1.72, 0.08]} color="#787888" rough={0.3} metal={0.8} />
      {/* Shelf 1 (bottom) — CO2 insufflator */}
      <Box p={[0, 0.38, 0]} s={[0.72, 0.22, 0.58]} color="#c4d0d8" rough={0.3} metal={0.7} />
      <Screen p={[0, 0.38, 0.30]} w={0.5} h={0.14} isOn={isOn} color="#00ffcc" />
      {/* Shelf 2 — light source */}
      <Box p={[0, 0.74, 0]} s={[0.72, 0.22, 0.58]} color="#b8c8d0" rough={0.3} metal={0.7} />
      <Box p={[0.16, 0.74, 0.30]} s={[0.24, 0.14, 0.01]}
        color={isOn ? '#ffffee' : '#111'} rough={0.1} metal={0.05}
        emissive={isOn ? '#ffffc0' : '#000'} emissiveIntensity={isOn ? 2.0 : 0} />
      <Cyl p={[-0.2, 0.72, 0.30]} r={0.05} h={0.01} rot={[Math.PI/2,0,0]}
        color={isOn ? '#ffffff' : '#220000'} rough={0.05} metal={0.05}
        emissive={isOn ? '#ffffff' : '#000'} emissiveIntensity={isOn ? 3.0 : 0} />
      {/* Shelf 3 — camera control unit */}
      <Box p={[0, 1.10, 0]} s={[0.72, 0.22, 0.58]} color="#b0c0c8" rough={0.3} metal={0.7} />
      <Screen p={[0, 1.10, 0.30]} w={0.56} h={0.15} isOn={isOn} color="#ffcc00" />
      {/* Main laparoscopy monitor — large on top */}
      <Cyl p={[0, 1.52, 0]} r={0.025} h={0.25} color="#888" rough={0.3} metal={0.8} />
      <Box p={[0, 1.68, 0.15]} s={[0.72, 0.54, 0.06]} color="#1a2030" rough={0.2} metal={0.3} />
      <Screen p={[0, 1.68, 0.18]} w={0.66} h={0.48} isOn={isOn} color="#e0f8a0" />
      {/* Scope holder on side */}
      <Cyl p={[-0.4, 1.0, 0]} r={0.018} h={0.08} rot={[0,0,Math.PI/2]} color="#9ab0b8" rough={0.3} metal={0.75} />
    </group>
  )
}

export function CO2Insufflator({ isOn }) {
  return (
    <group>
      <Wheels4 y={0.04} span={0.2} depth={0.16} />
      <Box p={[0, 0.3, 0]} s={[0.52, 0.48, 0.42]} color="#d0d8dc" rough={0.3} metal={0.65} />
      <Screen p={[0, 0.36, 0.22]} w={0.36} h={0.2} isOn={isOn} color="#00ccff" />
      <Box p={[0, 0.18, 0.22]} s={[0.44, 0.12, 0.01]} color="#1c2838" rough={0.8} metal={0.05} />
      {/* CO2 tank port */}
      <Cyl p={[0.18, 0.1, 0.22]} r={0.025} h={0.015} rot={[Math.PI/2,0,0]} color="#ddee44" rough={0.4} metal={0.5} />
      {/* Patient line port */}
      <Cyl p={[-0.1, 0.1, 0.22]} r={0.02} h={0.015} rot={[Math.PI/2,0,0]} color="#88aacc" rough={0.4} metal={0.5} />
      <Box p={[0, 0.52, 0.22]} s={[0.3, 0.04, 0.01]} color="#2a3848" rough={0.7} metal={0.3} />
      {isOn && <Sph p={[0.2, 0.4, 0.22]} r={0.015} color="#00ccff" rough={0.05} metal={0} />}
    </group>
  )
}

export function CArm({ isOn }) {
  const archRef = useRef()
  useFrame(() => {
    if (!archRef.current) return
    if (isOn) archRef.current.rotation.z = 0.05 * Math.sin(Date.now() * 0.0006)
    else archRef.current.rotation.z = 0
  })
  return (
    <group>
      {/* Mobile base */}
      <Box p={[0, 0.08, 0]} s={[0.88, 0.15, 0.62]} color="#a0b0b8" rough={0.25} metal={0.78} />
      {/* 4 large wheels */}
      {[[-0.38,0.06,0.28],[0.38,0.06,0.28],[-0.38,0.06,-0.28],[0.38,0.06,-0.28]].map((p,i) => (
        <Cyl key={i} p={p} r={0.09} h={0.07} rot={[Math.PI/2,0,0]} color="#222" rough={0.9} metal={0.1} />
      ))}
      {/* Console on base */}
      <Box p={[0, 0.46, 0]} s={[0.72, 0.6, 0.52]} color="#b0c0c8" rough={0.28} metal={0.72} />
      <Screen p={[0, 0.52, 0.27]} w={0.54} h={0.34} isOn={isOn} color="#88ccff" />
      {/* Vertical column */}
      <Cyl p={[0, 1.02, 0]} r={0.04} h={0.78} color="#9aaab8" rough={0.28} metal={0.82} />
      {/* Horizontal arm going right */}
      <Box p={[0.38, 1.36, 0]} s={[0.8, 0.045, 0.045]} color="#9aaab8" rough={0.28} metal={0.82} />
      {/* Animated C-arch — gentle positioning sway */}
      <group ref={archRef} position={[0.88, 1.36, 0]}>
        {Array.from({length: 8}, (_, i) => {
          const angle = -Math.PI * 0.2 + (Math.PI * 0.9 * i / 7)
          const r = 0.72
          return <Box key={i} p={[r*Math.sin(angle), r*Math.cos(angle)-r, 0]}
            rot={[0,0,-angle]} s={[0.25, 0.08, 0.06]}
            color="#9aaab8" rough={0.28} metal={0.82} />
        })}
        {/* X-ray tube head (top of C) */}
        <Box p={[0, 0.72, 0]} s={[0.2, 0.16, 0.14]} color="#2a3848" rough={0.4} metal={0.6} />
        <Cyl p={[0, 0.80, 0]} r={0.06} h={0.08} top={0.04} color="#1a2838" rough={0.5} metal={0.5} />
        {/* Flat panel detector (bottom of C) */}
        <Box p={[0, -0.72, 0]} s={[0.3, 0.024, 0.26]} color="#1a2838" rough={0.3} metal={0.4} />
      </group>
      <AnimLED isOn={isOn} position={[0.3, 0.72, 0.27]} color="#00ccff" speed={1.0} />
    </group>
  )
}

export function Microscope({ isOn }) {
  const ringMatRef = useRef()
  useFrame(() => {
    if (!ringMatRef.current) return
    if (!isOn) { ringMatRef.current.emissiveIntensity = 0; return }
    ringMatRef.current.emissiveIntensity = 1.4 + 0.7 * Math.sin(Date.now() * 0.0022)
  })
  return (
    <group>
      <Wheels4 y={0.055} span={0.26} depth={0.22} />
      {/* Base block */}
      <Box p={[0, 0.22, 0]} s={[0.62, 0.32, 0.52]} color="#c0ccd4" rough={0.28} metal={0.72} />
      {/* Balance arm (horizontal reach) */}
      <Box p={[-0.12, 0.70, 0]} s={[0.08, 0.88, 0.08]} color="#9aaab8" rough={0.28} metal={0.82} />
      {/* Counter-balance arm */}
      <Box p={[0.42, 0.62, 0]} s={[0.7, 0.055, 0.055]} color="#9aaab8" rough={0.28} metal={0.82} />
      <Box p={[0.78, 0.52, 0]} s={[0.055, 0.22, 0.055]} color="#9aaab8" rough={0.28} metal={0.82} />
      <Sph p={[0.78, 0.40, 0]} r={0.07} color="#b0c4cc" rough={0.3} metal={0.75} />
      {/* Microscope body */}
      <Box p={[-0.12, 1.18, 0]} s={[0.2, 0.42, 0.2]} color="#2a3848" rough={0.4} metal={0.6} />
      {/* Objective lenses */}
      <Cyl p={[-0.12, 0.94, 0]} r={0.09} h={0.18} color="#1a2838" rough={0.3} metal={0.6} />
      <Cyl p={[-0.12, 0.82, 0]} r={0.11} h={0.06} top={0.09} color="#2a3848" rough={0.4} metal={0.5} />
      {/* Pulsing illumination ring */}
      <mesh position={[-0.12, 0.88, 0]} castShadow>
        <cylinderGeometry args={[0.12, 0.12, 0.025, 20]} />
        <meshStandardMaterial ref={ringMatRef}
          color={isOn ? '#fffce8' : '#111'}
          emissive={isOn ? '#fffce8' : '#000'}
          emissiveIntensity={0}
          roughness={0.05} metalness={0.05}
        />
      </mesh>
      {/* Binocular head */}
      <Box p={[-0.12, 1.42, 0]} s={[0.24, 0.14, 0.18]} color="#1a2838" rough={0.3} metal={0.5} />
      {/* Left eyepiece */}
      <Cyl p={[-0.06, 1.52, 0.06]} r={0.03} h={0.12} color="#2a3848" rough={0.4} metal={0.5} />
      {/* Right eyepiece */}
      <Cyl p={[-0.18, 1.52, 0.06]} r={0.03} h={0.12} color="#2a3848" rough={0.4} metal={0.5} />
      {/* Optical lens (emissive blue) */}
      <Cyl p={[-0.12, 0.83, 0]} r={0.07} h={0.01} segs={18}
        color={isOn ? '#224488' : '#0a0a14'} rough={0.05} metal={0.1}
        emissive={isOn ? '#3366cc' : '#000'} emissiveIntensity={isOn ? 0.8 : 0} />
    </group>
  )
}

export function Ultrasound({ isOn }) {
  return (
    <group>
      <Wheels4 y={0.055} span={0.26} depth={0.2} />
      <Box p={[0, 0.62, 0]} s={[0.62, 1.12, 0.52]} color="#c0ccd4" rough={0.28} metal={0.72} />
      {/* Keyboard area */}
      <Box p={[0, 0.38, 0.27]} s={[0.56, 0.28, 0.01]} color="#1a2838" rough={0.7} metal={0.1} />
      {/* Trackball */}
      <Sph p={[0.18, 0.4, 0.28]} r={0.04} color="#668898" rough={0.4} metal={0.5} />
      {/* Monitor arm */}
      <Cyl p={[0, 1.24, 0]} r={0.022} h={0.28} color="#888" rough={0.3} metal={0.8} />
      <Box p={[0, 1.40, 0.18]} s={[0.55, 0.42, 0.06]} color="#1a2030" rough={0.2} metal={0.3} />
      <Screen p={[0, 1.40, 0.21]} w={0.49} h={0.36} isOn={isOn} color="#88ccff" />
      {/* Probe holder */}
      <Box p={[-0.34, 0.80, 0]} s={[0.045, 0.44, 0.045]} color="#9aaab8" rough={0.3} metal={0.7} />
      <Cyl p={[-0.34, 0.55, 0.0]} r={0.032} h={0.14} rot={[Math.PI/4,0,0]} color="#2a3848" rough={0.5} metal={0.4} />
      {/* Status LEDs */}
      {isOn && [[-0.2,1.54,0.21],[0,1.54,0.21],[0.2,1.54,0.21]].map(([x,y,z],i) => (
        <Sph key={i} p={[x,y,z]} r={0.014} color={i===0?'#00ff88':i===1?'#00ccff':'#ffcc00'} rough={0.05} metal={0} />
      ))}
    </group>
  )
}

export function NerveMonitor({ isOn }) {
  return (
    <group>
      <Wheels4 y={0.04} span={0.18} depth={0.14} />
      <Box p={[0, 0.32, 0]} s={[0.48, 0.56, 0.40]} color="#d4dce0" rough={0.28} metal={0.68} />
      <Screen p={[0, 0.44, 0.21]} w={0.36} h={0.32} isOn={isOn} color="#00ff88" />
      {/* Multiple electrode channel ports */}
      {[-0.16,-0.08,0,0.08,0.16].map((x,i) => (
        <Cyl key={i} p={[x, 0.14, 0.21]} r={0.015} h={0.015} rot={[Math.PI/2,0,0]}
          color={['#ee4444','#ee8800','#eeee00','#44ee44','#4444ee'][i]} rough={0.4} metal={0.5} />
      ))}
      <Box p={[0, 0.16, 0.21]} s={[0.4, 0.04, 0.01]} color="#1a2838" rough={0.8} metal={0.05} />
      {/* Speaker/audio output */}
      <Cyl p={[0.17, 0.58, 0.21]} r={0.04} h={0.01} segs={10} rot={[Math.PI/2,0,0]} color="#1a2838" rough={0.9} metal={0.1} />
      {/* Brand plate top */}
      <Box p={[0, 0.58, 0.21]} s={[0.28, 0.04, 0.01]} color="#2a4040" rough={0.7} metal={0.3} />
      {isOn && <Sph p={[0.19, 0.44, 0.21]} r={0.015} color="#00ff44" rough={0.05} metal={0} />}
    </group>
  )
}

export function EchoUnit({ isOn }) {
  return (
    <group>
      <Wheels4 y={0.055} span={0.26} depth={0.2} />
      <Box p={[0, 0.62, 0]} s={[0.68, 1.12, 0.56]} color="#c0ccd4" rough={0.28} metal={0.72} />
      {/* Main screen arm + monitor */}
      <Cyl p={[0, 1.24, 0]} r={0.025} h={0.28} color="#888" rough={0.3} metal={0.8} />
      <Box p={[0, 1.44, 0.2]} s={[0.58, 0.46, 0.065]} color="#1a2030" rough={0.2} metal={0.35} />
      <Screen p={[0, 1.45, 0.235]} w={0.52} h={0.40} isOn={isOn} color="#ff8844" />
      {/* Keyboard/panel */}
      <Box p={[0, 0.42, 0.29]} s={[0.6, 0.32, 0.01]} color="#1c2838" rough={0.7} metal={0.1} />
      {/* ECG connector strip */}
      {[-0.22,-0.11,0,0.11,0.22].map((x,i) => (
        <Cyl key={i} p={[x, 0.28, 0.29]} r={0.014} h={0.012} rot={[Math.PI/2,0,0]}
          color={['#ee4444','#ee8800','#eeee00','#44ee44','#4444ee'][i]} rough={0.4} metal={0.5} />
      ))}
      {/* TEE probe holder */}
      <Cyl p={[-0.4, 0.72, 0]} r={0.022} h={0.06} rot={[0,0,Math.PI/2]} color="#9ab0b8" rough={0.3} metal={0.75} />
      {isOn && <Sph p={[0.26, 1.56, 0.235]} r={0.016} color="#00ff88" rough={0.05} metal={0} />}
    </group>
  )
}

export function InfusionPump({ isOn }) {
  return (
    <group>
      {/* Base */}
      <Box p={[0, 0.03, 0]} s={[0.44, 0.05, 0.44]} color="#8090a0" rough={0.3} metal={0.85} />
      <Wheels4 y={0.03} span={0.2} depth={0.2} />
      {/* IV pole */}
      <Cyl p={[0, 0.92, 0]} r={0.022} h={1.72} color="#b0bcc8" rough={0.25} metal={0.88} />
      {/* Top hooks */}
      <Box p={[0, 1.78, 0]} rot={[0,0,Math.PI/2]} s={[0.024, 0.3, 0.024]} color="#c0bcc8" rough={0.3} metal={0.88} />
      <Cyl p={[-0.14, 1.78, 0]} r={0.012} h={0.04} rot={[Math.PI/2,0,0]} color="#c0bcc8" rough={0.3} metal={0.88} />
      <Cyl p={[0.14, 1.78, 0]} r={0.012} h={0.04} rot={[Math.PI/2,0,0]} color="#c0bcc8" rough={0.3} metal={0.88} />
      {/* Pump modules (2 stacked) */}
      {[0.96, 1.3].map((y, i) => (
        <group key={i} position={[0.12, y, 0]}>
          <Box p={[0,0,0]} s={[0.26, 0.26, 0.2]} color="#c8d4d8" rough={0.3} metal={0.65} />
          <Screen p={[0,0.06,0.11]} w={0.18} h={0.12} isOn={isOn} color="#00ff88" />
          {/* Door hinge */}
          <Box p={[-0.13,0,0.06]} s={[0.01,0.22,0.04]} color="#9aabb8" rough={0.3} metal={0.7} />
        </group>
      ))}
    </group>
  )
}

export function ArthroscopyTower({ isOn }) {
  // Similar to laparoscopy tower but with arthroscope pump
  return (
    <group>
      <Wheels4 y={0.055} span={0.3} depth={0.25} />
      <Box p={[0, 0.88, 0]} s={[0.08, 1.62, 0.08]} color="#787888" rough={0.3} metal={0.8} />
      <Box p={[0.3, 0.88, 0]} s={[0.08, 1.62, 0.08]} color="#787888" rough={0.3} metal={0.8} />
      <Box p={[-0.3, 0.88, 0]} s={[0.08, 1.62, 0.08]} color="#787888" rough={0.3} metal={0.8} />
      {/* Shaver/pump unit */}
      <Box p={[0, 0.36, 0]} s={[0.66, 0.18, 0.54]} color="#c4d0d8" rough={0.3} metal={0.7} />
      <Screen p={[0, 0.36, 0.28]} w={0.4} h={0.12} isOn={isOn} color="#44ddff" />
      {/* Light source */}
      <Box p={[0, 0.66, 0]} s={[0.66, 0.18, 0.54]} color="#b8c8d0" rough={0.3} metal={0.7} />
      <Box p={[-0.16, 0.66, 0.28]} s={[0.18, 0.1, 0.01]}
        color={isOn ? '#ffffc0' : '#111'} rough={0.1} metal={0.05}
        emissive={isOn ? '#ffffc0' : '#000'} emissiveIntensity={isOn ? 1.8 : 0} />
      {/* Camera unit */}
      <Box p={[0, 0.96, 0]} s={[0.66, 0.2, 0.54]} color="#b0bcc8" rough={0.3} metal={0.7} />
      <Screen p={[0, 0.96, 0.28]} w={0.52} h={0.14} isOn={isOn} color="#ffcc00" />
      {/* Main monitor */}
      <Cyl p={[0, 1.46, 0]} r={0.025} h={0.22} color="#888" rough={0.3} metal={0.8} />
      <Box p={[0, 1.62, 0.14]} s={[0.66, 0.5, 0.055]} color="#1a2030" rough={0.2} metal={0.3} />
      <Screen p={[0, 1.62, 0.17]} w={0.60} h={0.44} isOn={isOn} color="#88ffaa" />
    </group>
  )
}

export function GenericMachine({ isOn, color = '#00aaff' }) {
  return (
    <group>
      <Wheels4 y={0.055} span={0.24} depth={0.2} />
      <Box p={[0, 0.68, 0]} s={[0.62, 1.24, 0.52]} color="#b8c8cc" rough={0.28} metal={0.72} />
      <Box p={[0, 0.68, 0.27]} s={[0.58, 1.2, 0.01]} color="#1c2838" rough={0.8} metal={0.05} />
      <Screen p={[0, 0.82, 0.27]} w={0.44} h={0.36} isOn={isOn} color={color} />
      {[-0.2,-0.06,0.08,0.22].map((x,i) => (
        <Cyl key={i} p={[x, 0.46, 0.28]} r={0.03} h={0.022} rot={[Math.PI/2,0,0]} color="#4a6a7a" rough={0.4} metal={0.7} />
      ))}
      {[0.16,0.22,0.28].map((y,i) => (
        <Sph key={i} p={[-0.24, y, 0.28]} r={0.016}
          color={isOn ? (i===0?'#00ff88':i===1?'#ffcc00':'#00ccff') : '#1a2838'}
          rough={0.05} metal={0} />
      ))}
      <Box p={[0, 1.22, 0.27]} s={[0.38, 0.04, 0.01]} color="#2a4050" rough={0.7} metal={0.3} />
    </group>
  )
}

//  Machine model selector 
export function getMachineModel(name, isOn, color) {
  const n = name.toLowerCase()
  if (n.includes('anesthesia'))                                   return <AnesthesiaMachine isOn={isOn} />
  if (n.includes('ventilator'))                                   return <Ventilator isOn={isOn} />
  if (n.includes('monitor') && !n.includes('nerve'))             return <PatientMonitor isOn={isOn} />
  if (n.includes('bypass') || n.includes('cardiopulmonary') || n.includes('heart-lung') || n.includes('perfusion')) return <HeartLungMachine isOn={isOn} />
  if (n.includes('defibrillator') || n.includes('aed'))           return <Defibrillator isOn={isOn} />
  if (n.includes('electrocautery') || n.includes('esu') || n.includes('electrosurgical') || n.includes('ligasure') || n.includes('vessel sealer') || n.includes('diathermy')) return <ESU isOn={isOn} />
  if (n.includes('suction'))                                      return <SuctionDevice isOn={isOn} />
  if (n.includes('warming') || n.includes('blanket'))            return <WarmingBlanket isOn={isOn} />
  if (n.includes('instrument table') || n.includes('mayo'))      return <InstrumentTable isOn={isOn} />
  if (n.includes('cell saver'))                                   return <CellSaver isOn={isOn} />
  if (n.includes('blood warmer'))                                 return <BloodWarmer isOn={isOn} />
  if (n.includes('balloon pump') || n.includes('iabp') || n.includes('intra-aortic')) return <IABPump isOn={isOn} />
  if (n.includes('laparoscopy') || n.includes('laparoscopic tower')) return <LaparoscopyTower isOn={isOn} />
  if (n.includes('insufflator') || n.includes('co2'))            return <CO2Insufflator isOn={isOn} />
  if (n.includes('c-arm') || n.includes('fluoroscopy') || n.includes('cholangiography') || n.includes('x-ray')) return <CArm isOn={isOn} />
  if (n.includes('microscope'))                                   return <Microscope isOn={isOn} />
  if (n.includes('ultrasound') || n.includes('echo') || n.includes('transesophageal') || n.includes('tee')) return <EchoUnit isOn={isOn} />
  if (n.includes('nerve') || n.includes('neuro monitor') || n.includes('emg')) return <NerveMonitor isOn={isOn} />
  if (n.includes('infusion pump'))                               return <InfusionPump isOn={isOn} />
  if (n.includes('arthroscop'))                                  return <ArthroscopyTower isOn={isOn} />
  return <GenericMachine isOn={isOn} color={color} />
}

//  OR Personnel 
function HumanFigure({ scrubsColor = '#2a6070', role = 'surgeon', facing = 0 }) {
  const torsoRef    = useRef()
  const headRef     = useRef()
  const leftArmRef  = useRef()
  const rightArmRef = useRef()

  useFrame(() => {
    const t = Date.now() * 0.001
    if (role === 'surgeon') {
      if (torsoRef.current)    torsoRef.current.rotation.x    = 0.18 + 0.04 * Math.sin(t * 0.42)
      if (rightArmRef.current) {
        rightArmRef.current.rotation.x = -0.35 + 0.22 * Math.sin(t * 1.3)
        rightArmRef.current.rotation.z = -0.14 + 0.08 * Math.sin(t * 0.9)
      }
      if (leftArmRef.current) {
        leftArmRef.current.rotation.x = -0.28 + 0.16 * Math.sin(t * 1.1 + 0.7)
        leftArmRef.current.rotation.z =  0.13 - 0.07 * Math.sin(t * 1.0)
      }
    } else if (role === 'assistant') {
      if (torsoRef.current)    torsoRef.current.rotation.x    = 0.12 + 0.03 * Math.sin(t * 0.35)
      if (rightArmRef.current) {
        rightArmRef.current.rotation.x = -0.20 + 0.14 * Math.sin(t * 1.0 + 1.0)
        rightArmRef.current.rotation.z = -0.10 + 0.06 * Math.sin(t * 0.8)
      }
      if (leftArmRef.current)  leftArmRef.current.rotation.x  = -0.18 + 0.12 * Math.sin(t * 0.9 + 0.4)
    } else if (role === 'anesthesiologist') {
      if (rightArmRef.current) {
        rightArmRef.current.rotation.x = -0.45 + 0.28 * Math.sin(t * 0.55)
        rightArmRef.current.rotation.y =  0.15 * Math.sin(t * 0.42)
      }
      if (leftArmRef.current)  leftArmRef.current.rotation.x  = -0.22 + 0.10 * Math.sin(t * 0.6 + 0.8)
      if (headRef.current)     headRef.current.rotation.y     =  0.22 * Math.sin(t * 0.28)
    } else {
      // scrub nurse
      if (torsoRef.current)    torsoRef.current.rotation.y    =  0.18 * Math.sin(t * 0.3)
      if (rightArmRef.current) {
        rightArmRef.current.rotation.x = -0.22 + 0.25 * Math.sin(t * 0.9)
        rightArmRef.current.rotation.z = -0.20 + 0.12 * Math.sin(t * 0.7)
      }
      if (leftArmRef.current) {
        leftArmRef.current.rotation.x  = -0.15 + 0.20 * Math.sin(t * 0.8 + 0.5)
        leftArmRef.current.rotation.z  =  0.18 - 0.09 * Math.sin(t * 0.6)
      }
    }
  })

  const skinColor  = '#d4a882'
  const gloveColor = '#c8d4b0'
  const maskColor  = '#88b0c8'
  const shoeColor  = '#1a1a1a'

  return (
    <group rotation={[0, facing, 0]}>
      {/* Shoes */}
      <Box p={[-0.09, 0.05, 0.06]} s={[0.09, 0.08, 0.20]} color={shoeColor} rough={0.9} metal={0.0} />
      <Box p={[ 0.09, 0.05, 0.06]} s={[0.09, 0.08, 0.20]} color={shoeColor} rough={0.9} metal={0.0} />
      {/* Lower legs */}
      <Cyl p={[-0.09, 0.37, 0.02]} r={0.055} h={0.52} color={scrubsColor} rough={0.85} metal={0.0} />
      <Cyl p={[ 0.09, 0.37, 0.02]} r={0.055} h={0.52} color={scrubsColor} rough={0.85} metal={0.0} />
      {/* Upper legs */}
      <Cyl p={[-0.09, 0.74, 0]} r={0.066} h={0.44} color={scrubsColor} rough={0.85} metal={0.0} />
      <Cyl p={[ 0.09, 0.74, 0]} r={0.066} h={0.44} color={scrubsColor} rough={0.85} metal={0.0} />
      {/* Animated torso group (leans forward) */}
      <group ref={torsoRef}>
        <Box p={[0, 1.14, 0]} s={[0.30, 0.52, 0.20]} color={scrubsColor} rough={0.85} metal={0.0} />
        {/* Surgical gown overlay */}
        <Box p={[0, 1.14, 0.01]} s={[0.28, 0.50, 0.19]} color="#e0ecf0" rough={0.90} metal={0.0} transparent={true} opacity={0.85} />
        {/* Neck */}
        <Cyl p={[0, 1.44, 0]} r={0.048} h={0.10} color={skinColor} rough={0.7} metal={0.0} />
        {/* Animated head group (turns for anesthesiologist) */}
        <group ref={headRef} position={[0, 1.44, 0]}>
          <Sph p={[0, 0.15, 0]} r={0.115} color={skinColor} rough={0.7} metal={0.0} />
          {/* Surgical cap */}
          <mesh position={[0, 0.23, 0]} castShadow>
            <sphereGeometry args={[0.118, 12, 8, 0, Math.PI * 2, 0, Math.PI * 0.54]} />
            <meshStandardMaterial color={scrubsColor} roughness={0.85} metalness={0.0} />
          </mesh>
          {/* Surgical mask */}
          <mesh position={[0, 0.11, 0.10]} castShadow>
            <sphereGeometry args={[0.1, 10, 8, 0, Math.PI * 2, Math.PI * 0.48, Math.PI * 0.38]} />
            <meshStandardMaterial color={maskColor} roughness={0.7} metalness={0.0} />
          </mesh>
          {/* Eyes */}
          <Sph p={[-0.040, 0.160, 0.105]} r={0.016} color="#2a2020" rough={0.5} metal={0.0} />
          <Sph p={[ 0.040, 0.160, 0.105]} r={0.016} color="#2a2020" rough={0.5} metal={0.0} />
        </group>
        {/* Animated LEFT arm - pivots at shoulder joint */}
        <group ref={leftArmRef} position={[-0.20, 1.25, 0]}>
          <Cyl p={[0, -0.19, 0]} r={0.052} h={0.30} rot={[0, 0, Math.PI * 0.06]} color={scrubsColor} rough={0.85} metal={0.0} />
          <Cyl p={[-0.038, -0.44, 0.09]} r={0.044} h={0.26} rot={[-Math.PI * 0.28, 0, Math.PI * 0.04]} color={scrubsColor} rough={0.85} metal={0.0} />
          <Sph p={[-0.066, -0.58, 0.17]} r={0.055} color={gloveColor} rough={0.6} metal={0.0} />
        </group>
        {/* Animated RIGHT arm - pivots at shoulder joint */}
        <group ref={rightArmRef} position={[0.20, 1.25, 0]}>
          <Cyl p={[0, -0.19, 0]} r={0.052} h={0.30} rot={[0, 0, -Math.PI * 0.06]} color={scrubsColor} rough={0.85} metal={0.0} />
          <Cyl p={[0.038, -0.44, 0.09]} r={0.044} h={0.26} rot={[-Math.PI * 0.28, 0, -Math.PI * 0.04]} color={scrubsColor} rough={0.85} metal={0.0} />
          <Sph p={[0.066, -0.58, 0.17]} r={0.055} color={gloveColor} rough={0.6} metal={0.0} />
        </group>
      </group>
    </group>
  )
}

export function SurgeonFigure({ position, rotation }) {
  return <group position={position} rotation={rotation}><HumanFigure scrubsColor="#2a6878" role="surgeon" /></group>
}
export function AssistantFigure({ position, rotation }) {
  return <group position={position} rotation={rotation}><HumanFigure scrubsColor="#2a5060" role="assistant" /></group>
}
export function AnesthesiologistFigure({ position, rotation }) {
  return <group position={position} rotation={rotation}><HumanFigure scrubsColor="#2a3870" role="anesthesiologist" /></group>
}
export function ScrubNurseFigure({ position, rotation }) {
  return <group position={position} rotation={rotation}><HumanFigure scrubsColor="#3a7060" role="nurse" /></group>
}

export function ORPersonnel() {
  return (
    <>
      {/* Surgeon - right side of table, facing across */}
      <SurgeonFigure position={[1.15, 0, -0.1]} rotation={[0, -Math.PI / 2, 0]} />
      {/* Assistant surgeon - left side, facing across */}
      <AssistantFigure position={[-1.15, 0, -0.1]} rotation={[0, Math.PI / 2, 0]} />
      {/* Anesthesiologist - at head of table */}
      <AnesthesiologistFigure position={[0.6, 0, 2.2]} rotation={[0, Math.PI, 0]} />
      {/* Scrub nurse - near instrument side */}
      <ScrubNurseFigure position={[1.6, 0, -1.8]} rotation={[0, -Math.PI * 0.65, 0]} />
    </>
  )
}

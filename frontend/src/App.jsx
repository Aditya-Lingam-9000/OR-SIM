/**
 * App.jsx
 * Root component — assembles the full OR-SIM UI:
 *
 *  ┌──────────────────────────────────────────────────────┐
 *  │ [SurgerySelector]                    [StatusPanel]   │
 *  │                                                      │
 *  │              3D ORRoom (full screen)                 │
 *  │                                                      │
 *  │       [TranscriptionBar ─────────────────────]       │
 *  └──────────────────────────────────────────────────────┘
 */
import React, { Suspense } from 'react'
import { useORWebSocket }   from './hooks/useORWebSocket'
import { useMachineStore }  from './store/machineStore'
import SurgerySelector      from './components/SurgerySelector'
import TranscriptionBar     from './components/TranscriptionBar'
import ORRoom               from './components/ORRoom'

// ── Machine status sidebar ─────────────────────────────────────────────────
function StatusPanel() {
  const machinesOn  = useMachineStore((s) => s.machinesOn)
  const machinesOff = useMachineStore((s) => s.machinesOff)
  const surgery     = useMachineStore((s) => s.surgery)

  if (!surgery) return null

  return (
    <div style={{
      position: 'absolute', top: 16, right: 16, zIndex: 100,
      background: 'rgba(10,14,26,0.92)',
      border: '1px solid rgba(0,200,255,0.2)',
      borderRadius: 12, padding: '14px 18px',
      width: 230, backdropFilter: 'blur(8px)',
      boxShadow: '0 4px 32px rgba(0,0,0,0.5)',
      maxHeight: 'calc(100vh - 32px)',
      overflowY: 'auto',
    }}>
      <div style={{ fontSize: 10, letterSpacing: 2, color: '#00c8ff', textTransform: 'uppercase', marginBottom: 10 }}>
        Machine States
      </div>

      {machinesOn.length > 0 && (
        <>
          <div style={{ fontSize: 10, color: '#00ff88', marginBottom: 4, letterSpacing: 1 }}>● ON</div>
          {machinesOn.map(m => (
            <div key={m} style={{
              fontSize: 12, color: '#aaffcc', padding: '3px 8px', marginBottom: 2,
              background: 'rgba(0,255,136,0.07)', borderRadius: 4,
              borderLeft: '2px solid #00ff88',
            }}>
              {m}
            </div>
          ))}
        </>
      )}

      {machinesOff.length > 0 && (
        <>
          <div style={{ fontSize: 10, color: '#3a5060', marginTop: 8, marginBottom: 4, letterSpacing: 1 }}>● OFF</div>
          {machinesOff.map(m => (
            <div key={m} style={{
              fontSize: 11, color: '#2a4050', padding: '2px 8px', marginBottom: 2,
            }}>
              {m}
            </div>
          ))}
        </>
      )}
    </div>
  )
}

// ── Loading fallback ───────────────────────────────────────────────────────
function SceneLoader() {
  return (
    <div style={{
      width: '100%', height: '100%', display: 'flex',
      alignItems: 'center', justifyContent: 'center',
      flexDirection: 'column', gap: 12,
    }}>
      <div style={{ fontSize: 28 }}>🏥</div>
      <div style={{ color: '#00c8ff', fontSize: 13, letterSpacing: 2 }}>LOADING OR ROOM…</div>
    </div>
  )
}

// ── App ───────────────────────────────────────────────────────────────────
export default function App() {
  // Establish WebSocket connection on mount
  useORWebSocket()

  return (
    <div style={{ width: '100vw', height: '100vh', position: 'relative', background: '#0a0e1a' }}>
      {/* 3D scene — full screen */}
      <Suspense fallback={<SceneLoader />}>
        <ORRoom />
      </Suspense>

      {/* Overlays */}
      <SurgerySelector />
      <StatusPanel />
      <TranscriptionBar />
    </div>
  )
}

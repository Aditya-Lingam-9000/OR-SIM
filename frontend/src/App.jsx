/**
 * App.jsx
 * Root component — OR-SIM full UI
 */
import React, { Suspense } from 'react'
import { useORWebSocket }  from './hooks/useORWebSocket'
import { useMachineStore } from './store/machineStore'
import SurgerySelector     from './components/SurgerySelector'
import TranscriptionBar    from './components/TranscriptionBar'
import ORRoom              from './components/ORRoom'

//  Machine status panel 
function StatusPanel() {
  const machinesOn  = useMachineStore((s) => s.machinesOn)
  const machinesOff = useMachineStore((s) => s.machinesOff)
  const surgery     = useMachineStore((s) => s.surgery)

  if (!surgery) return null

  return (
    <div style={{
      position: 'absolute', top: 16, right: 16, zIndex: 100,
      width: 240,
      background: 'linear-gradient(145deg, rgba(8,14,28,0.97), rgba(10,18,32,0.97))',
      border: '1px solid rgba(0,200,255,0.22)',
      borderRadius: 14, padding: '14px 16px',
      backdropFilter: 'blur(12px)',
      boxShadow: '0 8px 40px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.04)',
      maxHeight: 'calc(100vh - 32px)', overflowY: 'auto',
      fontFamily: 'Segoe UI, system-ui, sans-serif',
    }}>
      <style>{`
        @keyframes glow-pulse {
          0%,100% { box-shadow: -2px 0 0 #00ff88, 0 0 6px rgba(0,255,136,0.2); }
          50%      { box-shadow: -2px 0 0 #00ff88, 0 0 14px rgba(0,255,136,0.45); }
        }
        .on-machine { animation: glow-pulse 2.2s ease-in-out infinite; }
      `}</style>

      <div style={{
        fontSize: 10, letterSpacing: 2.5, color: '#00c8ff',
        textTransform: 'uppercase', marginBottom: 12,
        display: 'flex', alignItems: 'center', gap: 8,
      }}>
        <span style={{
          width: 6, height: 6, borderRadius: '50%',
          background: '#00c8ff', boxShadow: '0 0 6px #00c8ff',
          display: 'inline-block', flexShrink: 0,
        }} />
        Machine States
      </div>

      {machinesOn.length > 0 && (
        <div style={{ marginBottom: 8 }}>
          <div style={{
            fontSize: 9.5, letterSpacing: 1.5, color: '#00ff88',
            textTransform: 'uppercase', marginBottom: 6,
            display: 'flex', alignItems: 'center', gap: 6,
          }}>
            <span style={{
              width: 5, height: 5, borderRadius: '50%',
              background: '#00ff88', boxShadow: '0 0 5px #00ff88',
              display: 'inline-block',
            }} />
            Active ({machinesOn.length})
          </div>
          {machinesOn.map(m => (
            <div key={m} className="on-machine" style={{
              fontSize: 11.5, color: '#b0ffcc',
              padding: '4px 10px 4px 12px', marginBottom: 3,
              background: 'rgba(0,255,136,0.07)',
              borderRadius: 6, borderLeft: '2px solid #00ff88',
              fontWeight: 600,
            }}>
              {m}
            </div>
          ))}
        </div>
      )}

      {machinesOff.length > 0 && (
        <div>
          <div style={{
            fontSize: 9.5, letterSpacing: 1.5, color: '#2a4050',
            textTransform: 'uppercase', marginBottom: 6,
            display: 'flex', alignItems: 'center', gap: 6,
          }}>
            <span style={{
              width: 5, height: 5, borderRadius: '50%',
              background: '#2a4050', display: 'inline-block',
            }} />
            Standby ({machinesOff.length})
          </div>
          {machinesOff.map(m => (
            <div key={m} style={{
              fontSize: 11, color: '#2d4054',
              padding: '3px 10px 3px 12px', marginBottom: 2,
              borderLeft: '2px solid #1a2a3a',
            }}>
              {m}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

//  Loading fallback 
function SceneLoader() {
  return (
    <div style={{
      width: '100%', height: '100%',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      flexDirection: 'column', gap: 14,
      background: 'radial-gradient(ellipse at center, #0c1428 0%, #050a14 100%)',
    }}>
      <div style={{
        width: 56, height: 56, borderRadius: '50%',
        border: '3px solid transparent',
        borderTop: '3px solid #00c8ff',
        borderRight: '3px solid rgba(0,200,255,0.3)',
        animation: 'spin 0.9s linear infinite',
      }} />
      <style>{`@keyframes spin { to { transform: rotate(360deg) } }`}</style>
      <div style={{
        color: '#00c8ff', fontSize: 11,
        letterSpacing: 3, textTransform: 'uppercase',
        fontFamily: 'Segoe UI, system-ui, sans-serif',
      }}>
        Initialising OR Room
      </div>
    </div>
  )
}

//  App 
export default function App() {
  useORWebSocket()

  return (
    <div style={{
      width: '100vw', height: '100vh', position: 'relative',
      background: 'radial-gradient(ellipse at 50% 80%, #0c1830 0%, #070c18 100%)',
      overflow: 'hidden',
    }}>
      <Suspense fallback={<SceneLoader />}>
        <ORRoom />
      </Suspense>

      <SurgerySelector />
      <StatusPanel />
      <TranscriptionBar />
    </div>
  )
}

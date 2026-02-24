/**
 * App.jsx
 * Root component — OR-SIM full UI
 */
import React, { Suspense, useState, useEffect, useRef } from 'react'
import { useORWebSocket }  from './hooks/useORWebSocket'
import { useMachineStore } from './store/machineStore'
import SurgerySelector     from './components/SurgerySelector'
import TranscriptionBar    from './components/TranscriptionBar'
import ORRoom from './components/ORRoom'

// ── "Machine not available" toast notification ────────────────────────────
function UnavailableToast({ items, onDismiss }) {
  if (!items.length) return null
  return (
    <div style={{
      position: 'absolute', bottom: 72, left: '50%',
      transform: 'translateX(-50%)',
      zIndex: 500,
      display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8,
      pointerEvents: 'none',
    }}>
      <style>{`
        @keyframes toast-in  { 0%{opacity:0;transform:translateY(14px) scale(0.92)} 100%{opacity:1;transform:translateY(0) scale(1)} }
        @keyframes toast-out { 0%{opacity:1;transform:scale(1)} 100%{opacity:0;transform:translateY(-8px) scale(0.94)} }
        @keyframes toast-bar { 0%{width:100%} 100%{width:0%} }
        @keyframes toast-warn { 0%,100%{box-shadow:0 0 0 0 rgba(255,160,40,0)} 60%{box-shadow:0 0 0 6px rgba(255,160,40,0.22)} }
      `}</style>
      {items.map(item => (
        <div key={item.id} style={{
          background: 'linear-gradient(135deg, rgba(20,10,4,0.97) 0%, rgba(30,16,4,0.97) 100%)',
          border: '1.5px solid rgba(255,150,30,0.55)',
          borderRadius: 12,
          padding: '10px 18px 14px',
          minWidth: 280, maxWidth: 400,
          boxShadow: '0 8px 32px rgba(0,0,0,0.7), 0 0 0 1px rgba(255,120,0,0.1)',
          animation: (item.leaving ? 'toast-out 0.28s ease-in forwards,' : 'toast-in 0.32s cubic-bezier(0.34,1.4,0.64,1) both,') +
            'toast-warn 2s ease-in-out 0.3s 2',
          pointerEvents: 'auto',
          position: 'relative', overflow: 'hidden',
        }}>
          {/* Header row */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 9, marginBottom: 5 }}>
            {/* Warning icon */}
            <svg width={18} height={18} viewBox="0 0 24 24" fill="none"
              style={{ flexShrink: 0, filter: 'drop-shadow(0 0 4px rgba(255,140,0,0.7))' }}>
              <path d="M12 2L2 20h20L12 2z" fill="rgba(255,140,0,0.15)" stroke="#ff9020" strokeWidth="1.8" strokeLinejoin="round" />
              <line x1="12" y1="9" x2="12" y2="14" stroke="#ffb040" strokeWidth="2" strokeLinecap="round" />
              <circle cx="12" cy="17" r="1" fill="#ffb040" />
            </svg>
            <span style={{
              fontSize: 11, letterSpacing: 2, color: '#ff9020',
              textTransform: 'uppercase', fontWeight: 700,
              fontFamily: 'Segoe UI, system-ui, sans-serif',
            }}>
              Machine Not Available
            </span>
            {/* Dismiss × */}
            <button
              onClick={() => onDismiss(item.id)}
              style={{
                marginLeft: 'auto', background: 'none', border: 'none',
                color: '#5a3a20', cursor: 'pointer', fontSize: 16, lineHeight: 1,
                padding: '0 2px', transition: 'color 0.2s',
              }}
              onMouseEnter={e => e.target.style.color = '#ff9020'}
              onMouseLeave={e => e.target.style.color = '#5a3a20'}
            >×</button>
          </div>

          {/* Machine name */}
          <div style={{
            fontSize: 14, fontWeight: 700, color: '#ffe0b0',
            fontFamily: 'Segoe UI, system-ui, sans-serif',
            letterSpacing: 0.2, marginBottom: 3,
            textShadow: '0 0 12px rgba(255,160,40,0.4)',
          }}>
            “{item.name}”
          </div>
          <div style={{
            fontSize: 11, color: '#7a5030',
            fontFamily: 'Segoe UI, system-ui, sans-serif',
          }}>
            This machine is not part of the current surgery setup.
          </div>

          {/* Auto-dismiss progress bar */}
          <div style={{
            position: 'absolute', bottom: 0, left: 0, height: 2,
            background: 'linear-gradient(90deg, #ff9020, #ffcc60)',
            animation: `toast-bar ${item.duration}ms linear forwards`,
            borderRadius: '0 0 0 12px',
          }} />
        </div>
      ))}
    </div>
  )
}

// ── Collapsible Machine Status Panel ─────────────────────────────────────────
function StatusPanel() {
  const [open, setOpen]    = useState(false)
  const machinesOn  = useMachineStore((s) => s.machinesOn)
  const machinesOff = useMachineStore((s) => s.machinesOff)
  const surgery     = useMachineStore((s) => s.surgery)

  if (!surgery) return null

  const onCount  = machinesOn.length
  const allCount = onCount + machinesOff.length

  return (
    <div style={{ width: 300, fontFamily: 'Segoe UI, system-ui, sans-serif' }}>
      <style>{`
        @keyframes sp-pulse  { 0%,100%{opacity:1;transform:scale(1)}    50%{opacity:0.55;transform:scale(0.92)} }
        @keyframes sp-sweep  { 0%{transform:translateX(-100%)} 100%{transform:translateX(200%)} }
        @keyframes sp-ecg    { 0%{stroke-dashoffset:160} 100%{stroke-dashoffset:0} }
        @keyframes sp-fadein { 0%{opacity:0;transform:translateY(-4px)} 100%{opacity:1;transform:translateY(0)} }
        @keyframes sp-glow   {
          0%,100% { box-shadow: -2px 0 0 #00ff88, 0 0 5px rgba(0,255,136,0.18); }
          50%     { box-shadow: -2px 0 0 #00ff88, 0 0 14px rgba(0,255,136,0.42); }
        }
      `}</style>

      {/* ── Toggle trigger button ── */}
      <button
        onClick={() => setOpen(o => !o)}
        style={{
          display: 'flex', alignItems: 'center', gap: 10,
          width: '100%', padding: '8px 14px',
          background: 'linear-gradient(135deg, rgba(8,14,28,0.97) 0%, rgba(14,24,44,0.97) 100%)',
          border: '1px solid rgba(0,200,255,0.30)',
          borderBottom: open ? '1px solid rgba(0,200,255,0.10)' : '1px solid rgba(0,200,255,0.30)',
          borderRadius: open ? '10px 10px 0 0' : 10,
          backdropFilter: 'blur(12px)',
          boxShadow: open
            ? '0 2px 16px rgba(0,0,0,0.45)'
            : '0 4px 20px rgba(0,0,0,0.50), inset 0 1px 0 rgba(255,255,255,0.04)',
          cursor: 'pointer', outline: 'none',
          overflow: 'hidden', position: 'relative',
          transition: 'border-radius 0.25s, box-shadow 0.25s',
        }}
      >
        {/* Sweep shimmer */}
        <div style={{
          position: 'absolute', top: 0, bottom: 0, width: '45%',
          background: 'linear-gradient(90deg, transparent, rgba(0,200,255,0.07), transparent)',
          animation: 'sp-sweep 3.6s linear infinite',
          pointerEvents: 'none',
        }} />

        {/* ECG heartbeat icon */}
        <svg width={30} height={18} viewBox="0 0 60 24" fill="none"
          style={{ flexShrink: 0, filter: 'drop-shadow(0 0 3px rgba(0,200,255,0.6))' }}>
          <polyline
            points="0,12 10,12 15,3 19,21 24,1 28,21 33,12 60,12"
            stroke="#00c8ff" strokeWidth="2.5"
            strokeLinecap="round" strokeLinejoin="round"
            strokeDasharray="160" strokeDashoffset="0"
            style={{ animation: 'sp-ecg 2.4s linear infinite' }}
          />
        </svg>

        {/* Text info */}
        <div style={{ flex: 1, textAlign: 'left', lineHeight: 1 }}>
          <div style={{ fontSize: 9.5, letterSpacing: 2.5, color: '#00c8ff',
            textTransform: 'uppercase', fontWeight: 700, marginBottom: 2 }}>
            Machine Status
          </div>
          <div style={{ fontSize: 10.5, color: '#3d5a6e' }}>
            <span style={{ color: '#00ff88', fontWeight: 700, fontSize: 12 }}>{onCount}</span>
            <span style={{ color: '#253545' }}>/{allCount}</span>
            <span style={{ color: '#2a4050', marginLeft: 5 }}>active</span>
          </div>
        </div>

        {/* Active count badge */}
        {onCount > 0 && (
          <div style={{
            fontSize: 11, fontWeight: 800, color: '#040c18',
            background: 'linear-gradient(135deg, #00ff88, #00e676)',
            borderRadius: 100, minWidth: 22, height: 22, padding: '0 5px',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 0 12px rgba(0,255,136,0.55)',
            animation: 'sp-pulse 2s ease-in-out infinite',
            flexShrink: 0,
          }}>
            {onCount}
          </div>
        )}

        {/* Animated chevron */}
        <svg width={14} height={14} viewBox="0 0 14 14" fill="none"
          style={{
            flexShrink: 0, marginLeft: 2,
            transform: open ? 'rotate(180deg)' : 'rotate(0deg)',
            transition: 'transform 0.3s cubic-bezier(0.4,0,0.2,1)',
            filter: 'drop-shadow(0 0 2px rgba(0,200,255,0.3))',
          }}>
          <polyline points="2,5 7,10 12,5" stroke="#3a5a70" strokeWidth="2"
            strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </button>

      {/* ── Expandable list ── */}
      <div style={{
        overflow: 'hidden',
        maxHeight: open ? 520 : 0,
        transition: 'max-height 0.38s cubic-bezier(0.4,0,0.2,1)',
      }}>
        <div style={{
          background: 'linear-gradient(180deg, rgba(9,15,30,0.97), rgba(10,18,32,0.97))',
          border: '1px solid rgba(0,200,255,0.16)',
          borderTop: 'none',
          borderRadius: '0 0 10px 10px',
          padding: '10px 14px 12px',
          backdropFilter: 'blur(12px)',
        }}>
          {machinesOn.length > 0 && (
            <div style={{ marginBottom: 8 }}>
              <div style={{
                fontSize: 9, letterSpacing: 1.8, color: '#00c8a0',
                textTransform: 'uppercase', marginBottom: 6,
                display: 'flex', alignItems: 'center', gap: 6,
              }}>
                <span style={{
                  width: 5, height: 5, borderRadius: '50%',
                  background: '#00ff88', boxShadow: '0 0 5px #00ff88',
                  display: 'inline-block',
                  animation: 'sp-pulse 1.6s ease-in-out infinite',
                }} />
                Active ({machinesOn.length})
              </div>
              {machinesOn.map((m, i) => (
                <div key={m} style={{
                  fontSize: 11.5, color: '#a8ffcc',
                  padding: '4px 10px 4px 12px', marginBottom: 3,
                  background: 'rgba(0,255,136,0.065)',
                  borderRadius: 6, borderLeft: '2px solid #00ff88',
                  fontWeight: 600,
                  animation: 'sp-glow 2.2s ease-in-out infinite',
                  animationDelay: `${i * 0.18}s`,
                  animationFillMode: 'both',
                }}>
                  {m}
                </div>
              ))}
            </div>
          )}

          {machinesOff.length > 0 && (
            <div>
              <div style={{
                fontSize: 9, letterSpacing: 1.8, color: '#1e3040',
                textTransform: 'uppercase', marginBottom: 5,
                display: 'flex', alignItems: 'center', gap: 6,
              }}>
                <span style={{
                  width: 5, height: 5, borderRadius: '50%',
                  background: '#1a2a3c', display: 'inline-block',
                }} />
                Standby ({machinesOff.length})
              </div>
              {machinesOff.map(m => (
                <div key={m} style={{
                  fontSize: 10.5, color: '#243444',
                  padding: '3px 10px 3px 12px', marginBottom: 2,
                  borderLeft: '2px solid #162030',
                  letterSpacing: 0.1,
                }}>
                  {m}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
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

  const unavailableMachines = useMachineStore((s) => s.unavailableMachines)

  // ── Unavailable machine toast detection ──────────────────────────────────
  // The backend now populates unavailable_machines directly when a machine
  // command can't be resolved for the active surgery — no frontend diff needed.
  const [toasts, setToasts] = useState([])
  const toastCounterRef     = useRef(0)

  useEffect(() => {
    if (!unavailableMachines.length) return
    const DURATION = 5000
    const newToasts = unavailableMachines.map(name => ({
      id: ++toastCounterRef.current,
      name,
      duration: DURATION,
      leaving: false,
    }))
    setToasts(prev => [...prev, ...newToasts])
    newToasts.forEach(t => {
      setTimeout(() => dismissToast(t.id), DURATION + 100)
    })
  }, [unavailableMachines])

  function dismissToast(id) {
    // Mark as leaving first for exit animation
    setToasts(prev => prev.map(t => t.id === id ? { ...t, leaving: true } : t))
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 300)
  }

  return (
    <div style={{
      width: '100vw', height: '100vh', position: 'relative',
      background: 'radial-gradient(ellipse at 50% 80%, #0c1830 0%, #070c18 100%)',
      overflow: 'hidden',
    }}>
      <Suspense fallback={<SceneLoader />}>
        <ORRoom />
      </Suspense>

      {/* Left sidebar: control panel + collapsible machine status beneath it */}
      <div style={{
        position: 'absolute', top: 16, left: 16, zIndex: 300,
        width: 300,
        display: 'flex', flexDirection: 'column', gap: 8,
        pointerEvents: 'auto',
      }}>
        <SurgerySelector />
        <StatusPanel />
      </div>

      <UnavailableToast items={toasts} onDismiss={dismissToast} />
      <TranscriptionBar />
    </div>
  )
}

/**
 * SurgerySelector.jsx
 * Surgery selection panel + start/stop session controls.
 *
 * On "Start Session" → POST /api/session/start {surgery}
 * On "Stop Session"  → POST /api/session/stop
 */
import React, { useState } from 'react'
import { useMachineStore } from '../store/machineStore'
import { useAudioStreamer } from '../hooks/useAudioStreamer'

const SURGERIES = [
  { key: 'heart',  label: 'Heart Transplantation',           icon: '🫀', fullName: 'Heart Transplantation'  },
  { key: 'liver',  label: 'Liver Resection',                 icon: '🫁', fullName: 'Liver Resection'          },
  { key: 'kidney', label: 'Kidney PCNL (Nephrolithotomy)',   icon: '🫘', fullName: 'Kidney PCNL'              },
]

const styles = {
  panel: {
    position: 'absolute', top: 16, left: 16, zIndex: 100,
    background: 'rgba(10,14,26,0.92)',
    border: '1px solid rgba(0,200,255,0.25)',
    borderRadius: 12, padding: '16px 20px',
    minWidth: 280, backdropFilter: 'blur(8px)',
    boxShadow: '0 4px 32px rgba(0,0,0,0.5)',
  },
  title: {
    fontSize: 11, letterSpacing: 2, color: '#00c8ff',
    textTransform: 'uppercase', marginBottom: 12,
  },
  btn: (active, color = '#00c8ff') => ({
    display: 'flex', alignItems: 'center', gap: 10,
    width: '100%', padding: '9px 14px', marginBottom: 6,
    background: active ? `rgba(${color === '#00c8ff' ? '0,200,255' : '0,255,128'},0.12)` : 'transparent',
    border: `1px solid ${active ? color : 'rgba(255,255,255,0.1)'}`,
    borderRadius: 8, color: active ? color : '#7a8fa8',
    cursor: 'pointer', fontSize: 13, fontFamily: 'inherit',
    transition: 'all 0.15s',
  }),
  actionBtn: (color, disabled) => ({
    width: '100%', padding: '10px 0', marginTop: 10,
    background: disabled ? 'rgba(255,255,255,0.05)' : `rgba(${color},0.15)`,
    border: `1px solid ${disabled ? 'rgba(255,255,255,0.1)' : `rgba(${color},0.5)`}`,
    borderRadius: 8, color: disabled ? '#3a4a5a' : `rgb(${color})`,
    cursor: disabled ? 'not-allowed' : 'pointer',
    fontSize: 13, fontWeight: 600, fontFamily: 'inherit',
    transition: 'all 0.15s',
  }),
}

export default function SurgerySelector() {
  const [selected, setSelected]   = useState('heart')
  const [loading,  setLoading]    = useState(false)
  const sessionActive = useMachineStore((s) => s.sessionActive)
  const setSessionActive = useMachineStore((s) => s.setSessionActive)
  const setSurgery    = useMachineStore((s) => s.setSurgery)

  // Keep the 3D room in sync with the selected surgery even before a session starts
  const selectedSurgery = SURGERIES.find(s => s.key === selected)
  const wsStatus      = useMachineStore((s) => s.wsStatus)

  // Streams mic audio to /ws/audio whenever a session is active.
  // sessionActive drives connect/disconnect automatically.
  const { micStatus } = useAudioStreamer(sessionActive)

  // Support remote backend via VITE_BACKEND_URL (e.g. ngrok URL)
  const API_BASE = import.meta.env.VITE_BACKEND_URL || ''

  async function startSession() {
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/api/session/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ surgery: selected }),
      })
      if (res.ok) {
        const data = await res.json()
        setSurgery(data.surgery)   // backend returns canonical name e.g. "Liver Resection"
        setSessionActive(true)
      }
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  async function stopSession() {
    setLoading(true)
    try {
      await fetch(`${API_BASE}/api/session/stop`, { method: 'POST' })
      setSessionActive(false)
      // Keep surgery set so the correct machine layout stays visible after stopping
      setSurgery(selectedSurgery?.fullName ?? null)
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  const wsColor = wsStatus === 'open' ? '#00ff88' : wsStatus === 'connecting' ? '#ffcc00' : '#ff4466'

  return (
    <div style={styles.panel}>
      <div style={styles.title}>OR-SIM  ·  Surgery Select</div>

      {SURGERIES.map(s => (
        <button
          key={s.key}
          style={styles.btn(selected === s.key)}
          onClick={() => {
            if (!sessionActive) {
              setSelected(s.key)
              setSurgery(s.fullName)  // update 3D room immediately on selection
            }
          }}
        >
          <span>{s.icon}</span>
          <span>{s.label}</span>
        </button>
      ))}

      {!sessionActive ? (
        <button
          style={styles.actionBtn('0,200,255', loading)}
          onClick={startSession}
          disabled={loading}
        >
          {loading ? 'Starting…' : '▶  Start Session'}
        </button>
      ) : (
        <button
          style={styles.actionBtn('255,80,80', loading)}
          onClick={stopSession}
          disabled={loading}
        >
          {loading ? 'Stopping…' : '■  Stop Session'}
        </button>
      )}

      {/* WS status dot */}
      <div style={{ marginTop: 10, fontSize: 11, color: '#3a4a5a', display: 'flex', alignItems: 'center', gap: 6 }}>
        <span style={{ width: 7, height: 7, borderRadius: '50%', background: wsColor, display: 'inline-block' }} />
        WebSocket: {wsStatus}
      </div>

      {/* Mic status — only shown when session is active */}
      {sessionActive && (
        <div style={{ marginTop: 4, fontSize: 11, color: '#3a4a5a', display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{
            width: 7, height: 7, borderRadius: '50%', display: 'inline-block',
            background: micStatus === 'streaming' ? '#00ff88'
                      : micStatus === 'requesting' ? '#ffcc00'
                      : micStatus === 'error'      ? '#ff4466'
                      : '#3a4a5a',
          }} />
          Mic: {micStatus}
        </div>
      )}
    </div>
  )
}

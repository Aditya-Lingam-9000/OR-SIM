/**
 * SurgerySelector.jsx
 * Compact dropdown-style surgery selector + session controls.
 *
 * UI: closed = trigger button (icon + label + chevron)
 *     open  = scrollable dropdown list of all 20 surgeries
 * Click outside to close.
 */
import React, { useState, useEffect, useRef } from 'react'
import { useMachineStore }  from '../store/machineStore'
import { useAudioStreamer } from '../hooks/useAudioStreamer'

const SURGERIES = [
  { key: 'heart',           label: 'Heart Transplantation',           icon: '' },
  { key: 'liver',           label: 'Liver Resection',                 icon: '' },
  { key: 'kidney',          label: 'Kidney PCNL',                     icon: '' },
  { key: 'cabg',            label: 'Coronary Artery Bypass Grafting', icon: '' },
  { key: 'appendectomy',    label: 'Appendectomy',                    icon: '' },
  { key: 'cholecystectomy', label: 'Laparoscopic Cholecystectomy',    icon: '' },
  { key: 'hip',             label: 'Total Hip Replacement',           icon: '' },
  { key: 'knee',            label: 'Total Knee Replacement',          icon: '' },
  { key: 'caesarean',       label: 'Caesarean Section',               icon: '' },
  { key: 'spinal',          label: 'Spinal Fusion',                   icon: '' },
  { key: 'cataract',        label: 'Cataract Surgery',                icon: '\ufe0f' },
  { key: 'hysterectomy',    label: 'Hysterectomy',                    icon: '' },
  { key: 'thyroidectomy',   label: 'Thyroidectomy',                   icon: '' },
  { key: 'colectomy',       label: 'Colectomy',                       icon: '' },
  { key: 'prostatectomy',   label: 'Radical Prostatectomy',           icon: '' },
  { key: 'craniotomy',      label: 'Craniotomy',                      icon: '' },
  { key: 'mastectomy',      label: 'Mastectomy',                      icon: '' },
  { key: 'aortic',          label: 'Aortic Aneurysm Repair',          icon: '' },
  { key: 'gastrectomy',     label: 'Gastrectomy',                     icon: '' },
  { key: 'lobectomy',       label: 'Lung Lobectomy',                  icon: '' },
]

const SURGERY_FULL = {
  heart: 'Heart Transplantation', liver: 'Liver Resection', kidney: 'Kidney PCNL',
  cabg: 'Coronary Artery Bypass Grafting', appendectomy: 'Appendectomy',
  cholecystectomy: 'Laparoscopic Cholecystectomy', hip: 'Total Hip Replacement',
  knee: 'Total Knee Replacement', caesarean: 'Caesarean Section', spinal: 'Spinal Fusion',
  cataract: 'Cataract Surgery', hysterectomy: 'Hysterectomy', thyroidectomy: 'Thyroidectomy',
  colectomy: 'Colectomy', prostatectomy: 'Radical Prostatectomy', craniotomy: 'Craniotomy',
  mastectomy: 'Mastectomy', aortic: 'Aortic Aneurysm Repair', gastrectomy: 'Gastrectomy',
  lobectomy: 'Lung Lobectomy',
}

export default function SurgerySelector() {
  const [selected,  setSelected]  = useState('heart')
  const [isOpen,    setIsOpen]    = useState(false)
  const [loading,   setLoading]   = useState(false)
  const [hovered,   setHovered]   = useState(null)
  const panelRef = useRef(null)

  const sessionActive    = useMachineStore((s) => s.sessionActive)
  const setSessionActive = useMachineStore((s) => s.setSessionActive)
  const setSurgery       = useMachineStore((s) => s.setSurgery)
  const wsStatus         = useMachineStore((s) => s.wsStatus)
  const { micStatus }    = useAudioStreamer(sessionActive)
  const API_BASE         = import.meta.env.VITE_BACKEND_URL || ''

  const current = SURGERIES.find(s => s.key === selected)

  // Close dropdown when clicking outside
  useEffect(() => {
    if (!isOpen) return
    function handler(e) {
      if (panelRef.current && !panelRef.current.contains(e.target)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [isOpen])

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
        setSurgery(data.surgery)
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
      setSurgery(SURGERY_FULL[selected] ?? null)
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  const wsColor = wsStatus === 'open' ? '#00ff88' : wsStatus === 'connecting' ? '#ffcc00' : '#ff4466'

  return (
    <div
      ref={panelRef}
      style={{
        position: 'absolute', top: 16, left: 16, zIndex: 200,
        width: 300,
        fontFamily: 'Segoe UI, system-ui, sans-serif',
      }}
    >
      {/* Panel background */}
      <div style={{
        background: 'linear-gradient(145deg, rgba(8,14,28,0.97), rgba(12,20,36,0.97))',
        border: '1px solid rgba(0,200,255,0.3)',
        borderRadius: 14,
        padding: '14px 16px',
        backdropFilter: 'blur(12px)',
        boxShadow: '0 8px 40px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.05)',
      }}>

        {/* Header */}
        <div style={{
          fontSize: 10, letterSpacing: 2.5, color: '#00c8ff',
          textTransform: 'uppercase', marginBottom: 12,
          display: 'flex', alignItems: 'center', gap: 8,
        }}>
          <span style={{
            width: 6, height: 6, borderRadius: '50%',
            background: '#00c8ff',
            boxShadow: '0 0 6px #00c8ff',
            display: 'inline-block',
          }} />
          OR-SIM Control Panel
        </div>

        {/* Dropdown trigger */}
        <button
          onClick={() => { if (!sessionActive) setIsOpen(o => !o) }}
          disabled={sessionActive}
          style={{
            width: '100%',
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            padding: '10px 14px',
            background: isOpen
              ? 'rgba(0,200,255,0.12)'
              : sessionActive
                ? 'rgba(0,0,0,0.2)'
                : 'rgba(255,255,255,0.06)',
            border: `1px solid ${isOpen ? 'rgba(0,200,255,0.5)' : 'rgba(255,255,255,0.12)'}`,
            borderRadius: isOpen ? '10px 10px 0 0' : 10,
            color: sessionActive ? '#2a4050' : '#d0e8f8',
            cursor: sessionActive ? 'not-allowed' : 'pointer',
            fontSize: 13, fontFamily: 'inherit',
            transition: 'all 0.18s',
          }}
        >
          <span style={{ display: 'flex', alignItems: 'center', gap: 9 }}>
            <span style={{ fontSize: 16 }}>{current?.icon}</span>
            <span style={{ fontWeight: 600 }}>{current?.label}</span>
          </span>
          <span style={{
            fontSize: 10, marginLeft: 6,
            transform: isOpen ? 'rotate(180deg)' : 'none',
            transition: 'transform 0.2s',
            color: '#00c8ff', opacity: sessionActive ? 0.25 : 1,
          }}>
            &#9660;
          </span>
        </button>

        {/* Dropdown list */}
        {isOpen && (
          <div style={{
            borderLeft: '1px solid rgba(0,200,255,0.3)',
            borderRight: '1px solid rgba(0,200,255,0.3)',
            borderBottom: '1px solid rgba(0,200,255,0.3)',
            borderRadius: '0 0 10px 10px',
            maxHeight: 280, overflowY: 'auto',
            background: 'rgba(6,12,24,0.98)',
            animation: 'dropIn 0.14s ease',
          }}>
            <style>{`
              @keyframes dropIn { from { opacity:0; transform:translateY(-6px) } to { opacity:1; transform:none } }
              .or-dd-item:hover { background: rgba(0,200,255,0.1) !important; }
              ::-webkit-scrollbar { width: 4px; }
              ::-webkit-scrollbar-track { background: transparent; }
              ::-webkit-scrollbar-thumb { background: rgba(0,200,255,0.3); border-radius: 2px; }
            `}</style>
            {SURGERIES.map(s => (
              <button
                key={s.key}
                className="or-dd-item"
                onClick={() => {
                  setSelected(s.key)
                  setSurgery(SURGERY_FULL[s.key])
                  setIsOpen(false)
                }}
                style={{
                  display: 'flex', alignItems: 'center', gap: 10,
                  width: '100%', padding: '9px 14px',
                  background: selected === s.key ? 'rgba(0,200,255,0.14)' : 'transparent',
                  border: 'none',
                  borderBottom: '1px solid rgba(255,255,255,0.04)',
                  color: selected === s.key ? '#00c8ff' : '#8ab0c0',
                  cursor: 'pointer', fontSize: 12.5, fontFamily: 'inherit',
                  textAlign: 'left', transition: 'background 0.12s',
                }}
              >
                <span style={{ fontSize: 15, flexShrink: 0 }}>{s.icon}</span>
                <span style={{ fontWeight: selected === s.key ? 600 : 400 }}>{s.label}</span>
                {selected === s.key && (
                  <span style={{ marginLeft: 'auto', color: '#00c8ff', fontSize: 10 }}>&#10003;</span>
                )}
              </button>
            ))}
          </div>
        )}

        {/* Session controls */}
        <div style={{ marginTop: 12 }}>
          {!sessionActive ? (
            <button
              onClick={startSession} disabled={loading}
              style={{
                width: '100%', padding: '10px 0',
                background: loading ? 'rgba(0,0,0,0.2)' : 'rgba(0,200,255,0.15)',
                border: `1px solid ${loading ? 'rgba(255,255,255,0.08)' : 'rgba(0,200,255,0.6)'}`,
                borderRadius: 9, color: loading ? '#2a4050' : '#00c8ff',
                cursor: loading ? 'not-allowed' : 'pointer',
                fontSize: 13, fontWeight: 700, fontFamily: 'inherit',
                boxShadow: loading ? 'none' : '0 0 18px rgba(0,200,255,0.15)',
                transition: 'all 0.18s',
              }}
            >
              {loading ? 'Starting' : '  Start Session'}
            </button>
          ) : (
            <button
              onClick={stopSession} disabled={loading}
              style={{
                width: '100%', padding: '10px 0',
                background: loading ? 'rgba(0,0,0,0.2)' : 'rgba(255,80,80,0.15)',
                border: `1px solid ${loading ? 'rgba(255,255,255,0.08)' : 'rgba(255,80,80,0.6)'}`,
                borderRadius: 9, color: loading ? '#3a2020' : '#ff5050',
                cursor: loading ? 'not-allowed' : 'pointer',
                fontSize: 13, fontWeight: 700, fontFamily: 'inherit',
                boxShadow: loading ? 'none' : '0 0 18px rgba(255,80,80,0.15)',
                transition: 'all 0.18s',
              }}
            >
              {loading ? 'Stopping' : '&#9632;  Stop Session'}
            </button>
          )}
        </div>

        {/* Status indicators */}
        <div style={{ marginTop: 10, display: 'flex', flexDirection: 'column', gap: 4 }}>
          <div style={{ fontSize: 11, color: '#2a4050', display: 'flex', alignItems: 'center', gap: 7 }}>
            <span style={{
              width: 7, height: 7, borderRadius: '50%',
              background: wsColor, display: 'inline-block',
              boxShadow: wsStatus === 'open' ? '0 0 5px #00ff88' : 'none',
            }} />
            <span style={{ color: wsStatus === 'open' ? '#3a6a50' : '#4a3040' }}>
              WebSocket: {wsStatus}
            </span>
          </div>
          {sessionActive && (
            <div style={{ fontSize: 11, color: '#2a4050', display: 'flex', alignItems: 'center', gap: 7 }}>
              <span style={{
                width: 7, height: 7, borderRadius: '50%', display: 'inline-block',
                background: micStatus === 'streaming' ? '#00ff88'
                          : micStatus === 'requesting' ? '#ffcc00'
                          : micStatus === 'error'      ? '#ff4466'
                          : '#3a4a5a',
                boxShadow: micStatus === 'streaming' ? '0 0 5px #00ff88' : 'none',
              }} />
              <span style={{ color: micStatus === 'streaming' ? '#3a6a50' : '#4a3040' }}>
                Mic: {micStatus}
              </span>
            </div>
          )}
        </div>

      </div>
    </div>
  )
}

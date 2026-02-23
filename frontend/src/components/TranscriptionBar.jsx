/**
 * TranscriptionBar.jsx
 * Animated bottom overlay: live transcription + MedGemma reasoning.
 */
import React from 'react'
import { useMachineStore } from '../store/machineStore'

export default function TranscriptionBar() {
  const transcription = useMachineStore((s) => s.transcription)
  const reasoning     = useMachineStore((s) => s.reasoning)

  if (!transcription) return null

  return (
    <div style={{
      position: 'absolute', bottom: 0, left: 0, right: 0, zIndex: 100,
      padding: '18px 28px 22px',
      background: 'linear-gradient(transparent, rgba(4,8,18,0.98) 35%)',
      backdropFilter: 'blur(6px)',
      fontFamily: 'Segoe UI, system-ui, sans-serif',
    }}>
      <style>{`
        @keyframes fadeSlideUp {
          from { opacity: 0; transform: translateY(10px); }
          to   { opacity: 1; transform: translateY(0);    }
        }
        .tb-entry { animation: fadeSlideUp 0.28s ease; }
      `}</style>

      {/* Accent line */}
      <div style={{
        height: 1, marginBottom: 12,
        background: 'linear-gradient(90deg, transparent, rgba(0,200,255,0.25) 40%, transparent)',
      }} />

      {/* Transcription row */}
      <div className="tb-entry" style={{
        display: 'flex', alignItems: 'baseline', gap: 12, marginBottom: 7,
      }}>
        <span style={{
          fontSize: 9.5, letterSpacing: 2.5, color: '#00c8ff',
          textTransform: 'uppercase', whiteSpace: 'nowrap', flexShrink: 0,
          background: 'rgba(0,200,255,0.1)',
          border: '1px solid rgba(0,200,255,0.25)',
          borderRadius: 4, padding: '2px 7px',
        }}>
          HEARD
        </span>
        <span style={{
          fontSize: 15.5, color: '#ddf0ff',
          fontStyle: 'italic', fontWeight: 400,
          textShadow: '0 0 20px rgba(0,200,255,0.2)',
          lineHeight: 1.4,
        }}>
          &ldquo;{transcription}&rdquo;
        </span>
      </div>

      {/* Reasoning row */}
      {reasoning && (
        <div className="tb-entry" style={{
          display: 'flex', alignItems: 'baseline', gap: 12,
        }}>
          <span style={{
            fontSize: 9.5, letterSpacing: 2.5, color: '#00ff88',
            textTransform: 'uppercase', whiteSpace: 'nowrap', flexShrink: 0,
            background: 'rgba(0,255,136,0.08)',
            border: '1px solid rgba(0,255,136,0.22)',
            borderRadius: 4, padding: '2px 7px',
          }}>
            REASON
          </span>
          <span style={{
            fontSize: 13, color: '#80c8a8',
            lineHeight: 1.5,
          }}>
            {reasoning}
          </span>
        </div>
      )}
    </div>
  )
}

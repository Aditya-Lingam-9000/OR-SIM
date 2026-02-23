/**
 * TranscriptionBar.jsx
 * Bottom overlay showing the latest transcription and MedGemma reasoning.
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
      padding: '12px 24px 16px',
      background: 'linear-gradient(transparent, rgba(5,8,18,0.97))',
      backdropFilter: 'blur(4px)',
    }}>
      {/* Transcription */}
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, marginBottom: 4 }}>
        <span style={{
          fontSize: 10, letterSpacing: 2, color: '#00c8ff',
          textTransform: 'uppercase', whiteSpace: 'nowrap', flexShrink: 0,
        }}>🎙 HEARD</span>
        <span style={{ fontSize: 15, color: '#e8f4ff', fontStyle: 'italic', fontWeight: 400 }}>
          "{transcription}"
        </span>
      </div>

      {/* Reasoning */}
      {reasoning && (
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 10 }}>
          <span style={{
            fontSize: 10, letterSpacing: 2, color: '#00ff88',
            textTransform: 'uppercase', whiteSpace: 'nowrap', flexShrink: 0,
          }}>🤖 REASON</span>
          <span style={{ fontSize: 12, color: '#7ab8a0' }}>{reasoning}</span>
        </div>
      )}
    </div>
  )
}

/**
 * useAudioStreamer.js
 *
 * Captures the browser microphone via getUserMedia and streams raw PCM
 * (float32, 16 kHz) to the FastAPI /ws/audio endpoint.
 *
 * The backend receives the PCM, runs it through the VAD state-machine,
 * then MedASR → MedGemma → machine state updates (broadcast over /ws/state).
 *
 * Usage
 * -----
 *   const { micStatus } = useAudioStreamer(sessionActive)
 *
 *   micStatus values:
 *     'idle'        – session not active, hook dormant
 *     'requesting'  – asking browser for mic permission
 *     'streaming'   – mic open, audio flowing to backend
 *     'error'       – mic permission denied or audio context error
 */
import { useEffect, useRef, useState } from 'react'

// Match backend SAMPLE_RATE (backend/asr/utils.py)
const SAMPLE_RATE = 16000

// ScriptProcessorNode buffer: 4096 samples = 256 ms at 16 kHz
// The backend chunks this into 320-sample (20 ms) VAD blocks internally.
const BUFFER_SIZE = 4096

// Build the /ws/audio URL using the same VITE_BACKEND_URL env var as the WS state hook
function buildAudioWsUrl() {
  const backendUrl = import.meta.env.VITE_BACKEND_URL || ''
  if (backendUrl) {
    // Remote backend (ngrok): strip scheme, force wss://
    const host = backendUrl.replace(/^https?:\/\//, '')
    return `wss://${host}/ws/audio`
  }
  // Local dev: use Vite proxy (same host)
  const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
  return `${proto}://${window.location.host}/ws/audio`
}

export function useAudioStreamer(sessionActive) {
  const [micStatus, setMicStatus] = useState('idle')

  const wsRef           = useRef(null)
  const ctxRef          = useRef(null)
  const streamRef       = useRef(null)
  const processorRef    = useRef(null)
  const sourceRef       = useRef(null)
  const reconnectTimerRef = useRef(null)
  const cancelledRef    = useRef(false)

  useEffect(() => {
    if (!sessionActive) {
      cancelledRef.current = true
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current)
        reconnectTimerRef.current = null
      }
      teardown()
      setMicStatus('idle')
      return
    }

    cancelledRef.current = false

    async function start() {
      setMicStatus('requesting')
      try {
        // 1. Request mic permission
        const mediaStream = await navigator.mediaDevices.getUserMedia({
          audio: {
            sampleRate:   SAMPLE_RATE,
            channelCount: 1,
            echoCancellation: true,
            noiseSuppression: true,
          },
          video: false,
        })
        if (cancelledRef.current) { mediaStream.getTracks().forEach(t => t.stop()); return }
        streamRef.current = mediaStream

        // 2. AudioContext at 16 kHz — matches backend SAMPLE_RATE exactly,
        //    so no resampling is needed.
        const ctx = new (window.AudioContext || window.webkitAudioContext)({
          sampleRate: SAMPLE_RATE,
        })
        if (cancelledRef.current) { ctx.close(); mediaStream.getTracks().forEach(t => t.stop()); return }
        ctxRef.current = ctx

        // 3. Build audio graph:  mic source → scriptProcessor
        const source    = ctx.createMediaStreamSource(mediaStream)
        const processor = ctx.createScriptProcessor(BUFFER_SIZE, 1, 1)
        sourceRef.current    = source
        processorRef.current = processor

        // 4. Open WebSocket to /ws/audio
        const wsUrl = buildAudioWsUrl()
        const ws    = new WebSocket(wsUrl)
        ws.binaryType = 'arraybuffer'
        wsRef.current = ws

        ws.onopen = () => {
          if (cancelledRef.current) { ws.close(); return }
          console.log('[OR-SIM] Audio WS open →', wsUrl)

          // Only start sending once the WS is connected
          processor.onaudioprocess = (event) => {
            if (ws.readyState !== WebSocket.OPEN) return
            // getChannelData returns a Float32Array view — slice to get a copy
            const samples = event.inputBuffer.getChannelData(0)
            ws.send(samples.buffer.slice(samples.byteOffset, samples.byteOffset + samples.byteLength))
          }

          // Connect graph AFTER the WS is open to avoid dropping initial frames
          source.connect(processor)
          processor.connect(ctx.destination)   // required by some browsers even when silent
          setMicStatus('streaming')
        }

        ws.onclose = (ev) => {
          console.log('[OR-SIM] Audio WS closed', ev.code, ev.reason)
          if (cancelledRef.current) return   // intentional teardown — stay idle
          // Unexpected close while session is still active → reconnect
          console.log('[OR-SIM] Audio WS dropped unexpectedly — reconnecting in 2 s…')
          setMicStatus('idle')
          teardown()
          reconnectTimerRef.current = setTimeout(() => {
            if (!cancelledRef.current) start()
          }, 2000)
        }

        ws.onerror = (err) => {
          console.warn('[OR-SIM] Audio WS error', err)
          // onclose will fire after onerror, so reconnect is handled there
          setMicStatus('error')
        }

      } catch (err) {
        if (!cancelledRef.current) {
          console.error('[OR-SIM] Mic error:', err)
          setMicStatus('error')
        }
      }
    }

    start()

    return () => {
      cancelledRef.current = true
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current)
        reconnectTimerRef.current = null
      }
      teardown()
    }
  }, [sessionActive]) // eslint-disable-line react-hooks/exhaustive-deps

  function teardown() {
    // Disconnect and close everything in reverse order
    if (processorRef.current) {
      processorRef.current.onaudioprocess = null
      try { processorRef.current.disconnect() } catch (_) {}
      processorRef.current = null
    }
    if (sourceRef.current) {
      try { sourceRef.current.disconnect() } catch (_) {}
      sourceRef.current = null
    }
    if (ctxRef.current) {
      ctxRef.current.close().catch(() => {})
      ctxRef.current = null
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(t => t.stop())
      streamRef.current = null
    }
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
  }

  return { micStatus }
}

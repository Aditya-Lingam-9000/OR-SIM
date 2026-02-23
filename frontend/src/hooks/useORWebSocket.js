/**
 * useORWebSocket.js
 * React hook — manages the WebSocket connection to /ws/state.
 *
 * Behaviour:
 *  - Opens a WebSocket when called (auto-reconnect on close with 2s back-off)
 *  - Maps incoming JSON snapshots → useMachineStore.applySnapshot()
 *  - Exposes wsStatus so the UI can show a connection indicator
 *  - Cleans up on component unmount
 */
import { useEffect, useRef } from 'react'
import { useMachineStore } from '../store/machineStore'

// If VITE_BACKEND_URL is set (e.g. https://xxxx.ngrok-free.app) the WS hook
// connects directly to that host over wss://.  When blank the Vite dev-server
// proxy handles the connection transparently (local / same-host deployments).
const BACKEND_URL     = import.meta.env.VITE_BACKEND_URL || ''
const WS_URL          = BACKEND_URL
  ? BACKEND_URL.replace(/^https?:\/\//, '') // strip scheme, build wss:// below
  : null                                     // null → use window.location.host
const RECONNECT_DELAY = 2000

export function useORWebSocket() {
  const applySnapshot = useMachineStore((s) => s.applySnapshot)
  const setWsStatus   = useMachineStore((s) => s.setWsStatus)
  const wsRef         = useRef(null)
  const timerRef      = useRef(null)
  const unmounted     = useRef(false)

  function connect() {
    if (unmounted.current) return
    setWsStatus('connecting')

    // Remote backend (ngrok): connect directly with wss://
    // Local backend         : connect via Vite proxy (same host)
    const wsUri = WS_URL
      ? `wss://${WS_URL}/ws/state`
      : (() => {
          const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
          return `${proto}://${window.location.host}/ws/state`
        })()
    const ws = new WebSocket(wsUri)
    wsRef.current  = ws

    ws.onopen = () => {
      setWsStatus('open')
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        applySnapshot(data)
      } catch (e) {
        console.warn('OR-SIM WS parse error:', e)
      }
    }

    ws.onerror = () => {
      setWsStatus('error')
    }

    ws.onclose = () => {
      if (!unmounted.current) {
        setWsStatus('closed')
        timerRef.current = setTimeout(connect, RECONNECT_DELAY)
      }
    }
  }

  useEffect(() => {
    unmounted.current = false
    connect()

    return () => {
      unmounted.current = true
      clearTimeout(timerRef.current)
      if (wsRef.current) {
        wsRef.current.onclose = null   // prevent reconnect loop on unmount
        wsRef.current.close()
      }
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps
}

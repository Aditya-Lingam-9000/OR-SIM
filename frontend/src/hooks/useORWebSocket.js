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

const WS_URL          = '/ws/state'   // proxied by Vite to ws://127.0.0.1:8000
const RECONNECT_DELAY = 2000          // ms between reconnect attempts

export function useORWebSocket() {
  const applySnapshot = useMachineStore((s) => s.applySnapshot)
  const setWsStatus   = useMachineStore((s) => s.setWsStatus)
  const wsRef         = useRef(null)
  const timerRef      = useRef(null)
  const unmounted     = useRef(false)

  function connect() {
    if (unmounted.current) return
    setWsStatus('connecting')

    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
    const host     = window.location.host
    const ws       = new WebSocket(`${protocol}://${host}${WS_URL}`)
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

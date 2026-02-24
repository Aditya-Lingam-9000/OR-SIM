/**
 * hooks/use3DHover.js
 *
 * Adds hover-tooltip behaviour to any R3F group or mesh.
 *
 * Rules
 * ─────
 *  • Tooltip appears 1 s after the pointer enters the object.
 *  • Tooltip disappears instantly when the pointer leaves.
 *  • Tooltip auto-dismisses 8 s after it first appears.
 *
 * Usage
 * ─────
 *  const hover = use3DHover({ label, subtitle, description, accentColor })
 *  return <group {...hover}> … </group>
 */
import { useRef } from 'react'
import { useHoverStore } from '../store/hoverStore'

export function use3DHover({
  label,
  subtitle     = '',
  description  = '',
  accentColor  = '#00c8ff',
}) {
  const setHoverInfo   = useHoverStore((s) => s.setHoverInfo)
  const clearHoverInfo = useHoverStore((s) => s.clearHoverInfo)

  const showTimerRef    = useRef(null)
  const dismissTimerRef = useRef(null)

  function onPointerEnter(e) {
    e.stopPropagation()
    document.body.style.cursor = 'crosshair'
    clearTimeout(showTimerRef.current)
    clearTimeout(dismissTimerRef.current)
    showTimerRef.current = setTimeout(() => {
      setHoverInfo({ label, subtitle, description, accentColor })
      dismissTimerRef.current = setTimeout(clearHoverInfo, 8000)
    }, 1000)
  }

  function onPointerLeave(e) {
    e.stopPropagation()
    document.body.style.cursor = ''
    clearTimeout(showTimerRef.current)
    clearTimeout(dismissTimerRef.current)
    clearHoverInfo()
  }

  return { onPointerEnter, onPointerLeave }
}

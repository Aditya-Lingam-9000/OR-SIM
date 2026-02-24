/**
 * hoverStore.js
 * Tiny Zustand store for the 3D-object hover tooltip.
 *
 * hoverInfo shape:
 *   { label: string, subtitle: string, description: string, accentColor: string }
 */
import { create } from 'zustand'

export const useHoverStore = create((set) => ({
  hoverInfo: null,

  setHoverInfo:   (info) => set({ hoverInfo: info }),
  clearHoverInfo: ()     => set({ hoverInfo: null }),
}))

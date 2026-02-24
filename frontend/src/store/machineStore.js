/**
 * machineStore.js
 * Zustand store — single source of truth for OR machine states.
 *
 * Shape:
 *   surgery        : string | null      — active surgery name
 *   machinesOn     : string[]           — canonical names currently ON
 *   machinesOff    : string[]           — canonical names currently OFF
 *   transcription  : string             — latest spoken command
 *   reasoning      : string             — MedGemma reasoning snippet
 *   wsStatus       : 'connecting' | 'open' | 'closed' | 'error'
 *   sessionActive  : boolean
 */
import { create } from 'zustand'

export const useMachineStore = create((set) => ({
  surgery:             null,
  machinesOn:          [],
  machinesOff:         [],
  unavailableMachines: [],
  transcription:       '',
  reasoning:           '',
  wsStatus:            'closed',
  sessionActive:       false,
  isRotating:          false,

  // Called when a WS message arrives with a full state snapshot
  applySnapshot: (snapshot) => set({
    surgery:             snapshot.surgery             ?? null,
    machinesOn:          snapshot.machine_states?.['1'] ?? [],
    machinesOff:         snapshot.machine_states?.['0'] ?? [],
    unavailableMachines: snapshot.unavailable_machines  ?? [],
    transcription:       snapshot.transcription        ?? '',
    reasoning:           snapshot.reasoning            ?? '',
  }),

  setWsStatus:      (s)   => set({ wsStatus: s }),
  setSessionActive: (val) => set({ sessionActive: val }),
  setSurgery:       (s)   => set({ surgery: s }),
  setIsRotating:    (v)   => set({ isRotating: v }),
}))

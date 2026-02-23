/**
 * scenes/HeartTransplantRoom.js
 * Machine layout for Heart Transplantation OR.
 *
 * Positions are [x, z] in world units around the surgical table (which sits at origin).
 * Scale: 1 unit ≈ ~0.5 m.  Room is roughly 10×10 units.
 */
export const HEART_MACHINES = [
  { name: 'Patient Monitor',               pos: [-4.2,  0.0 ], color: '#00aaff', icon: '' },
  { name: 'Ventilator',                    pos: [-4.2,  1.8 ], color: '#00ddff', icon: '' },
  { name: 'Anesthesia Machine',            pos: [-4.2,  3.4 ], color: '#44bbcc', icon: '' },
  { name: 'Cardiopulmonary Bypass Machine',pos: [ 4.2,  1.0 ], color: '#ff6644', icon: ''  },
  { name: 'Perfusion Pump',                pos: [ 4.2, -0.8 ], color: '#ff8866', icon: '' },
  { name: 'Defibrillator',                 pos: [ 4.2,  2.8 ], color: '#ffdd00', icon: '' },
  { name: 'Electrocautery Unit',           pos: [ 1.8,  4.2 ], color: '#ff9900', icon: '' },
  { name: 'Suction Device',                pos: [-1.8,  4.2 ], color: '#aabbcc', icon: '' },
  { name: 'Warming Blanket',               pos: [-3.2, -3.0 ], color: '#ff6688', icon: ''  },
  { name: 'Surgical Lights',               pos: [ 0.0, -0.3 ], color: '#fffde0', icon: '' },
  { name: 'Instrument Table',              pos: [ 3.0,  4.2 ], color: '#889999', icon: '' },
  { name: 'Blood Warmer',                  pos: [-3.2, -1.2 ], color: '#cc4444', icon: '' },
  { name: 'Cell Saver',                    pos: [ 4.2, -2.6 ], color: '#44cc88', icon: '' },
  { name: 'Transesophageal Echo Unit',     pos: [-4.2, -2.6 ], color: '#66aaff', icon: '' },
  { name: 'Intra-Aortic Balloon Pump',     pos: [ 0.0,  4.2 ], color: '#ff4466', icon: '' },
]

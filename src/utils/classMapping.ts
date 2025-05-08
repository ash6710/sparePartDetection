// Class mappings loaded from the improved_class_indices.pkl file
export const classMapping: Record<number, string> = {
  0: 'Gen Set 15 KVA (TMTL) Blower Assy',
  1: 'Gen Set 15 KVA (TMTL) Crankshaft',
  2: 'Gen Set 15 KVA (TMTL) Fuel Pump assy',
  3: 'Gen Set 15 KVA(TMTL) Piston & Gudgon Pin',
  4: 'Gen Set 15 Kva &35 KVA(TMTL) Air Filter',
  5: 'Gen Set 15 Kva &35 KVA(TMTL) Alternator Assy 12 V',
  6: 'Gen Set 15 Kva &35 KVA(TMTL) Connecting Rod',
  7: 'Gen Set 15 Kva &35 KVA(TMTL) Cyl Head',
  8: 'Gen Set 15 Kva &35 KVA(TMTL) Fuel Hose',
  9: 'Gen Set 15 Kva &35 KVA(TMTL) Fuel filter',
  10: 'Gen Set 15 Kva &35 KVA(TMTL) Injector',
  11: 'Gen Set 15 Kva &35 KVA(TMTL) Inlet & Exhaust Valve',
  12: 'Gen Set 15 Kva &35 KVA(TMTL) Oil Preasssure Gauge',
  13: 'Gen Set 15 Kva &35 KVA(TMTL) Oil Pump',
  14: 'Gen Set 15 Kva &35 KVA(TMTL) Push Rod',
  15: 'Gen Set 15 Kva &35 KVA(TMTL) Sleeves',
  16: 'Gen Set 15 Kva ,35 KVA & 63 KVA (TMTL) Flywheel Ring',
  17: 'Gen Set 15 Kva ,35 KVA & 63 KVA (TMTL) Over Flow Pipe',
  18: 'Gen Set 15 Kva ,35 KVA & 63 KVA (TMTL) Push Rod Tube',
  19: 'Gen Set 15 Kva ,35 KVA & 63 KVA (TMTL) Push Rod seal',
  20: 'Gen Set 15 Kva ,35 KVA & 63 KVA (TMTL) Ring Set',
  21: 'Gen Set 15 Kva ,35 KVA & 63 KVA (TMTL) Stopper Solonide',
  22: 'Gen Set 35 KVA (TMTL) Oil Filter',
  23: 'Gen Set 35 KVA(TMTL) Piston',
  24: 'Gen set 15 KVA,35 KVA&63 KVA (KOEL) Valve Guide'
};

export const getClassName = (classIndex: number): string => {
  return classMapping[classIndex] || `Unknown Part ${classIndex}`;
}; 
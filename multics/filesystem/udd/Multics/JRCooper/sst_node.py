
from multics.globals import *

NODE = PL1.Structure (

    rank            = fixed.bin . init (0),
    SX              = fixed.bin . init (0),
    SY              = fixed.bin . init (0),
    PX              = fixed.bin . init (0),
    PY              = fixed.bin . init (0),
    time_left       = fixed.dec (5, 2) . init (0),
    
    beacon          = PL1.Structure(
        SX          = fixed.bin . init (0),
        SY          = fixed.bin . init (0),
        PX          = fixed.bin . init (0),
        PY          = fixed.bin . init (0),
        landed      = bit (1) . init (b'0')
    ),
        
    supplyN         = fixed.bin . init (0),
    supply          = Dim(6) (PL1.Structure(
        SX          = fixed.bin,
        SY          = fixed.bin,
        PX          = fixed.bin,
        PY          = fixed.bin,
        uses_left   = fixed.bin
    )),
        
    arachnidT       = fixed.bin . init (0),
    skinnyT         = fixed.bin . init (0),
    heavy_beamT     = fixed.bin . init (0),
    
)

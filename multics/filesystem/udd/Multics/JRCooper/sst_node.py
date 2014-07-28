
from multics.globals import *

NODE = PL1.Structure (

    rank            = fixed.bin . init (0),
    SX              = fixed.bin . init (0),
    SY              = fixed.bin . init (0),
    PX              = fixed.bin . init (0),
    PY              = fixed.bin . init (0),
    suit_pts        = fixed.bin . init (50),
    body_pts        = fixed.bin . init (20),
    jet_energy      = fixed.bin . init (1000),
    flamer_energy   = fixed.bin . init (1000),
    HE_bombN        = fixed.bin . init (0),
    nuke_bombN      = fixed.bin . init (4),
    time_left       = fixed.dec (5, 2) . init (0),
    encamped        = bit (1) . init (b'0'),
    sitting_in_rad  = bit (1) . init (b'0'),
    was_in_rad      = bit (1) . init (b'0'),
    
    beacon          = PL1.Structure(
        SX          = fixed.bin . init (0),
        SY          = fixed.bin . init (0),
        PX          = fixed.bin . init (0),
        PY          = fixed.bin . init (0),
        landed      = bit (1) . init (b'0'),
    ),
        
    supplyN         = fixed.bin . init (0),
    supply          = Dim(6) (PL1.Structure(
        SX          = fixed.bin,
        SY          = fixed.bin,
        PX          = fixed.bin,
        PY          = fixed.bin,
        uses_left   = fixed.bin,
    )),
    
    equipment       = PL1.Structure(
        snooper     = PL1.Structure(
            working = bit (1) . init (b'1'),
            repair_time = fixed.dec (5, 2) . init (0)),
        scanner     = PL1.Structure(
            working = bit (1) . init (b'1'),
            repair_time = fixed.dec (5, 2) . init (0)),
        jet_boosters = PL1.Structure(
            working = bit (1) . init (b'1'),
            repair_time = fixed.dec (5, 2) . init (0)),
        flamer      = PL1.Structure(
            working = bit (1) . init (b'1'),
            repair_time = fixed.dec (5, 2) . init (0)),
        HE_launcher = PL1.Structure(
            working = bit (1) . init (b'1'),
            repair_time = fixed.dec (5, 2) . init (0)),
        nuke_launcher = PL1.Structure(
            working = bit (1) . init (b'1'),
            repair_time = fixed.dec (5, 2) . init (0)),
        listening_dev = PL1.Structure(
            working = bit (1) . init (b'1'),
            repair_time = fixed.dec (5, 2) . init (0)),
    ),
        
    arachnidT       = fixed.bin . init (0),
    Arachnid        = Dim(60) (PL1.Structure(
        SX          = fixed.bin,
        SY          = fixed.bin,
        PX          = fixed.bin,
        PY          = fixed.bin,
        life_pts    = fixed.bin,
    )),
    
    skinnyT         = fixed.bin . init (0),
    Skinny          = Dim(30) (PL1.Structure(
        SX          = fixed.bin,
        SY          = fixed.bin,
        PX          = fixed.bin,
        PY          = fixed.bin,
        life_pts    = fixed.bin,
    )),
    
    heavy_beamT     = fixed.bin . init (0),
    Heavy_beam      = Dim(6) (PL1.Structure(
        SX          = fixed.bin,
        SY          = fixed.bin,
        PX          = fixed.bin,
        PY          = fixed.bin,
        life_pts    = fixed.bin,
    )),
    
    missile_lT      = fixed.bin . init (0),
    Missile_l       = Dim(6) (PL1.Structure(
        SX          = fixed.bin,
        SY          = fixed.bin,
        PX          = fixed.bin,
        PY          = fixed.bin,
        life_pts    = fixed.bin,
    )),
    
    breachN         = fixed.bin . init (0),
    breach          = Dim(25) (PL1.Structure(
        SX          = fixed.bin,
        SY          = fixed.bin,
        PX          = fixed.bin,
        PY          = fixed.bin,
        engineer    = fixed.bin,
        prisoners   = fixed.bin,
    )),
    
    fortN           = fixed.bin . init (0),
    fort            = Dim(60) (PL1.Structure(
        SX          = fixed.bin,
        SY          = fixed.bin,
        PX          = fixed.bin,
        PY          = fixed.bin,
        guard       = fixed.bin,
        prisoner_X  = fixed.bin . init (0),
        prixoner_Y  = fixed.bin . init (0),
    )),
    
    sector          = Dim(5, 5) (PL1.Structure(
        arachnidN   = fixed.bin,
        skinnyN     = fixed.bin,
        radiation   = char (1),
        supply      = char (1),
        point       = Dim(10, 10) (char (1)),
    )),
    
    chart           = Dim(5, 5) (PL1.Structure(
        arachnidN   = char (1),
        skinnyN     = char (1),
        radiation   = char (1),
        supply      = char (1),
    )),
    
    score           = PL1.Structure(
        total               = fixed.bin . init (0),
        arachnids_Xed       = fixed.bin . init (0),
        skinnies_Xed        = fixed.bin . init (0),
        heavy_beams_Xed     = fixed.bin . init (0),
        missile_ls_Xed      = fixed.bin . init (0),
        mountains_Xed       = fixed.bin . init (0),
        supplies_Xed        = fixed.bin . init (0),
        prisoners_rescued   = fixed.bin . init (0),
        death_penalty       = fixed.bin . init (0),
        captured_penalty    = fixed.bin . init (0),
        success_ratio       = fixed.bin . init (-1),
        rank_bonus          = fixed.bin . init (0),
        skinny_prisoners    = fixed.bin . init (0),
    ),
    
    nuke_bonus_score = fixed.bin . init (5000),
    
    distress        = PL1.Structure(
        SX          = fixed.bin . init (0),
        SY          = fixed.bin . init (0),
        notified    = bit (1) . init (b'0'),
        which_supply = fixed.bin . init (0),
    ),
)

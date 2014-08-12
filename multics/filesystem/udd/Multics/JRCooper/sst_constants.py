
from multics.globals import *

declare (

    MAIN                   = char (20) . init ("starship_troopers"),
    RANK                   = Dim(3+1) (char (10)) . init (["", "Leutenant", "Sergeant", "Captain"]),
    
    LEUTENANT              = fixed.bin . init (1),
    SERGEANT               = fixed.bin . init (2),
    CAPTAIN                = fixed.bin . init (3),

    ARACHNID               = char (1) . init ("A"),
    SKINNY                 = char (1) . init ("S"),
    HEAVY_BEAM             = char (1) . init ("H"),
    MISSILE_L              = char (1) . init ("M"),
    MOUNTAIN               = char (1) . init ("^"),
    RADIATION              = char (1) . init ("#"),
    SUPPLY_SHIP            = char (1) . init ("+"),
    BEACON                 = char (1) . init ("!"),
    BREACH                 = char (1) . init ("*"),
    FORT                   = char (1) . init ("@"),
    TROOPER                = char (1) . init ("T"),

    LOCUS                  = fixed.bin . init (1),
    SUIT                   = fixed.bin . init (2),
    BODY                   = fixed.bin . init (3),
    BOOSTER_ENERGY         = fixed.bin . init (4),
    FLAMER_ENERGY          = fixed.bin . init (5),
    HE_BOMBN               = fixed.bin . init (6),
    NUKE_BOMBN             = fixed.bin . init (7),
    BUGS_LEFT              = fixed.bin . init (8),
    TIME_LEFT              = fixed.bin . init (9),
    SCANNER                = fixed.bin . init (10),
    SNOOPER                = fixed.bin . init (11),
    FLAMER_RIFLE           = fixed.bin . init (12),
    HE_LAUNCHER            = fixed.bin . init (13),
    NUKE_LAUNCHER          = fixed.bin . init (14),
    LISTENING_DEV          = fixed.bin . init (15),
    JET_BOOSTERS           = fixed.bin . init (16),
    ARACHNID_SCORE         = fixed.bin . init (17),
    SKINNY_SCORE           = fixed.bin . init (18),
    HEAVY_BEAM_SCORE       = fixed.bin . init (19),
    MISSILE_L_SCORE        = fixed.bin . init (20),
    MOUNTAIN_SCORE         = fixed.bin . init (21),
    SUPPLY_SCORE           = fixed.bin . init (22),
    PRISONER_SCORE         = fixed.bin . init (23),

    ARACHNID_SCORE_FACTOR  = fixed.bin . init (100),
    SKINNY_SCORE_FACTOR    = fixed.bin . init (10),
    HEAVY_BEAM_SCORE_FACTOR = fixed.bin . init (500),
    MISSILE_L_SCORE_FACTOR = fixed.bin . init (300),
    MOUNTAIN_SCORE_FACTOR  = fixed.bin . init (-50),
    SUPPLY_SCORE_FACTOR    = fixed.bin . init (-250),
    PRISONER_SCORE_FACTOR  = fixed.bin . init (1000),

)

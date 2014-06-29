
from multics.pl1types import *

sl_info_version_1 = 1
        
sl_info_p = ptr

sl_info = PL1.Structure.based(sl_info_p) (
    version      = sl_info_version_1,
    num_paths    = fixed.binary,
    paths        = Dim(Dynamic.num_paths) (PL1.Structure(
        type     = fixed.binary,
        code     = fixed.binary(35),
        pathname = char(168),
    )),
)

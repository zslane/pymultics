
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

# class sl_info(PL1.Structure):
    # def __init__(self):
        # PL1.Structure.__init__(self,
            # version      = sl_info_version_1,
            # num_paths    = fixed.binary,
            # paths        = Dim(Dynamic.num_paths) (PL1.Structure(
                # type     = fixed.binary,
                # code     = fixed.binary(35),
                # pathname = char(168),
            # )),
        # )

# class sl_info_path(PL1.Structure):
    # def __init__(self):
        # PL1.Structure.__init__(self,
            # type     = fixed.binary,
            # code     = fixed.binary(35),
            # pathname = char(168),
        # )
        
# class sl_info_structure(PL1.Structure):
    # def __init__(self):
        # PL1.Structure.__init__(self,
            # version      = sl_info_version_1,
            # paths        = Dim('*') (sl_info_path),
        # )

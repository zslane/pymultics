
from multics.pl1types import PL1

process_env_version_1 = 1

class process_env_structure(PL1.Structure):
    def __init__(self):
        PL1.Structure.__init__(self,
            version       = process_env_version_1,
            process_id    = 0,
            process_dir   = "",
            pit           = None,
            pds           = None,
            rnt           = None,
            mbx           = None,
            msg           = None,
            core_function = None,
        )

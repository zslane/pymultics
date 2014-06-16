
from multics.pl1types import PL1

rnt_version_1 = 1

class rnt_structure(PL1.Structure):
    def __init__(self):
        PL1.Structure.__init__(self,
            rnt_version  = rnt_version_1,
            reference_names = None,
            search_rules = None,
            working_dir  = "",
        )

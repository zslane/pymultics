
from multics.pl1types import PL1

pds_version_1 = 1

class pds_structure(PL1.Structure):
    def __init__(self):
        PL1.Structure.__init__(self,
            version       = pds_version_1,
            process_stack = None,
        )

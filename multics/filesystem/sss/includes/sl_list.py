
from multics.pl1types import *

sl_list_version_1 = 1

class sl_list_link(PL1.Structure):
    def __init__(self):
        PL1.Structure.__init__(self,
            names = Dim('*') (char (32)),
        )

class sl_list_structure(PL1.Structure):
    def __init__(self):
        PL1.Structure.__init__(self,
            version   = sl_list_version_1,
            link      = Dim('*') (sl_list_link),
        )

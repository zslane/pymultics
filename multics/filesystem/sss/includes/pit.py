
from multics.globals import *

class pit_structure(PL1.Structure):
    def __init__(self):
        PL1.Structure.__init__(self,
            login_name = "",
            project    = "",
            home_dir   = "",
            login_time = None,
            process_id = 0,
        )
    
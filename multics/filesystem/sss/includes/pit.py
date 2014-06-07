
from multics.globals import *

class pit_structure(PL1.Structure):
    def __init__(self):
        PL1.Structure.__init__(self,
            login_name   = "",
            project      = "",
            process_type = 1, # 1 = interactive, 2 = absentee, 3 = daemon
            homedir      = "",
            time_login   = None,
            process_id   = 0,
        )
    
    @property
    def user_id(self):
        return self.login_name + "." + self.project
        
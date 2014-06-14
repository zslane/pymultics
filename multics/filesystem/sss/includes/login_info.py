
from multics.pl1types import PL1

login_info_version_1 = 1

class login_info_structure(PL1.Structure):
    def __init__(self):
        PL1.Structure.__init__(self,
            version      = login_info_version_1,
            person_id    = "",
            project_id   = "",
            process_type = 0, # 1 = interactive, 2 = absentee, 3 = daemon
            process_id   = 0,
            homedir      = "",
            time_login   = None,
            cp_path      = "",
            no_start_up  = False,
        )
    
    @property
    def user_id(self):
        return self.person_id + "." + self.project_id

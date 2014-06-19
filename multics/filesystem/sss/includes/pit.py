
from multics.pl1types import PL1, parameter

pit_version_1 = 1

pit_process_type_interactive = 1
pit_process_type_absentee = 2
pit_process_type_daemon = 3

class pit_structure(PL1.Structure):
    def __init__(self):
        PL1.Structure.__init__(self,
            pit_version  = pit_version_1,
            login_name   = "",
            project      = "",
            process_type = pit_process_type_interactive,
            homedir      = "",
            no_start_up  = False,
            time_login   = None,
            process_id   = 0,
        )
    
    @property
    def user_id(self):
        return self.login_name + "." + self.project
        
    @property
    def instance_tag(self):
        return ["", "a", "m", "z"][self.process_type]
        
pit_ptr = parameter()

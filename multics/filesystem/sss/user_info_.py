
from multics.globals import *

class user_info_(SystemExecutable):
    def __init__(self, system_services):
        super(user_info_, self).__init__(self.__class__.__name__, system_services)
        self.__pit = parm()
        
    def _load_pit(self):
        declare (get_pdir_ = entry . returns (char ('*')),
                 code      = parm)
                 
        if not self.__pit.data:
            call.hcs_.initiate(get_pdir_(), "pit", self.__pit, code)
            if code.val != 0:
                raise SegmentFault(get_pdir_() + ">pit")
            
    def procedure(self, person, project, acct):
        self.whoami(person, project, acct)
        
    def whoami(self, person, project, acct):
        self._load_pit()
        person.id = self.__pit.data.login_name
        project.id = self.__pit.data.project
        
    def homedir(self, homedir):
        self._load_pit()
        homedir.name = self.__pit.data.homedir

    def login_data(self, person, project, acct, time_login):
        self._load_pit()
        person.id = self.__pit.data.login_name
        project.id = self.__pit.data.project
        time_login.val = self.__pit.data.time_login
        
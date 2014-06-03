
from multics.globals import *

class user_info_(SystemExecutable):
    def __init__(self, system_services):
        super(user_info_, self).__init__(self.__class__.__name__, system_services)
        
    def whoami(self, person, project):
        person.id, project.id = self.system.session_thread.session.user_id.split(".")
        
    def homedir(self, homedir):
        homedir.name = self.system.session_thread.session.homedir



from multics.globals import *

class cp_(SystemExecutable):
    def __init__(self, system_services):
        super(cp_, self).__init__(self.__class__.__name__, system_services)
        
    def execute(self, command_line, code):
        code.val = self.system.session_thread.session.process.command_processor._parse_and_execute(command_line)
        
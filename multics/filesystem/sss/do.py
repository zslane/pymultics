
from multics.globals import *
    
class do(Executable):
    def __init__(self):
        super(do, self).__init__(self.__class__.__name__)
        
    def procedure(self, cmd_string, *args, **kwargs):
        declare (code = parm)
        cmd_line = cmd_string.format(*args, **kwargs)
        call.cp_.execute(cmd_line, code)

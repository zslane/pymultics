
from multics.globals import *
    
class do(Executable):
    def __init__(self):
        super(do, self).__init__(self.__class__.__name__)
        
    def procedure(self, cmd_string, *args, **kwargs):
        code = parm()
        cmd_line = cmd_string.format(*args, **kwargs)
        call.cu_.cp(cmd_line, code)

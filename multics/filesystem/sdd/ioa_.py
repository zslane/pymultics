
from multics.globals import *

class ioa_(SystemExecutable):
    def __init__(self, system_services):
        super(ioa_, self).__init__(self.__class__.__name__, system_services)
        
    def procedure(self, format_string="", *args, **kwargs):
        if isinstance(format_string, PL1.EnumValue):
            s = repr(format_string)
        else:
            s = format_string.format(*args, **kwargs)
        # end if
        self.system.hardware.io.put_output(s + "\n")
        
    def nnl(self, format_string="", *args, **kwargs):
        s = format_string.format(*args, **kwargs)
        self.system.hardware.io.put_output(s)


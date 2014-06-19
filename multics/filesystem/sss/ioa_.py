
from multics.globals import *

class ioa_(SystemExecutable):
    def __init__(self, system_services):
        super(ioa_, self).__init__(self.__class__.__name__, system_services)
        
    def procedure(self, format_string="", *args, **kwargs):
        print self._format(format_string, *args, **kwargs)
        self.system.llout(self._format(format_string, *args, **kwargs) + "\n")
        
    def nnl(self, format_string="", *args, **kwargs):
        self.system.llout(self._format(format_string, *args, **kwargs))
    
    def rs(self, format_string, return_string, *args, **kwargs):
        return_string.val = self._format(format_string, *args, **kwargs) + "\n"
        
    def rsnnl(self, format_string, return_string, *args, **kwargs):
        return_string.val = self._format(format_string, *args, **kwargs)
    
    def _format(self, format_string, *args, **kwargs):
        if isinstance(format_string, PL1.EnumValue):
            s = repr(format_string)
        else:
            s = format_string.format(*args, **kwargs)
        # end if
        return s
        
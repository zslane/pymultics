
from multics.globals import *

class command_query_(SystemExecutable):
    def __init__(self, system_services):
        super(command_query_, self).__init__(self.__class__.__name__, system_services)
        
    def __call__(self):
        input = self._get_input(block=True)
        self.system.llout(input + "\n")
        return input
        
    def noecho(self):
        return self._get_input(block=True)
    
    def _get_input(self, block=False):
        return self.system.llin(block)
        

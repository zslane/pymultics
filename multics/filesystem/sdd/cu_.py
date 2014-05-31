
from multics.globals import *

class cu_(SystemExecutable):
    def __init__(self, system_services):
        super(cu_, self).__init__(self.__class__.__name__, system_services)
        
        self.__program_name = ""
        self.__argument_string = []
        
    def arg_count(self):
        return len(self.arg_list())
        
    def arg_list(self):
        return self.__argument_string.split()
        
    def arg_string(self, starting_with=0):
        s = self.__argument_string
        d = []
        for i in range(starting_with):
            discard, _, s = s.strip().partition(" ")
            d.append(discard)
        # end for
        if d:
            return (d, s.strip())
        else:
            return s.strip()
        
    def _set_command_line(self, program_name, argument_string):
        self.__program_name = program_name
        self.__argument_string = argument_string.strip()

